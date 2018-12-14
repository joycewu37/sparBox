# Joyce Wu
# ID: joycewu
# Section: A
# bagSesh.py creates a runtime object for the kinect punching bag gameplay mode

from pykinect2 import PyKinectV2, PyKinectRuntime
from pykinect2.PyKinectV2 import *

import ctypes
import _ctypes
import pygame
import sys
import math
import random

class BagSeshRuntime(object):
    def __init__(self,isOrthodox,numRounds=12,roundLength=180,restLength=60):
        pygame.init()

        self.screenWidth = 1920
        self.screenHeight = 1080

        self.orthodox = isOrthodox

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

        # specific types of punches
        self.numJabs = 0
        self.numCrosses = 0
        self.numLeftHooks = 0
        self.numRightHooks = 0
        self.numLeftUppercuts = 0
        self.numRightUppercuts = 0

        self.landedPunchCount = 0
        self.glance = 0
        self.totalPunches = 0
        self.userAccuracy = 0

        # bag does not move
        self.bagWidth = 300
        self.bagHeight = 4*self.screenHeight/5

        self.bagLeft = self.screenWidth//2-self.bagWidth//2
        self.bagTop = self.screenHeight-self.bagHeight
        self.bagRight = self.screenWidth//2+self.bagWidth//2
        self.bagBottom = self.screenHeight

        # suggested punch for user
        self.suggestion = ""

        self.gameStartTime = None

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
        self.kinect =\
        PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | \
            PyKinectV2.FrameSourceTypes_Body)

        # back buffer surface for getting Kinect color frames, 32bit color, 
        # width and height equal to the Kinect color frame size
        self.frameSurface = pygame.Surface((self.kinect.color_frame_desc.Width,\
                             self.kinect.color_frame_desc.Height), 0, 32)

        # here we will store skeleton data 
        self.bodies = None

    def displayPunchName(self,punchType):
        punchFont = pygame.font.Font(None, 70)
        punchText = punchFont.render(punchType,
                            1, (52, 152, 219))
        self.frameSurface.blit(punchText, (self.screenWidth//2+250,
            2*self.screenHeight//3))

    def drawTimerBar(self):
        margin = 75
        maxBar = self.screenWidth - 2*margin
        barHeight = 40
        roundLength = self.roundLength
        barLength = int((self.roundTimeLeft/roundLength) * maxBar)
        pygame.draw.rect(self.frameSurface,
                    (170, 218, 255),[margin,self.screenHeight-margin-barHeight,
                    barLength,barHeight])

    def getUserAccuracy(self):
        if self.totalPunches == 0:
            self.userAccuracy = 0 # can't div. by 0
        else:
            self.landedPunchCount = sum([self.numRightHooks,
                self.numRightUppercuts,self.numLeftHooks,
                self.numLeftUppercuts,self.numJabs,self.numCrosses])
            self.userAccuracy = (self.landedPunchCount+int(1/3*(self.glance)))\
                                    /self.totalPunches

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

    #### Checking Punch Type: Compare dX, dY, dZ ####

    # so DX DY DZ measure in meters
    # convert position of hand to pixels for collisions
    def isRightHook(self):
        # returns True if punch is mostly horizontal movement
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

            elif (abs(self.rightPunchDX) < abs(self.rightPunchDY)) or\
                (abs(self.rightPunchDX) < abs(self.rightPunchDZ)):
                print("not enough DX for right hook")
                return False # not a predominantly horizontal punch
            self.displayPunchName("right hook")
            print("right hook!")

            didItCollide = self.collision()
            if didItCollide == "glance":
               # counts as a punch, but did it land?
                self.glance += 1

            elif didItCollide == "hit":
                self.numRightHooks += 1

                centerX = self.bagRight+100
                centerY = (self.bagTop+self.bagBottom)//2
                starTime = 50
                while starTime > 0:
                    self.drawStar(centerX,centerY)# based on bot head location
                    starTime -= 1
            return True

    def isLeftHook(self):

        screenLeftDX = self.leftPunchDX*self.screenWidth
        hookThreshold = 28.6

        if (not self.isLeftPunching and self.leftPunchDX != 0):
            if self.leftPunchDX < 0:
                print("wrong way for left hook!")
                return False
            # left hooks move left to right (negative DX)
            elif abs(screenLeftDX) < self.screenWidth//hookThreshold:
                print("too small for left hook!")
                return False # small movements don't count
            elif (abs(self.leftPunchDX) < abs(self.leftPunchDY)) or\
                (abs(self.leftPunchDX) < abs(self.leftPunchDZ)):
                return False # not a predominantly horizontal punch
            self.displayPunchName("left hook")
            print("left hook!")
            didItCollide = self.collision()
            if didItCollide == "glance":
               # counts as a punch, but did it land?
                self.glance += 1
            elif didItCollide == "hit":
                self.numLeftHooks += 1
                centerX = self.bagLeft-100
                centerY = (self.bagTop+self.bagBottom)//2
                starTime = 50
                while starTime > 0:
                    self.drawStar(centerX,centerY)
                    starTime -= 1
            return True

    def isRightUppercut(self):
    # returns True if punch is mostly vertical movement
        
        screenRightDY = self.rightPunchDY*self.screenHeight
        uppercutThresh = 38.6

        if not self.isRightPunching and self.rightPunchDY != 0:
            if self.rightPunchDY < 0: # downwards doesn't count
                return False
            
            elif abs(screenRightDY) < self.screenHeight//uppercutThresh:
                print("your R upper is too small")
                return False # small movements don't count

            elif (abs(self.rightPunchDY) < abs(self.rightPunchDX)) or\
                (abs(self.rightPunchDY) < abs(self.rightPunchDZ)):
                print("your R upper DY is too small")
                return False # not a predominantly vertical punch
            self.displayPunchName("right uppercut")
            print("right uppercut!")

            didItCollide = self.collision()
            if didItCollide == "glance":
               # counts as a punch, but did it land?
                self.glance += 1

            elif didItCollide == "hit":
                self.numRightUppercuts += 1

                centerX = self.bagRight+100
                centerY = 2*(self.bagTop+self.bagBottom)//3
                starTime = 50
                while starTime > 0:
                    self.drawStar(centerX,centerY)
                    starTime -= 1
            return True  

    def isLeftUppercut(self):
    # returns True if punch is mostly vertical movement

        screenLeftDY = self.leftPunchDY*self.screenHeight
        uppercutThresh = 38.6

        if not self.isLeftPunching and self.leftPunchDY != 0:
            if self.leftPunchDY < 0: # downwards doesn't count
                return False
        
            elif abs(screenLeftDY) < self.screenHeight//uppercutThresh:
                print("your L uppercut is too small")
                return False # small movements don't count
            elif (abs(self.leftPunchDY) < abs(self.leftPunchDX)) or\
                (abs(self.leftPunchDY) < abs(self.leftPunchDZ)):
                print("your L upper dY is too small")
                return False # not a predominantly vertical punch
            self.displayPunchName("left uppercut")
            print("left uppercut!")

            didItCollide = self.collision()
            if didItCollide == "glance":
               # counts as a punch, but did it land?
                self.glance += 1

            elif didItCollide == "hit":
                self.numLeftUppercuts += 1

                centerX = self.bagLeft-100
                centerY = 2*(self.bagTop+self.bagBottom)//3
                starTime = 50
                while starTime > 0:
                    self.drawStar(centerX,centerY)
                    starTime -= 1
            return True 

    def isJab(self):
    # returns True if non-dominant hand has mostly depth movement
        depthThresh = 0.005

        if self.orthodox and not self.isLeftPunching:  
            if abs(self.leftPunchDZ) < depthThresh:
                print(self.leftPunchDZ,"left jab depth")
                return False
            elif (abs(self.leftPunchDZ) < abs(self.leftPunchDX)) or\
                (abs(self.leftPunchDZ) < abs(self.leftPunchDY)):
                print("not really a left jab")
                return False # not a predominantly DZ punch
            self.displayPunchName("left jab")
            print("left jab!")

            didItCollide = self.collision()
            if didItCollide == "glance":
               # counts as a punch, but did it land?
                self.glance += 1

            elif didItCollide == "hit":
                self.numJabs += 1
                centerX = self.bagLeft-100
                centerY = (self.bagTop+self.bagBottom)//2
                starTime = 50
                while starTime > 0:
                    self.drawStar(centerX,centerY)
                    starTime -= 1
            return True

        elif not self.orthodox and not self.isRightPunching:
            if self.rightPunchDZ < depthThresh:
                print(self.rightPunchDZ, "not enough right jab depth")
                return False
            elif (abs(self.rightPunchDZ) < abs(self.rightPunchDX)) or\
                (abs(self.rightPunchDZ) < abs(self.rightPunchDY)):
                print("not really a right jab")
                return False # not a predominantly DZ punch
            self.displayPunchName("right jab")
            print("right jab!")

            didItCollide = self.collision()
            if didItCollide == "glance":
               # counts as a punch, but did it land?
                self.glance += 1

            elif didItCollide == "hit":
                self.numJabs += 1
                centerX = self.bagRight-100
                centerY = (self.bagTop+self.bagBottom)//2
                starTime = 50
                while starTime > 0:
                    self.drawStar(centerX,centerY)
                    starTime -= 1
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
            elif (abs(self.rightPunchDZ) < abs(self.rightPunchDX)) or\
                (abs(self.rightPunchDZ) < abs(self.rightPunchDY)):
                print("not really a right cross")
                return False # not a predominantly DZ punch
            self.displayPunchName("right cross")
            print("right cross!")

            didItCollide = self.collision()
            if didItCollide == "glance":
               # counts as a punch, but did it land?
                self.glance += 1

            elif didItCollide == "hit":
                centerX = self.bagRight-100
                centerY = (self.bagTop+self.bagBottom)//2
                starTime = 50
                while starTime > 0:
                    self.drawStar(centerX,centerY)
                    starTime -= 1
                self.numCrosses += 1
            return True

        elif not self.orthodox and not self.isLeftPunching:
            if self.rightPunchDZ < 0:
                return False # pulling fist backwards doesn't count
                # small movements don't count
            elif abs(self.leftPunchDZ) < depthThresh:
                print(self.leftPunchDZ,"not enough left cross depth")
                return False
            elif (abs(self.leftPunchDZ) < abs(self.leftPunchDX)) or\
                (abs(self.leftPunchDZ) < abs(self.leftPunchDY)):
                print("not really a left cross")
                return False # not a predominantly DZ punch
            self.displayPunchName("left cross")
            print("left cross!")

            didItCollide = self.collision()
            if didItCollide == "glance":
               # counts as a punch, but did it land?
                self.glance += 1

            elif didItCollide == "hit":
                centerX = self.bagLeft-100
                centerY = (self.bagTop+self.bagBottom)//2
                starTime = 50
                while starTime > 0:
                    self.drawStar(centerX,centerY)
                    starTime -= 1
                self.numCrosses += 1
            return True

    def collision(self):
        #### checks for collision between user hand and bot head ####
        if not self.isRightPunching:

            # connected punches: user center of hand reaches virtual bag
            screenRightEndX = \
                self.rightPunchEndX*self.screenWidth+self.screenWidth//2
            screenRightEndY = \
                self.screenHeight//2-(self.rightPunchEndY*self.screenHeight)
            if self.bagLeft+25 < screenRightEndX < self.bagRight-25 and\
                screenRightEndY > (self.screenHeight-self.bagHeight-25):

                print("hit!")
                return "hit"
            # glancing punches: user hand reaches edge of virtual bag
            elif self.bagLeft < screenRightEndX < self.bagRight and\
                screenRightEndY > (self.screenHeight-self.bagHeight):

                print("glance")
                return ("glance")

        elif not self.isLeftPunching:
            # connected punches: user center of hand reaches bag
            screenLeftEndX = \
                self.leftPunchEndX*self.screenWidth+self.screenWidth//2
            screenLeftEndY = \
                self.screenHeight//2-(self.leftPunchEndY*self.screenHeight)
            if self.bagLeft+25 < screenLeftEndX < self.bagRight-25 and\
                screenLeftEndY > (self.screenHeight-self.bagHeight-25):

                print("hit!")
                return "hit"
            # glancing punches: user hand reaches edge of bag
            elif self.bagLeft < screenLeftEndX < self.bagRight and\
                screenLeftEndY > (self.screenHeight-self.bagHeight):

                print("glance")
                return "glance"

        # miss: none of user hand reaches bag
            # do not increase landed or glance counts          

    def drawPunchingBag(self):
        bagPoints = [(self.bagLeft,self.bagTop),
                    (self.bagLeft,self.bagBottom),
                    (self.bagRight,self.bagBottom),
                    (self.bagRight,self.bagTop)]

        pygame.draw.polygon(self.frameSurface,
                        (52, 73, 94),bagPoints)

        # chains at top of bag
        chainLeft = [self.bagLeft,self.bagTop]
        chainTop = [self.screenWidth//2,0]
        chainRight = [self.bagRight,self.bagTop]
        pygame.draw.line(self.frameSurface,
                        (231, 76, 60),chainLeft,chainTop,10)
        pygame.draw.line(self.frameSurface,
                        (231, 76, 60),chainRight,chainTop,10)

    def drawStar(self, x, y, diameter=100):
        numPoints = 12
        isOutRad = True
        outRad = diameter/2
        inRad = (5/8)*outRad
        pointList = []
        for num in range(numPoints*2): #points drawn is 2x number of star points
            angle = (2*math.pi*(num))/(numPoints*2) + math.pi/2
            if isOutRad: radius = outRad
            else: radius = inRad
            xCord = (x) + radius*math.cos(angle)
            yCord = (y) - radius*math.sin(angle)
            isOutRad = not isOutRad 
            pointList.append(((int(xCord),int(yCord))))
        
        pygame.draw.polygon(self.frameSurface,
                        (241, 196, 15),pointList)

    def suggestPunches(self):
        punchType = min({self.numRightHooks,self.numLeftHooks,
                            self.numRightUppercuts,self.numLeftUppercuts,
                            self.numJabs,self.numCrosses})

        if punchType == self.numRightHooks:
            self.suggestion = "right hooks!"
        elif punchType == self.numLeftHooks:
            self.suggestion = "left hooks!"
        elif punchType == self.numRightUppercuts:
            self.suggestion = "right uppercuts!"
        elif punchType == self.numLeftUppercuts:
            self.suggestion = "left uppercuts!"
        elif punchType == self.numJabs:
            self.suggestion = "jabs!"
        elif punchType == self.numCrosses:
            self.suggestion = "crosses!"

    def displaySuggestion(self):
        suggestionFont = pygame.font.Font(None, 70)
        suggestText = \
        suggestionFont.render("Throw more "+self.suggestion, 1, (52, 152, 219))
        self.frameSurface.blit(suggestText, (self.screenWidth//2+170,600))

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
                if self.kinect.has_new_body_frame(): # is IR camera working
                    self.bodies = self.kinect.get_last_body_frame()

                    if self.bodies is not None: 
                        for i in range(0, self.kinect.max_body_count):
                            body = self.bodies.bodies[i] #extract body object
                            if not body.is_tracked: # where is body
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

                                    if BagSeshRuntime.isRightHook(self):
                                        self.totalPunches += 1

                                    elif BagSeshRuntime.isRightUppercut(self):
                                        self.totalPunches += 1

                                    elif BagSeshRuntime.isJab(self):   
                                        self.totalPunches += 1
                                    # right jabs only for southpaw boxers
                                    elif BagSeshRuntime.isCross(self):
                                        
                                        self.totalPunches += 1
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
                                (PyKinectV2.HandState_Closed==\
                                    body.hand_left_state)

                                if self.isLeftHandClosed and \
                                self.leftPunchStartX == 0:
                                    self.isLeftPunching = True
                                    self.leftPunchStartX = self.currLeftHandX
                                    self.leftPunchStartY = self.currLeftHandY
                                    self.leftPunchStartZ = self.currLeftHandZ

                                elif not self.isLeftHandClosed and \
                                self.leftPunchStartX != 0:
                                #not currently punching
                                    self.isLeftPunching = False

                                    # save positions at end of punch (hand opens)
                                    if self.leftPunchStartX != 0 and \
                                    self.leftPunchEndX == 0:
                                        self.leftPunchEndX = self.currLeftHandX
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

                                    # reset punch start and end values
                                    self.leftPunchStartX = 0
                                    self.leftPunchStartY = 0
                                    self.leftPunchStartZ = 0
                                    self.leftPunchEndX = 0
                                    self.leftPunchEndY = 0
                                    self.leftPunchEndZ = 0

                                    if BagSeshRuntime.isLeftHook(self):
                                        self.totalPunches += 1

                                    elif BagSeshRuntime.isLeftUppercut(self):
                                        self.totalPunches += 1

                                    elif BagSeshRuntime.isJab(self):
                                        self.totalPunches += 1
                                    # left jabs only for orthodox boxers

                                    elif BagSeshRuntime.isCross(self):
                                        self.totalPunches += 1
                                    # left crosses only for southpaw boxers  

                                # reset delta's after calculating punch
                                self.leftPunchDX = 0
                                self.leftPunchDY = 0
                                self.leftPunchDZ = 0                      


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
                        
            # --- Game logic 
            # Draw graphics
            self.drawPunchingBag()
            self.drawTimerBar()

            # update user's accuracy so far
            self.getUserAccuracy()

            self.suggestPunches()
            self.displaySuggestion()

            self.displayWarning()

            # text displaying round time left
            pygame.draw.rect(self.frameSurface,(189, 195, 199),
                [75,self.screenHeight-425,500,300])
            roundTimeFont = pygame.font.Font(None, 80)
            if self.roundTimeLeft%60 != 0:
                if self.roundTimeLeft%60 >= 10:
                    roundText = roundTimeFont.render("Round Time: "+\
                        str(self.roundTimeLeft//60)+":"+\
                        "%d"%(self.roundTimeLeft%60),
                               1, (192, 57, 43))
                else:
                    roundText = roundTimeFont.render("Round Time: "+\
                        str(self.roundTimeLeft//60)+":"+"0"+\
                        "%d"%(self.roundTimeLeft%60),
                               1, (192, 57, 43))
            else:
                roundText = roundTimeFont.render("Round Time: "+\
                    str(self.roundTimeLeft//60)+":"+"00",
                               1, (192, 57, 43))

            self.frameSurface.blit(roundText, (100,self.screenHeight-400))

            currRoundFont = pygame.font.Font(None, 80)
            currRoundText = currRoundFont.render("Round "+\
                str(self.currRound),1, (0, 110, 27))
            self.frameSurface.blit(currRoundText, (100,self.screenHeight-200))

            # text displaying rest time left
            restTimeFont = pygame.font.Font(None, 80)
            if self.restTimeLeft%60 != 0:
                if self.restTimeLeft%60 >= 10:
                    restText = restTimeFont.render("Rest Time: "+\
                        str(self.restTimeLeft//60)+":"+\
                        "%d"%(self.restTimeLeft%60),
                               1, (39, 174, 96))
                else:
                    restText = restTimeFont.render("Rest Time: "+\
                        str(self.restTimeLeft//60)+":"+"0"+\
                        "%d"%(self.restTimeLeft%60),
                               1, (39, 174, 96))
            else:
                restText = restTimeFont.render("Rest Time: "+\
                    str(self.restTimeLeft//60)+":"+"00",
                               1, (39, 174, 96))

            self.frameSurface.blit(restText, (100,self.screenHeight-300))

            if self.roundTimeLeft == 10:
                tenSecWarning = roundTimeFont.render("10 seconds!",
                                    1, (170, 218, 255))
                self.frameSurface.blit(tenSecWarning, (self.screenWidth//2,200))

            # section (6 lines) from github.com/fletcher-marsh
            # --- copy back buffer surface pixels to the screen
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
            if self.gameTimeLeft == self.preGameBuffer + self.postGameBuffer +\
                self.numRounds*(self.roundTimeLeft+self.restTimeLeft) and\
                    self.threeSecWarningPlayed == False:#188:
                pygame.mixer.Sound.play(self.bellSound)
                self.threeSecWarningPlayed = True

            if self.gameTimeLeft == self.postGameBuffer +\
            self.numRounds*(self.roundTimeLeft+self.restTimeLeft):
                self.roundOngoing = True

            # --- 60 frames per second
            self.clock.tick(60)
            if self.gameStartTime == None:
                self.gameStartTime = pygame.time.get_ticks()
            self.gameTimeLeft = (self.preGameBuffer+self.postGameBuffer\
             + self.numRounds*(self.roundLength+self.restLength))\
              - (pygame.time.get_ticks()-self.gameStartTime)//1000

            modGameTime = ((self.gameTimeLeft-self.postGameBuffer-1) %\
                (self.roundLength+self.restLength))
            
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
                self.currRound = self.numRounds-self.gameTimeLeft //\
                (self.roundLength+self.restLength)+1
            if self.gameTimeLeft == 0:
                self.gameOver = True

        # Close Kinect sensor, close the window and quit.
        self.kinect.close()
        pygame.quit()