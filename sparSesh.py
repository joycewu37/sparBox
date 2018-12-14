# Joyce Wu
# ID: joycewu
# Section: A
# sparSesh.py creates a runtime object for the kinect sparring gameplay mode

from pykinect2 import PyKinectV2, PyKinectRuntime
from pykinect2.PyKinectV2 import *

import ctypes
import _ctypes
import pygame
import sys
import math
import random

class SparSeshRuntime(object):
    def __init__(self,isOrthodox,numRounds=12,roundLength=180,restLength=60):
        pygame.init()

        self.screenWidth = 1920
        self.screenHeight = 1080

        self.orthodox = isOrthodox

        #### Head Position from Previous Frame ####
        self.prevUserHeadX = 0
        self.prevUserHeadY = 0
        self.prevUserHeadZ = 0

        #### Head Position from Current Frame ####
        self.currUserHeadX = 0
        self.currUserHeadY = 0
        self.currUserHeadZ = 0

        #### Hand Positions from Previous Frame ####
        # track previous right hand position (x,y,z) as separate variables
        # Note: user is mirrored on screen
        self.prevRightHandX = 0 # user's right hand horizontal position
        self.prevRightHandY = 0 # user's right hand height
        self.prevRightHandZ = 0 # user's right hand distance from sensor

        # track previous left hand position (x,y,z)
        self.prevLeftHandX = 0
        self.prevLeftHandY = 0
        self.prevLeftHandZ = 0

        # current right hand position
        self.currRightHandX = 0
        self.currRightHandY = 0
        self.currRightHandZ = 0

        # current left hand position
        self.currLeftHandX = 0
        self.currLeftHandY = 0
        self.currLeftHandZ = 0

        # is the user currently throwing a punch?
        self.isRightPunching = False
        self.isLeftPunching = False

        self.rightPunchStartX = 0
        self.rightPunchStartY = 0
        self.rightPunchStartZ = 0

        self.rightPunchEndX = 0
        self.rightPunchEndY = 0
        self.rightPunchEndZ = 0

        self.leftPunchStartX = 0
        self.leftPunchStartY = 0
        self.leftPunchStartZ = 0

        self.leftPunchEndX = 0
        self.leftPunchEndY = 0
        self.leftPunchEndZ = 0
        
        # once punch is thrown, calculate curr position - prev. postition
        self.rightPunchDX = 0 # hooks travel mostly horizontally
        self.rightPunchDY = 0 # uppercuts travel vertically
        self.rightPunchDZ = 0 # straight punches travel towards sensor

        self.leftPunchDX = 0
        self.leftPunchDY = 0
        self.leftPunchDZ = 0

        self.landedPunchCount = 0
        self.glance = 0
        self.totalPunches = 0
        self.userAccuracy = 0
        self.prevUserPunches = [] # user's previous 10 punches for patterns

        self.botMaxShift = 50
        self.botShiftX = 0 # entire bot moves around on screen
        self.botShiftY = 0
        self.botCenterX = self.screenWidth//2+self.botShiftX
        self.botCenterY = self.screenHeight//3+self.botShiftY

        self.botHeadWidth = 160
        self.botHeadHeight = 200
        self.botHeadX = self.botCenterX-self.botHeadWidth//2
        self.botHeadY = self.botCenterY-self.botHeadHeight//2

        self.botHeadMoveX = 0
        self.botHeadMoveY = 0
        self.botIsPunching = False

        self.botLanded = 0
        self.botGlance = 0
        self.botTotal = 0
        self.botAccuracy = 0
        self.botPunchChoice = [0]
        self.prevBotPunches = [] # avoids generating predictable punch combos
        self.botSlowDown = 0

        self.userHealth = 100
        self.botHealth = 100

        self.roundLength = roundLength # 3-minute rounds
        self.roundTimeLeft = self.roundLength 

        self.restLength = restLength # 1-minute rests
        self.restTimeLeft = self.restLength
        self.currRound = 1
        self.numRounds = numRounds
        self.roundOngoing = False
        self.restOngoing = False

        self.preGameBuffer = 3
        self.postGameBuffer = 5
        self.gameStartTime = None
        self.gameTimeLeft = self.preGameBuffer+self.postGameBuffer \
                + self.numRounds*(self.roundTimeLeft+self.restTimeLeft)
        self.gameOver = False # game ends when time runs out

        # visual effects from google images
        self.blackBlur = pygame.image.load('blackBlur.gif')
        self.blood = pygame.image.load('blood.gif')

        self.lastPunchNameTime = 0
        self.lastPunchName = ""

        self.lastStarTime = 0
        self.starXCoord = 0
        self.starYCoord = 0

        # play background music
        pygame.mixer.init()
        pygame.mixer.music.load('purple.ogg')
        pygame.mixer.music.play(-1)

        # load sound effects
        self.bellSound = pygame.mixer.Sound('SparBox3sWarning.ogg')
        self.warningSound = pygame.mixer.Sound('SparBox10sWarning.ogg')
        self.punchSound = pygame.mixer.Sound('punchSound.ogg')
        self.threeSecWarningPlayed = False
        self.tenSecWarningPlayed = False

        # Used to manage how fast the screen updates
        self.clock = pygame.time.Clock()

        # Set the width and height of the window [width/2, height/2]
        self.screen = pygame.display.set_mode((960,540),\
                 pygame.HWSURFACE|pygame.DOUBLEBUF, 32)

        # Loop until the user clicks the close button.
        self.done = False

        # Kinect runtime object, we want color and body frames 
        self.kinect = \
        PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | \
            PyKinectV2.FrameSourceTypes_Body)

        # back buffer surface for getting Kinect color frames, 32bit color, 
        # width and height equal to the Kinect color frame size
        self.frameSurface = pygame.Surface((self.kinect.color_frame_desc.Width,\
                             self.kinect.color_frame_desc.Height), 0, 32)

        # here we will store skeleton data 
        self.bodies = None

    def displayPunchName(self):
    # when punch is detected, type of punch is displayed
        punchFont = pygame.font.Font(None, 100)
        punchText = punchFont.render(self.lastPunchName,
                            1, (52, 152, 219))
        self.frameSurface.blit(punchText,
            (self.screenWidth//2,2*self.screenHeight//3))

    def drawTimerBar(self):
    # bar length indicates how much time left
        margin = 75
        maxBar = self.screenWidth - 2*margin
        barHeight = 40
        roundLength = self.roundLength
        barLength = int((self.roundTimeLeft/roundLength) * maxBar)
        pygame.draw.rect(self.frameSurface,
                    (170, 218, 255),[margin,self.screenHeight-margin-barHeight,
                    barLength,barHeight])

    def drawHealthBars(self):
    # indicates user's and bot's health based on punches taken
        margin = 50
        barLength = self.screenWidth//2-2*margin
        
        userBarX = margin
        botBarX = self.screenWidth-margin

        barY = 100
        barThick = 20

        greenUser = int(self.userHealth/100 * barLength)

        if 20 <= greenUser <= barLength-20:
            diagOffsetUser = 20
        else:
            diagOffsetUser = 0

        greenUserPoints = [(userBarX, barY-barThick), # top left
                            (userBarX, barY+barThick), # bottom left
        (userBarX+greenUser-diagOffsetUser, barY+barThick), # bottom right
        (userBarX+greenUser+diagOffsetUser, barY-barThick) # top right        
        ]
        redUserPoints = [(userBarX+greenUser+diagOffsetUser, barY-barThick),
                        (userBarX+greenUser-diagOffsetUser, barY+barThick),
                        (userBarX+barLength,barY+barThick),
                        (userBarX+barLength,barY-barThick)
        ]

        # user health bar
        pygame.draw.polygon(self.frameSurface,
                            (46, 204, 113),
                            greenUserPoints)
        pygame.draw.polygon(self.frameSurface,
                            (231, 76, 60),
                            redUserPoints)
        


        greenBot = int(self.botHealth/100 * barLength)

        if 20 <= greenBot <= barLength-20:
            diagOffsetBot = 20
        else:
            diagOffsetBot = 0

        greenBotPoints = [(botBarX, barY-barThick), # top right
                            (botBarX, barY+barThick), # bottom right
        (botBarX-greenBot+diagOffsetBot, barY+barThick), # bottom left   
        (botBarX-greenBot-diagOffsetBot, barY-barThick) # top left
        ]
        redBotPoints = [
                (botBarX-greenBot+diagOffsetBot, barY+barThick), # bottom right   
                (botBarX-greenBot-diagOffsetBot, barY-barThick), # top right
                (botBarX-barLength, barY-barThick),# top left
                (botBarX-barLength, barY+barThick)# bottom left
        ]

        # bot health bar
        pygame.draw.polygon(self.frameSurface,
                            (46, 204, 113),
                            greenBotPoints)
        pygame.draw.polygon(self.frameSurface,
                            (231, 76, 60),
                            redBotPoints) 

        healthFont = pygame.font.Font(None, 36)
        userLabel = healthFont.render("USER", 1, (52, 152, 219))
        self.frameSurface.blit(userLabel, (margin,50))
        botLabel = healthFont.render("SPARBOT", 1, (231, 76, 60))
        self.frameSurface.blit(botLabel, (self.screenWidth-margin-120,50))

    def getUserAccuracy(self):
    # user's landed punches / total punches (partial credit for glancing shots)
        if self.totalPunches == 0:
            self.userAccuracy = 0 # can't div. by 0
        else:
            self.userAccuracy = (self.landedPunchCount+int(1/3*(self.glance))) \
                                    /self.totalPunches

    def getBotAccuracy(self):
    # bot's landed punches / total punches (partial credit for glancing shots)
        if self.botTotal == 0:
            self.botAccuracy = 0 # can't div. by 0
        else:
            self.botAccuracy = (self.botLanded+int(1/3*(self.botGlance))) \
                                    /self.botTotal

    def updateHealths(self):
    # updates health bar status
        self.userHealth = 100 - self.botLanded//10
        self.botHealth = 100 - self.landedPunchCount//3

    def displayWarning(self):
        # start doing warnings after 15 user strikes
        roundTimeFont = pygame.font.Font(None, 100)
        if self.totalPunches >= 15:
            if self.userAccuracy < 0.2:
            # warning for low user accuracy
                userMessage = roundTimeFont.render("punch accurately!",
                                       1, (231, 76, 60))
                self.frameSurface.blit(userMessage,
                    (self.screenWidth//5,self.screenHeight//2))

        # warnings after 15 landed bot strikes
        if self.botLanded >= 15:
            if self.botAccuracy > 0.6:
            # warning for bot high accuracy
                botMessage = roundTimeFont.render("move more!",
                                       1, (231, 76, 60))
                self.frameSurface.blit(botMessage,
                    (3*self.screenWidth//5+100,self.screenHeight//2))

    def drawBloodAndBlur(self):
    # visual fx when user is hit too many times
        if self.botLanded > 10:
            self.frameSurface.blit(self.blackBlur,
                (self.screenWidth//2-400,self.screenHeight//2-550))
        if self.botLanded > 15:
            self.frameSurface.blit(self.blood,
                (self.screenWidth//2-400,self.screenHeight//2-550))

    #### Checking Punch Type: Compare dX, dY, dZ ####

    # so DX DY DZ measure in meters
    # convert position of hand to pixels for collisions
    def isRightHook(self):
        # returns True if right punch is mostly horizontal movement
        screenRightDX = self.rightPunchDX*self.screenWidth
        hookThreshold = 28.6
        if (not self.isRightPunching and screenRightDX != 0):    
            if screenRightDX > 0:
            # right hooks move right to left (negative DX)
                print("wrong way for right hook!")
                return False           

            elif abs(screenRightDX) < self.screenWidth//hookThreshold:
                print(screenRightDX*self.rightPunchStartZ,"z*x")
                print("move more for right hook!")
                return False # small movements don't count

            elif (abs(self.rightPunchDX) < abs(self.rightPunchDY)) or \
                (abs(self.rightPunchDX) < abs(self.rightPunchDZ)):
                print("not enough DX for right hook")
                return False # not a predominantly horizontal punch
            self.lastPunchNameTime = pygame.time.get_ticks()
            self.lastPunchName = "right hook"
            print("right hook!")
            didItCollide = self.collision()
            if didItCollide == "glance":
               # counts as a punch, but did it land?
                self.glance += 1
            elif didItCollide == "hit":
                self.landedPunchCount += 1
                self.lastStarTime = pygame.time.get_ticks()
                self.starXCoord = self.botHeadX+self.botHeadWidth
                self.starYCoord = self.botHeadY
                # points based on bot head location
                
            self.totalPunches += 1   
            return True

    def isLeftHook(self):
        # returns True if left punch is mostly horizontal movement
        screenLeftDX = self.leftPunchDX*self.screenWidth
        hookThreshold = 28.6

        if (not self.isLeftPunching and self.leftPunchDX != 0):
            if self.leftPunchDX < 0:
                print("wrong way for left hook!")
                return False

            elif abs(screenLeftDX) < self.screenWidth//hookThreshold:
                print("too small for left hook!")
                return False # small movements don't count

            elif (abs(self.leftPunchDX) < abs(self.leftPunchDY)) or \
                (abs(self.leftPunchDX) < abs(self.leftPunchDZ)):
                return False # not a predominantly horizontal punch
            self.lastPunchNameTime = pygame.time.get_ticks()
            self.lastPunchName = "left hook"
            print("left hook!")
            didItCollide = self.collision()
            if didItCollide == "glance":
               # counts as a punch, but did it land?
                self.glance += 1
            elif didItCollide == "hit":
                self.landedPunchCount += 1
                self.lastStarTime = pygame.time.get_ticks()
                self.starXCoord = self.botHeadX
                self.starYCoord = self.botHeadY
            self.totalPunches += 1 
            return True

    def isRightUppercut(self):
    # returns True if right punch is mostly vertical movement
        
        screenRightDY = self.rightPunchDY*self.screenHeight
        uppercutThresh = 38.6

        if not self.isRightPunching and self.rightPunchDY != 0:
            if self.rightPunchDY < 0: # downwards doesn't count
                return False
            
            elif abs(screenRightDY) < self.screenHeight//uppercutThresh:
                print("your R upper is too small")
                return False # small movements don't count

            elif (abs(self.rightPunchDY) < abs(self.rightPunchDX)) or \
                (abs(self.rightPunchDY) < abs(self.rightPunchDZ)):
                print("your R upper DY is too small")
                return False # not a predominantly vertical punch
            self.lastPunchNameTime = pygame.time.get_ticks()
            self.lastPunchName = "right uppercut"
            print("right uppercut!")

            didItCollide = self.collision()
            if didItCollide == "glance":
               # counts as a punch, but did it land?
                self.glance += 1
            elif didItCollide == "hit":
                self.landedPunchCount += 1
                self.lastStarTime = pygame.time.get_ticks()
                self.starXCoord = self.botHeadX+self.botHeadWidth
                self.starYCoord = self.botHeadY+self.botHeadHeight
            self.totalPunches += 1 
            return True  

    def isLeftUppercut(self):
    # returns True if left punch is mostly vertical movement

        screenLeftDY = self.leftPunchDY*self.screenHeight
        uppercutThresh = 38.6

        if not self.isLeftPunching and self.leftPunchDY != 0:
            if self.leftPunchDY < 0: # downwards doesn't count
                return False
        
            elif abs(screenLeftDY) < self.screenHeight//uppercutThresh:
                print("your L uppercut is too small")
                return False # small movements don't count
            elif (abs(self.leftPunchDY) < abs(self.leftPunchDX)) or \
                (abs(self.leftPunchDY) < abs(self.leftPunchDZ)):
                print("your L upper dY is too small")
                return False # not a predominantly vertical punch
            self.lastPunchNameTime = pygame.time.get_ticks()
            self.lastPunchName = "left uppercut"
            print("left uppercut!")

            didItCollide = self.collision()
            if didItCollide == "glance":
               # counts as a punch, but did it land?
                self.glance += 1
            elif didItCollide == "hit":
                self.landedPunchCount += 1
                self.lastStarTime = pygame.time.get_ticks()
                self.starXCoord = self.botHeadX
                self.starYCoord = self.botHeadY+self.botHeadHeight
            self.totalPunches += 1 
            return True 

    def isJab(self):
    # returns True if non-dominant hand has mostly depth movement
        depthThresh = 0.005

        if self.orthodox and not self.isLeftPunching:
            if self.leftPunchDZ > 0:
                return False # pulling fist backwards doesn't count   
            elif abs(self.leftPunchDZ) < depthThresh:
                print(self.leftPunchDZ,"left jab depth")
                return False
            elif (abs(self.leftPunchDZ) < abs(self.leftPunchDX)) or \
                (abs(self.leftPunchDZ) < abs(self.leftPunchDY)):
                print("not really a left jab")
                return False # not a predominantly DZ punch
            self.lastPunchNameTime = pygame.time.get_ticks()
            self.lastPunchName = "left jab"
            print("left jab!")
            didItCollide = self.collision()
            if didItCollide == "glance":
               # counts as a punch, but did it land?
                self.glance += 1
            elif didItCollide == "hit":
                self.landedPunchCount += 1
                self.lastStarTime = pygame.time.get_ticks()
                self.starXCoord = self.botHeadX+self.botHeadWidth//3
                self.starYCoord = self.botHeadY+self.botHeadHeight//2
            self.totalPunches += 1 
            return True

        elif not self.orthodox and not self.isRightPunching:
            if self.rightPunchDZ > 0:
                return False # pulling fist backwards doesn't count
            elif self.rightPunchDZ < depthThresh:
                print(self.rightPunchDZ, "not enough right jab depth")
                return False
            elif (abs(self.rightPunchDZ) < abs(selfrightPunchDX)) or \
                (abs(self.rightPunchDZ) < abs(self.rightPunchDY)):
                print("not really a right jab")
                return False # not a predominantly DZ punch
            self.lastPunchNameTime = pygame.time.get_ticks()
            self.lastPunchName = "right jab"
            print("right jab!")
            didItCollide = self.collision()
            if didItCollide == "glance":
               # counts as a punch, but did it land?
                self.glance += 1
            elif didItCollide == "hit":
                self.landedPunchCount += 1
                self.lastStarTime = pygame.time.get_ticks()
                self.starXCoord = self.botHeadX+2*self.botHeadWidth//3
                self.starYCoord = self.botHeadY+self.botHeadHeight//2
            self.totalPunches += 1 
            return True

    def isCross(self):
    # returns True if dominant hand has mostly dZ movement
        depthThresh = 0.3

        if self.orthodox and not self.isRightPunching:
            if self.rightPunchDZ > 0:
                return False # pulling fist backwards doesn't count
                # small movements don't count
            elif abs(self.rightPunchDZ) < depthThresh:
                print(self.rightPunchDZ,"not enough right cross depth")
                return False
            elif (abs(self.rightPunchDZ) < abs(self.rightPunchDX)) or \
                (abs(self.rightPunchDZ) < abs(self.rightPunchDY)):
                print("not really a right cross")
                return False # not a predominantly DZ punch
            self.lastPunchNameTime = pygame.time.get_ticks()
            self.lastPunchName = "right cross"
            print("right cross!")
            didItCollide = self.collision()
            if didItCollide == "glance":
               # counts as a punch, but did it land?
                self.glance += 1
            elif didItCollide == "hit":
                self.lastStarTime = pygame.time.get_ticks()
                self.starXCoord = self.botHeadX+2*self.botHeadWidth//3
                self.starYCoord = self.botHeadY+self.botHeadHeight//2
                self.landedPunchCount += 1
            self.totalPunches += 1 
            return True

        elif not self.orthodox and not self.isLeftPunching:
            if self.rightPunchDZ < 0:
                return False # pulling fist backwards doesn't count
                # small movements don't count
            elif abs(self.leftPunchDZ) < depthThresh:
                print(self.leftPunchDZ,"not enough left cross depth")
                return False
            elif (abs(self.leftPunchDZ) < abs(self.leftPunchDX)) or \
                (abs(self.leftPunchDZ) < abs(self.leftPunchDY)):
                print("not really a left cross")
                return False # not a predominantly DZ punch
            self.lastPunchNameTime = pygame.time.get_ticks()
            self.lastPunchName = "left cross"
            print("left cross!")

            didItCollide = self.collision()
            if didItCollide == "glance":
               # counts as a punch, but did it land?
                self.glance += 1
            elif didItCollide == "hit":
                self.lastStarTime = pygame.time.get_ticks()
                self.starXCoord = self.botHeadX+self.botHeadWidth//3
                self.starYCoord = self.botHeadY+self.botHeadHeight//2
                self.landedPunchCount += 1
            self.totalPunches += 1 
            return True

    def distance(x0,y0,x1,y1):
    # calculates distance between two given (x,y) points
        return math.sqrt((x0-x1)**2+(y0-y1)**2)

    def collision(self):
    #### checks for collision between user hand and bot head ####
        if self.isRightPunching:
            screenRightEndX = self.rightPunchEndX*self.screenWidth+ \
                self.screenWidth//2
            screenRightEndY = self.screenHeight//2-\
                (self.rightPunchEndY*self.screenHeight)

            dist = SparSeshRuntime.distance(screenRightEndX,\
                screenRightEndY,
                        self.botHeadX,self.botHeadY)

            # connected punches: user center of hand reaches virtual face
            if dist < 20*self.botHeadHeight:
                print("hit!")
                pygame.mixer.Sound.play(self.punchSound)
                return "hit"
            # glancing punches: part of user hand reaches virtual face
            elif 20*self.botHeadHeight < dist < 28*self.botHeadHeight:
                print("glance")
                return ("glance")

        elif self.isLeftPunching:

            screenLeftEndX = self.leftPunchEndX*self.screenWidth+ \
                self.screenWidth//2
            screenLeftEndY = self.screenHeight//2- \
                (self.leftPunchEndY*self.screenHeight)

            dist = SparSeshRuntime.distance(screenLeftEndX,\
                screenLeftEndY,
                        self.botHeadX,self.botHeadY)

            # connected punches: user center of hand reaches virtual face
            if dist < 20*self.botHeadHeight:
                pygame.mixer.Sound.play(self.punchSound)
                print("hit!")
                return "hit"
            # glancing punches: part of user hand reaches virtual face
            elif 20*self.botHeadHeight < dist < 28*self.botHeadHeight:
                print("glance")
                return "hit"

        # miss: none of user hand reaches virtual face
        # do not increase landed or glance counts

    def botCollision(self,handPoints):
        #### checks for collision between bot hand and user head ####
        handCX = handPoints[0]+handPoints[2]//2
        handCY = handPoints[1]+handPoints[3]//2

        screenHeadX = self.currUserHeadX*self.screenWidth+self.screenWidth//2
        screenHeadY = self.screenHeight//2-\
            (self.currUserHeadY*self.screenHeight)
        if self.botIsPunching: 
            dist = SparSeshRuntime.distance(screenHeadX,\
                        screenHeadY,
                        handCX,handCY)           

            # connected punches: bot center of hand reaches user face
            if dist < 300: # threshhold for hitting user face
                if self.botSlowDown%25==0:
                    self.botLanded += 1
                    self.botTotal += 1
                    pygame.mixer.Sound.play(self.punchSound)
                    print("bot hit!")

            # glancing punches: part of user hand reaches virtual face
            elif 300 < dist < 700:
                if self.botSlowDown%25==0:
                    self.botGlance += 1
                    self.botTotal += 1
                    print("bot glance")           

    def getPunchChoices(self):
    # generates new punches for Bot using pseudo AI
        if self.botSlowDown % 25 != 0: return []
        #### single punches ####
        if self.landedPunchCount >= 75:
            punchChoice = random.randint(2,6) # no more jabs (weak punches)
        elif self.landedPunchCount >= 50:
            punchChoice = random.randint(1,6) # bot no longer hesitates
        elif self.landedPunchCount >= 10:
            while True: # don't generate too many of same punch
                punchChoice = random.randint(0,6)
                if self.prevBotPunches.count(punchChoice) <= 3:
                    break
        else: # pseudo AI: start with any punch (basic level)
            punchChoice = random.randint(0,6) # punches are enumerated

        if self.landedPunchCount >= 100:
        # pseudo AI: bot may mirror user's movement 50/50 chance (confuses user)
            if len(self.prevUserPunches) > 0:
                mirrorPunch = self.prevUserPunches[-1]
                mirrorChoice = random.choice([mirrorPunch,punchChoice])
                punchChoice = mirrorChoice

        #### combos of punches ####
        # what is the longest string of punches Bot can choose
        if self.landedPunchCount >= 40:
            maxComboLength = 5 # any longer, too unrealistic
        elif self.landedPunchCount >= 30:
            maxComboLength = 4
        elif self.landedPunchCount >= 20:
            maxComboLength = 3
        elif self.landedPunchCount >= 10:
            maxComboLength = 2
        else:
            maxComboLength = 1  

        # pseudo AI: length of combo depends on user success
        possibCombos = []
        twoPunchComboList =    [[1,1],
                                [1,2],
                                [1,3],
                                [1,4],
                                [1,5],
                                [1,6],
                                [2,1],
                                [6,3],
                                [4,1],
                                [6,2],
                                [2,2]]

        threePunchComboList =  [[1,1,2],
                                [1,2,1],
                                [1,3,2],
                                [1,2,3],
                                [2,0,2],
                                [1,1,1],
                                [2,1,2],
                                [2,3,2],
                                [1,0,1]]

        fourPunchComboList =   [[1,2,1,2],
                                [1,2,3,2],
                                [1,6,3,2],
                                [6,5,2,1],
                                [4,6,3,2],
                                [1,1,2,3],
                                [6,6,2,1],
                                [1,0,1,2]]

        fivePunchComboList =   [[4,3,2,1,2],
                                [2,1,1,6,1],
                                [1,1,2,3,2],
                                [1,2,1,2,3],
                                [2,0,2,1,2],
                                [1,2,3,4,1]]

        if maxComboLength >= 1:
            possibCombos += [[punchChoice]] # add in the selected single punch 
        if maxComboLength >= 2:
            possibCombos = twoPunchComboList
        if maxComboLength >= 3:
            possibCombos += threePunchComboList
        if maxComboLength >= 4:
            possibCombos += fourPunchComboList
        if maxComboLength >= 5:
            possibCombos += fivePunchComboList

        comboChoice = random.choice(possibCombos)
        return comboChoice

    def moveVirtualBoxer(self):
        #### pseudo AI: Bot moves more as user improves ####
        if self.landedPunchCount > 110:
            self.botMaxShift += 1 # will increase with each frame
        elif self.landedPunchCount >= 100:
            self.botMaxShift = 100
        elif self.landedPunchCount >= 90:
            self.botMaxShift = 95
        elif self.landedPunchCount >= 80:
            self.botMaxShift = 90
        elif self.landedPunchCount >= 70:
            self.botMaxShift = 85        
        elif self.landedPunchCount >= 60:
            self.botMaxShift = 80
        elif self.landedPunchCount >= 50:
            self.botMaxShift = 75
        elif self.landedPunchCount >= 40:
            self.botMaxShift = 70
        elif self.landedPunchCount >= 30:
            self.botMaxShift = 65
        elif self.landedPunchCount >= 20:
            self.botMaxShift = 60
        elif self.landedPunchCount >= 10:
            self.botMaxShift = 55

        if self.isRightPunching:
        # user is punching, bot must avoid
        # doesn't guarantee successful dodge (realistic)
            if self.isJab() or self.isCross() or self.isRightUppercut():
                self.botShiftX -= 100 # shift left
            elif self.isRightHook():
                self.botShiftY += 100
            self.botCenterX += self.botShiftX
            self.botCenterY += self.botShiftY
            # is it running off the screen?

        elif self.isLeftPunching:
            if self.isJab() or self.isCross() or self.isLeftUppercut():
                self.botShiftX += 100 # shift right
            elif self.isLeftHook():
                self.botShiftY += 100
            self.botCenterX += self.botShiftX
            self.botCenterY += self.botShiftY

        else: # Bot moving around regularly
            #### Bot Body Movement ####
            if (self.botShiftX, self.botShiftY) == (0,0):
                self.botShiftX = random.randint(-self.botMaxShift,
                    self.botMaxShift)
                self.botShiftY = random.randint(-self.botMaxShift,
                    self.botMaxShift)

                self.botCenterX += self.botShiftX
                self.botCenterY += self.botShiftY

            else:
                self.botShiftX, self.botShiftY = 0,0 # don't migrate off screen
                self.botCenterX = self.screenWidth//2+self.botShiftX # reset
                self.botCenterY = self.screenHeight//3+self.botShiftY 

            self.botIsPunching = not (self.isLeftPunching or \
                self.isRightPunching)
            self.botPunchChoice = [0] # start with Bot hesitation
            if self.botIsPunching:
                if len(self.botPunchChoice) == 1 and self.botSlowDown%25==0:
                    self.botPunchChoice += self.getPunchChoices()
                self.prevBotPunches += self.botPunchChoice
                
                while len(self.prevBotPunches) > 10:
                    self.prevBotPunches.pop(0)
                # delete one old punch
                if len(self.botPunchChoice) > 1:
                    self.botPunchChoice.pop(0)

        #### Bot Head Movement ####
        if self.botHeadX == self.botCenterX-80 and \
            self.botHeadY == self.botCenterY-100:
            # head is in neutral position
            self.botHeadMoveX = random.randint(-15,15)
            self.botHeadMoveY = random.randint(-15,15)
            # moving head diagonally
            self.botHeadX += self.botHeadMoveX
            self.botHeadY += self.botHeadMoveY

        else: # neutral position head
            self.botHeadX = self.botCenterX-80
            self.botHeadY = self.botCenterY-100            

    def drawVirtualBoxer(self):
        width = self.screenWidth
        height = self.screenHeight

        # head
        pygame.draw.ellipse(self.frameSurface, 
                           (231, 76, 60), 
                           [self.botHeadX, self.botHeadY,
                        160, 200])

        # neck
        neckPoints = [(self.botCenterX-28,self.botCenterY+80),
                    (self.botCenterX+28,self.botCenterY+80),
                    (self.botCenterX+32,self.botCenterY+160),
                    (self.botCenterX-32,self.botCenterY+160)]

        pygame.draw.polygon(self.frameSurface,
                        (192, 57, 43),
                    neckPoints)

        #torso
        torsoPoints = [(self.botCenterX-140,self.botCenterY+160),
                        (self.botCenterX+140,self.botCenterY+160),
                        (self.botCenterX+120,int(height)),
                        (self.botCenterX-120,int(height))]

        pygame.draw.polygon(self.frameSurface,
                        (231, 76, 60),
                    torsoPoints)

        # unpacking the punch enumeration
        if self.botPunchChoice[0] == 0:
            punchChoice = None # no punch (bot hesitation)
        elif self.botPunchChoice[0] == 1:
            punchChoice = "Jab"
        elif self.botPunchChoice[0] == 2:
            punchChoice = "Cross"
        elif self.botPunchChoice[0] == 3:
            punchChoice = "Left Hook"
        elif self.botPunchChoice[0] == 4:
            punchChoice = "Right Hook"
        elif self.botPunchChoice[0] == 5:
            punchChoice = "Left Uppercut"
        elif self.botPunchChoice[0] == 6:
            punchChoice = "Right Uppercut"

        #right arm
        if punchChoice == "Cross":
            rightBicepPoints = [(self.botCenterX-140,self.botCenterY+160),
                            (self.botCenterX-100,self.botCenterY+200),
                            (self.botCenterX-160,self.botCenterY+300),
                            (self.botCenterX-200,self.botCenterY+280)]

            rightForearmPoints = [(self.botCenterX-160,self.botCenterY+295),
                            
                            (self.botCenterX-167,self.botCenterY+340),
                            (self.botCenterX-196,self.botCenterY+336),
                            (self.botCenterX-200,self.botCenterY+280)
                            ]

            rightHandPoints = (self.botCenterX-212,self.botCenterY+330,
                        60,60)

        elif punchChoice == "Right Hook":
            rightBicepPoints = [(self.botCenterX-140,self.botCenterY+160),
                            (self.botCenterX-100,self.botCenterY+200),
                            (self.botCenterX-160,self.botCenterY+300),
                            (self.botCenterX-200,self.botCenterY+280)]

            rightForearmPoints = [(self.botCenterX-160,self.botCenterY+310),
                            (self.botCenterX-190,self.botCenterY+275),
                            (self.botCenterX-60,self.botCenterY+280),
                            (self.botCenterX-50,self.botCenterY+310)
                            ]

            rightHandPoints = (self.botCenterX-76,self.botCenterY+262,60,60)

        elif punchChoice == "Right Uppercut":
            rightBicepPoints = [(self.botCenterX-140,self.botCenterY+160),
                            (self.botCenterX-100,self.botCenterY+200),
                            (self.botCenterX-160,self.botCenterY+300),
                            (self.botCenterX-200,self.botCenterY+280)]

            rightForearmPoints = [(self.botCenterX-155,self.botCenterY+305),
                            (self.botCenterX-205,self.botCenterY+280),
                            (self.botCenterX-195,self.botCenterY+165),
                            (self.botCenterX-165,self.botCenterY+165)
                            ]

            rightHandPoints = (self.botCenterX-210,self.botCenterY+130,
                        60,60)
        else: # neutral position
            rightBicepPoints = [(self.botCenterX-140,self.botCenterY+160),
                            (self.botCenterX-100,self.botCenterY+200),
                            (self.botCenterX-160,self.botCenterY+300),
                            (self.botCenterX-200,self.botCenterY+280)]

            rightForearmPoints = [(self.botCenterX-160,self.botCenterY+300),
                            (self.botCenterX-200,self.botCenterY+280),
                            (self.botCenterX-80,self.botCenterY+200),
                            (self.botCenterX-40,self.botCenterY+260)
                            ]

            # Rect = (x,y,width,height) and (x,y) represents top left corner
            rightHandPoints = (self.botCenterX-93,self.botCenterY+200,60,60)

        pygame.draw.polygon(self.frameSurface,
                            (192, 57, 43),
                        rightBicepPoints)

        pygame.draw.polygon(self.frameSurface,
                        (192, 57, 43),
                        rightForearmPoints)

        pygame.draw.ellipse(self.frameSurface, 
                           (39, 174, 96),
                           rightHandPoints)

        self.botCollision(rightHandPoints)

        #left arm
        if punchChoice == "Jab":
            leftBicepPoints = [(self.botCenterX+140,self.botCenterY+160),
                            (self.botCenterX+100,self.botCenterY+200),
                            (self.botCenterX+160,self.botCenterY+300),
                            (self.botCenterX+200,self.botCenterY+280)]

            leftForearmPoints = [(self.botCenterX+160,self.botCenterY+295),
                            (self.botCenterX+200,self.botCenterY+280),
                            
                            (self.botCenterX+196,self.botCenterY+336),
                            (self.botCenterX+167,self.botCenterY+340)
                            ]

            leftHandPoints = (self.botCenterX+155,self.botCenterY+330,
                        60,60)
        elif punchChoice == "Left Hook":
            leftBicepPoints = [(self.botCenterX+140,self.botCenterY+160),
                            (self.botCenterX+100,self.botCenterY+200),
                            (self.botCenterX+160,self.botCenterY+300),
                            (self.botCenterX+200,self.botCenterY+280)]

            leftForearmPoints = [(self.botCenterX+160,self.botCenterY+310),
                            (self.botCenterX+190,self.botCenterY+275),
                            (self.botCenterX+60,self.botCenterY+280),
                            (self.botCenterX+50,self.botCenterY+310)
                            ]

            leftHandPoints = (self.botCenterX+45,self.botCenterY+255,60,60)
        elif punchChoice == "Left Uppercut":
            leftBicepPoints = [(self.botCenterX+140,self.botCenterY+160),
                            (self.botCenterX+100,self.botCenterY+200),
                            (self.botCenterX+160,self.botCenterY+300),
                            (self.botCenterX+200,self.botCenterY+280)]

            leftForearmPoints = [(self.botCenterX+155,self.botCenterY+305),
                            (self.botCenterX+205,self.botCenterY+280),
                            (self.botCenterX+195,self.botCenterY+165),
                            (self.botCenterX+165,self.botCenterY+165)
                            ]

            leftHandPoints = (self.botCenterX+155,self.botCenterY+117,
                        60,60)
        else: # neutral position
            leftBicepPoints = [(self.botCenterX+140,self.botCenterY+160),
                                (self.botCenterX+100,self.botCenterY+200),
                                (self.botCenterX+160,self.botCenterY+300),
                                (self.botCenterX+200,self.botCenterY+280)]

            leftForearmPoints = [(self.botCenterX+160,self.botCenterY+300),
                                (self.botCenterX+200,self.botCenterY+280),
                                (self.botCenterX+100,self.botCenterY+200),
                                (self.botCenterX+60,self.botCenterY+240)
                                ]

            leftHandPoints = [self.botCenterX+60,self.botCenterY+200,
                            60,60]

        self.botCollision(leftHandPoints)

        pygame.draw.polygon(self.frameSurface,
                        (192, 57, 43),
                        leftBicepPoints)

        pygame.draw.polygon(self.frameSurface,
                        (192, 57, 43),
                        leftForearmPoints)

        pygame.draw.ellipse(self.frameSurface, 
                        (39, 174, 96), 
                        leftHandPoints)

        #legs are off-screen

    def drawStar(self, diameter=100):
        numPoints = 12
        isOutRad = True
        outRad = diameter/2
        inRad = (5/8)*outRad
        pointList = []
        for num in range(numPoints*2): #points drawn is 2x number of star points
            angle = (2*math.pi*(num))/(numPoints*2) + math.pi/2
            if isOutRad: radius = outRad
            else: radius = inRad
            xCord = self.starXCoord + radius*math.cos(angle)
            yCord = self.starYCoord - radius*math.sin(angle)
            isOutRad = not isOutRad 
            pointList.append(((int(xCord),int(yCord))))
        
        pygame.draw.polygon(self.frameSurface,
                        (241, 196, 15),pointList)

    def drawColorFrame(self, frame, targetSurface):
        targetSurface.lock()
        address = self.kinect.surface_as_array(targetSurface.get_buffer())
        # cleanly replacing old frame with new one
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        targetSurface.unlock()

    def run(self):
        # -------- Main Program Loop -----------
        while not self.done:
            # --- Main event loop
            if self.gameOver:
                break
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    self.done = True # Flag that we are done so exit this loop

            # section (4 lines) from github.com/fletcher-marsh
            # have a color frame. Fill out back buffer surface with frame's data 
            if self.kinect.has_new_color_frame(): #is the kinect working
                frame = self.kinect.get_last_color_frame()
                self.drawColorFrame(frame, self.frameSurface)
                frame = None #saving memory, be clean

            if self.roundOngoing:
                # section (7 lines) from github.com/fletcher-marsh
                # We have a body frame, so can get skeletons
                if self.kinect.has_new_body_frame(): # check IR camera
                    self.bodies = self.kinect.get_last_body_frame()

                    if self.bodies is not None: 
                        for i in range(0, self.kinect.max_body_count):
                            body = self.bodies.bodies[i] #extract body object
                            if not body.is_tracked: # do we know where body is
                                continue 
                        
                            joints = body.joints # access data from IR camera
                            handRight = PyKinectV2.JointType_HandRight
                            handLeft = PyKinectV2.JointType_HandLeft
                            #access joints at the joint type
                            if joints[handRight].TrackingState != \
                                PyKinectV2.TrackingState_NotTracked:

                                # update current right hand positions
                                self.currRightHandX = \
                            joints[PyKinectV2.JointType_HandRight].Position.x
                                self.currRightHandY = \
                            joints[PyKinectV2.JointType_HandRight].Position.y
                                self.currRightHandZ = \
                            joints[PyKinectV2.JointType_HandRight].Position.z

                                # punch starts when right hand closes
                                self.isRightHandClosed = \
                            (PyKinectV2.HandState_Closed==body.hand_right_state)
                                #print(self.isRightHandClosed)

                                if self.isRightHandClosed and \
                                    self.rightPunchStartX == 0:

                                    self.isRightPunching = True
                                    self.rightPunchStartX = self.currRightHandX
                                    self.rightPunchStartY = self.currRightHandY
                                    self.rightPunchStartZ = self.currRightHandZ

                                elif not self.isRightHandClosed and \
                                    self.rightPunchStartX != 0:
                                    #not currently punching

                                    self.isRightPunching = False
                                    
                                    # save positions at end of punch
                                    if self.rightPunchStartX != 0 and \
                                        self.rightPunchEndX == 0:

                                        self.rightPunchEndX = \
                                            self.currRightHandX
                                        # calculate length at end of punch
                                        self.rightPunchDX = \
                                            (self.rightPunchEndX - \
                                                self.rightPunchStartX)
                                    
                                    if self.rightPunchStartY != 0 and \
                                        self.rightPunchEndY == 0:

                                        self.rightPunchEndY = \
                                            self.currRightHandY
                                        self.rightPunchDY = \
                                            (self.rightPunchEndY - \
                                                self.rightPunchStartY)
                                    
                                    if self.rightPunchStartZ != 0 and \
                                        self.rightPunchEndZ == 0:

                                        self.rightPunchEndZ = \
                                            self.currRightHandZ
                                        self.rightPunchDZ = \
                                            (self.rightPunchEndZ - \
                                                self.rightPunchStartZ)

                                    # reset punch start and end values
                                    self.rightPunchStartX = 0
                                    self.rightPunchStartY = 0
                                    self.rightPunchStartZ = 0
                                    self.rightPunchEndX = 0
                                    self.rightPunchEndY = 0
                                    self.rightPunchEndZ = 0

                                    if SparSeshRuntime.isRightHook(self):
                                        if self.orthodox:
                                            self.prevUserPunches.append(4)
                                        else:
                                            self.prevUserPunches.append(3)
                       
                                    elif SparSeshRuntime.isRightUppercut(self):
                                        if self.orthodox:
                                            self.prevUserPunches.append(6)
                                        else:
                                            self.prevUserPunches.append(5)
                          
                                    elif SparSeshRuntime.isJab(self):
                                        self.prevUserPunches.append(1)
                                    # right jabs only for southpaw boxers

                                    elif SparSeshRuntime.isCross(self):
                                        self.prevUserPunches.append(2)
                                    # right crosses only for orthodox boxers

                                # reset delta's after calculating punch
                                self.rightPunchDX = 0
                                self.rightPunchDY = 0
                                self.rightPunchDZ = 0
                                
                            if joints[handLeft].TrackingState != \
                                PyKinectV2.TrackingState_NotTracked:
                                # update current left hand positions
                                self.currLeftHandX = \
                                joints[PyKinectV2.JointType_HandLeft].Position.x
                                self.currLeftHandY = \
                                joints[PyKinectV2.JointType_HandLeft].Position.y
                                self.currLeftHandZ = \
                                joints[PyKinectV2.JointType_HandLeft].Position.z

                                self.isLeftHandClosed = \
                                (PyKinectV2.HandState_Closed == \
                                    body.hand_left_state)

                                if self.isLeftHandClosed and \
                                    self.leftPunchStartX == 0:

                                    self.isLeftPunching = True
                                    self.leftPunchStartX = self.currLeftHandX
                                    self.leftPunchStartY = self.currLeftHandY
                                    self.leftPunchStartZ = self.currLeftHandZ

                                elif not self.isLeftHandClosed and \
                                    self.leftPunchStartX != 0: #not punching

                                    self.isLeftPunching = False

                                    # save positions at end of punch
                                    if self.leftPunchStartX != 0 and \
                                        self.leftPunchEndX == 0:

                                        self.leftPunchEndX = self.currLeftHandX
                                        # calculate length when punch ends
                                        self.leftPunchDX = \
                                            (self.leftPunchEndX - \
                                                self.leftPunchStartX)
                                    
                                    if self.leftPunchStartY != 0 and \
                                        self.leftPunchEndY == 0:

                                        self.leftPunchEndY = self.currLeftHandY
                                        self.leftPunchDY = \
                                            (self.leftPunchEndY - \
                                                self.leftPunchStartY)
                                    
                                    if self.leftPunchStartZ != 0 and \
                                        self.leftPunchEndZ == 0:

                                        self.leftPunchEndZ = self.currLeftHandZ
                                        self.leftPunchDZ = \
                                            (self.leftPunchEndZ - \
                                                self.leftPunchStartZ)

                                    # reset start and end values
                                    self.leftPunchStartX = 0
                                    self.leftPunchStartY = 0
                                    self.leftPunchStartZ = 0
                                    self.leftPunchEndX = 0
                                    self.leftPunchEndY = 0
                                    self.leftPunchEndZ = 0

                                    if SparSeshRuntime.isLeftHook(self):
                                        #self.totalPunches += 1
                                        if self.orthodox:
                                            self.prevUserPunches.append(3)
                                        else:
                                            self.prevUserPunches.append(4)
                       
                                    elif SparSeshRuntime.isLeftUppercut(self):
                                        #self.totalPunches += 1
                                        if self.orthodox:
                                            self.prevUserPunches.append(5)
                                        else:
                                            self.prevUserPunches.append(6)
                          
                                    elif SparSeshRuntime.isJab(self):
                                    # left jabs only for orthodox boxers
                                        self.prevUserPunches.append(1)
                                    
                                    elif SparSeshRuntime.isCross(self):
                                    # left crosses only for southpaw boxers 
                                        self.prevUserPunches.append(2)

                                # reset delta's after calculating punch
                                self.leftPunchDX = 0
                                self.leftPunchDY = 0
                                self.leftPunchDZ = 0 

                            while len(self.prevUserPunches) > 10:
                                self.prevUserPunches.pop(0)

                            if joints[PyKinectV2.JointType_Head].TrackingState \
                                 != PyKinectV2.TrackingState_NotTracked:
                                self.currUserHeadX = \
                                joints[PyKinectV2.JointType_Head].Position.x
                                self.currUserHeadY = \
                                joints[PyKinectV2.JointType_Head].Position.y
                                self.currUserHeadZ = \
                                joints[PyKinectV2.JointType_Head].Position.z                        

                            if math.isnan(self.rightPunchDX):
                                self.rightPunchDX = 0
                            if math.isnan(self.rightPunchDY):
                                self.rightPunchDY = 0
                            if math.isnan(self.rightPunchDZ):
                                self.rightPunchDZ = 0
                            if math.isnan(self.leftPunchDX):
                                self.leftPunchDX = 0
                            if math.isnan(self.leftPunchDY):
                                self.leftPunchDY = 0
                            if math.isnan(self.leftPunchDZ):
                                self.leftPunchDZ = 0

                            # cycle previous and current positions for next time
                            self.prevRightHandX = self.currRightHandX
                            self.prevRightHandY = self.currRightHandY
                            self.prevRightHandZ = self.currRightHandZ

                            self.prevLeftHandX = self.currLeftHandX
                            self.prevLeftHandY = self.currLeftHandY
                            self.prevLeftHandZ = self.currLeftHandZ

                            self.prevUserHeadX = self.currUserHeadX
                            self.prevUserHeadY = self.currUserHeadY
                            self.prevUserHeadZ = self.currUserHeadZ
                            
                # --- Game logic 
                # Draw graphics
                self.moveVirtualBoxer()

                # update user's and bot's accuracy so far
                self.getUserAccuracy()
                self.getBotAccuracy()
                self.botSlowDown += 1

                # update user's and bot's health
                self.updateHealths()
                
                # display warning messages
                self.displayWarning()

            # draw bot before round starts
            self.drawVirtualBoxer()

            # draw visual fx on top of bot
            self.drawBloodAndBlur()

            # draw bars
            self.drawHealthBars()
            self.drawTimerBar()       

            # text displaying round time left
            pygame.draw.rect(self.frameSurface,(189, 195, 199),
                [75,self.screenHeight-425,500,300])
            roundTimeFont = pygame.font.Font(None, 80)
            if self.roundTimeLeft%60 != 0:
                if self.roundTimeLeft%60 >= 10:
                    roundText = roundTimeFont.render("Round Time: "+ \
                        str(self.roundTimeLeft//60)+":"+ \
                        "%d"%(self.roundTimeLeft%60),
                               1, (192, 57, 43))
                else:
                    roundText = roundTimeFont.render("Round Time: "+ \
                        str(self.roundTimeLeft//60)+":"+"0"+ \
                        "%d"%(self.roundTimeLeft%60),
                               1, (192, 57, 43))
            else:
                roundText = roundTimeFont.render("Round Time: "+ \
                    str(self.roundTimeLeft//60)+":"+"00",
                               1, (192, 57, 43))

            self.frameSurface.blit(roundText, (100,self.screenHeight-400))

            currRoundFont = pygame.font.Font(None, 80)
            currRoundText = currRoundFont.render("Round "+ \
                str(self.currRound),1, (0, 110, 27))
            self.frameSurface.blit(currRoundText, (100,self.screenHeight-200))

            # text displaying rest time left
            restTimeFont = pygame.font.Font(None, 80)
            if self.restTimeLeft%60 != 0:
                if self.restTimeLeft%60 >= 10:
                    restText = restTimeFont.render("Rest Time: "+ \
                        str(self.restTimeLeft//60)+":"+ \
                        "%d"%(self.restTimeLeft%60),
                               1, (39, 174, 96))
                else:
                    restText = restTimeFont.render("Rest Time: "+ \
                        str(self.restTimeLeft//60)+":"+"0"+ \
                        "%d"%(self.restTimeLeft%60),
                               1, (39, 174, 96))
            else:
                restText = restTimeFont.render("Rest Time: "+ \
                    str(self.restTimeLeft//60)+":"+"00",
                               1, (39, 174, 96))

            self.frameSurface.blit(restText, (100,self.screenHeight-300))

            if self.roundTimeLeft == 10:
                tenSecWarning = roundTimeFont.render("10 seconds!",
                                    1, (170, 218, 255))
                self.frameSurface.blit(tenSecWarning, (self.screenWidth//2,200))

            # section (6 lines) from github.com/fletcher-marsh
            # --- copy back buffer surface pixels to the screen,
            # resize it if needed and keep aspect ratio
            # --- (screen size may be different from Kinect's color frame size) 
            hToW = float(self.frameSurface.get_height()) / \
                self.frameSurface.get_width()
            targetHeight = int(hToW * self.screen.get_width())
            surfaceToDraw = pygame.transform.scale(self.frameSurface, 
                (self.screen.get_width(), targetHeight));
            self.screen.blit(surfaceToDraw, (0,0))
            surfaceToDraw = None
            pygame.display.update()

            # play start bell
            if self.gameTimeLeft == self.preGameBuffer + self.postGameBuffer + \
                self.numRounds*(self.roundTimeLeft+self.restTimeLeft) and \
                    self.threeSecWarningPlayed == False:
                pygame.mixer.Sound.play(self.bellSound)
                self.threeSecWarningPlayed = True

            if self.gameTimeLeft == self.postGameBuffer + \
                self.numRounds*(self.roundTimeLeft+self.restTimeLeft):

                self.roundOngoing = True

            # draw pow star
            currTime = pygame.time.get_ticks()
            if abs(currTime-self.lastStarTime) <= 60:
                self.drawStar()
            if abs(currTime-self.lastPunchNameTime) <= 60:
                self.displayPunchName()

            # --- 60 frames per second
            self.clock.tick(60)
            if self.gameStartTime == None:
                self.gameStartTime = pygame.time.get_ticks()
            self.gameTimeLeft = (self.preGameBuffer+self.postGameBuffer \
             + self.numRounds*(self.roundLength+self.restLength))\
              - (pygame.time.get_ticks()-self.gameStartTime)//1000

            modGameTime = ((self.gameTimeLeft-self.postGameBuffer-1) \
                % (self.roundLength+self.restLength))
            
            if self.roundOngoing:
                self.roundTimeLeft = modGameTime - self.restLength
                self.tenSecWarningPlayed = False
                self.threeSecWarningPlayed = False
            if self.restOngoing:
                self.restTimeLeft = modGameTime
                self.tenSecWarningPlayed = False
                self.threeSecWarningPlayed = False

            # time's up for the round and game
            if self.roundTimeLeft == 10 and not self.tenSecWarningPlayed:
                pygame.mixer.Sound.play(self.warningSound)
                self.tenSecWarningPlayed = True
            elif self.roundTimeLeft == 3 and not self.threeSecWarningPlayed:
                # three second warning that the round will end
                pygame.mixer.Sound.play(self.bellSound)
                self.threeSecWarningPlayed = True

            if self.restTimeLeft == 10 and not self.tenSecWarningPlayed:
                pygame.mixer.Sound.play(self.warningSound)
                self.tenSecWarningPlayed = True

            elif self.restTimeLeft == 3 and not self.threeSecWarningPlayed:
                # three second warning that the round will end
                pygame.mixer.Sound.play(self.bellSound)
                self.threeSecWarningPlayed = True

            if self.roundOngoing and self.roundTimeLeft == 0:
                self.roundOngoing = False
                self.tenSecWarningPlayed = False
                self.threeSecWarningPlayed = False
                self.restOngoing = True
                self.restTimeLeft = self.restLength
                
            if self.restOngoing and self.restTimeLeft == 0 and \
                self.currRound<self.numRounds:

                self.restOngoing = False
                self.tenSecWarningPlayed = False
                self.threeSecWarningPlayed = False
                self.roundOngoing = True
                self.roundTimeLeft = self.roundLength
                             
            if modGameTime == 0:
                self.currRound = self.numRounds-self.gameTimeLeft // \
                    (self.roundLength+self.restLength)+1
            if self.gameTimeLeft == 0:
                self.gameOver = True

        # Close Kinect sensor, close the window and quit.
        self.kinect.close()
        pygame.quit()