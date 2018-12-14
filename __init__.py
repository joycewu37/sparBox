# Joyce Wu
# ID: joycewu
# Section: A
# 15-112 Fall 18 Term Project: Virtual Box

# __init__.py binds the modes of gameplay and user interface into one experience

# if modules have not been installed:
import module_manager
module_manager.review()

from tkinter import *

import string
import os

import matplotlib.pyplot as plt
import numpy as np

import smtplib
from email.message import EmailMessage

import sparSesh
import bagSesh
import comboSesh

def init(data):

    # for username screen:
    data.mode = "usernameScreen"
    data.prevMode = None
    data.username = ""

    # for pre screen:
    data.isOrthodox = None
    data.username = ""
    data.allUsers = dict()

    # for pre spar:
    data.userInputRounds = 12

    # for splash screen:
    data.splashButtonWidth = 250
    data.splashButtonHeight = 60
    loadLogo(data)
    data.newSparSesh = None
    data.newBagSesh = None
    data.newComboSesh = None

    # for tutorial screen:
    data.currInstruct = 0
    loadInstructions(data)
    data.coachIsPunching = False
    data.timerCalls = 0

    # for pre- and end screen:
    data.mainButtonWidth = 250
    data.mainButtonHeight = 60
    data.hiScoreShowing = False

def loadLogo(data):
    logoName = "SparBox.001.gif" # logo in same directory as file
    data.logo = PhotoImage(file=logoName)

def loadInstructions(data):
    neutral = "neutral.gif"
    jab = "jab.gif"
    cross = "cross.gif"
    leadHook = "leadHook.gif"
    rearHook = "rearHook.gif"
    leadUpper = "leadUpper.gif"
    rearUpper = "rearUpper.gif"

    data.neutralImg = PhotoImage(file=neutral)
    data.jabImg = PhotoImage(file=jab)
    data.crossImg = PhotoImage(file=cross)
    data.leadHookImg = PhotoImage(file=leadHook)
    data.rearHookImg = PhotoImage(file=rearHook)
    data.leadUpperImg = PhotoImage(file=leadUpper)
    data.rearUpperImg = PhotoImage(file=rearUpper)

def mousePressed(event,data):
# handle clicks from user
    if (data.mode == "usernameScreen"):
        usernameScreenMousePressed(event,data)
    elif (data.mode == "preScreen"):
        preScreenMousePressed(event,data)
    elif (data.mode == "splashScreen"):
        splashScreenMousePressed(event,data)
    elif (data.mode == "tutorial"):
        tutorialMousePressed(event,data)
    elif (data.mode == "preSpar"):
        preSparMousePressed(event,data)
    elif (data.mode == "sparSesh"):
        sparSeshMousePressed(event,data)
    elif (data.mode == "preBag"):
        preBagMousePressed(event,data)
    elif (data.mode == "bagSesh"):
        bagSeshMousePressed(event,data)
    elif (data.mode == "preCombo"):
        preComboMousePressed(event,data)
    elif (data.mode == "comboSesh"):
        comboSeshMousePressed(event,data)
    elif (data.mode == "endScreen"):
        prevMode = data.prevMode
        endScreenMousePressed(event,data,prevMode)

def keyPressed(event,data):
# handle key events from user
    if (data.mode == "usernameScreen"):
        usernameScreenKeyPressed(event,data)
    elif (data.mode == "preScreen"):
        preScreenKeyPressed(event,data)
    elif (data.mode == "splashScreen"):
        splashScreenKeyPressed(event,data)
    elif (data.mode == "tutorial"):
        tutorialKeyPressed(event,data)
    elif (data.mode == "preSpar"):
        preSparKeyPressed(event,data)
    elif (data.mode == "sparSesh"):
        sparSeshKeyPressed(event,data)
    elif (data.mode == "preBag"):
        preBagKeyPressed(event,data)
    elif (data.mode == "bagSesh"):
        bagSeshKeyPressed(event,data)
    elif (data.mode == "preCombo"):
        preComboKeyPressed(event,data)
    elif (data.mode == "comboSesh"):
        comboSeshKeyPressed(event,data)
    elif (data.mode == "endScreen"):
        prevMode = data.prevMode
        endScreenKeyPressed(event,data,prevMode)   

def timerFired(data):
# update animation every 100 milliseconds
    if (data.mode == "usernameScreen"):
        usernameScreenTimerFired(data)
    elif (data.mode == "preScreen"):
        preScreenTimerFired(data)
    elif (data.mode == "splashScreen"):
        splashScreenTimerFired(data)
    elif (data.mode == "tutorial"):
        tutorialTimerFired(data)
    elif (data.mode == "preSpar"):
        preSparTimerFired(data)
    elif (data.mode == "sparSesh"):
        sparSeshTimerFired(data)
    elif (data.mode == "preBag"):
        preBagTimerFired(data)
    elif (data.mode == "bagSesh"):
        bagSeshTimerFired(data)
    elif (data.mode == "preCombo"):
        preComboTimerFired(data)
    elif (data.mode == "comboSesh"):
        comboSeshTimerFired(data)
    elif (data.mode == "endScreen"):
        prevMode = data.prevMode
        endScreenTimerFired(data,prevMode)

def redrawAll(canvas,data):
# redraws animation on screen repeatedly
    if (data.mode == "usernameScreen"):
        usernameScreenRedrawAll(canvas,data)
    elif (data.mode == "preScreen"):
        preScreenRedrawAll(canvas,data)
    elif (data.mode == "splashScreen"):
        splashScreenRedrawAll(canvas,data)
    elif (data.mode == "tutorial"):
        tutorialRedrawAll(canvas,data)
    elif (data.mode == "preSpar"):
        preSparRedrawAll(canvas,data)
    elif (data.mode == "sparSesh"):
        sparSeshRedrawAll(canvas,data)
    elif (data.mode == "preBag"):
        preBagRedrawAll(canvas,data)
    elif (data.mode == "bagSesh"):
        bagSeshRedrawAll(canvas,data)
    elif (data.mode == "preCombo"):
        preComboRedrawAll(canvas,data)
    elif (data.mode == "comboSesh"):
        comboSeshRedrawAll(canvas,data)
    elif (data.mode == "endScreen"):
        prevMode = data.prevMode
        endScreenRedrawAll(canvas,data,prevMode)

# NOTE: each of the 3 game modes has their own end screen so pass in a parameter

####################################
# usernameScreen mode
####################################
def usernameScreenMousePressed(event,data):
    pass

def usernameScreenKeyPressed(event,data):
# user can enter alphanumeric usnername with no spaces
    if event.char.isalnum():
        data.username = data.username + event.char
    elif event.keysym == "BackSpace":
        if len(data.username) > 0:
            data.username = data.username[:-1]
    elif event.keysym == "Return":
        if data.username != "":
            data.allUsers[data.username] = [None,None,None]
            for filename in os.listdir():
                if data.username+"Spar.txt" in filename:
                    data.allUsers[data.username][0] = readFile(data.username+"Spar.txt")
                if data.username+"Bag.txt" in filename:
                    data.allUsers[data.username][1] = readFile(data.username+"Bag.txt")
                if data.username+"Combo.txt" in filename:
                    data.allUsers[data.username][2] = readFile(data.username+"Combo.txt")
            data.mode = "preScreen"

def usernameScreenTimerFired(data):
    pass

def usernameScreenRedrawAll(canvas,data):
    yStart = data.height//4
    yStep = data.height//4
    # enter your name:
    canvas.create_text(data.width//2, yStart,
        text="Enter your name:",
        fill="white", font="Courier 36")
    # username drawn on screen
    canvas.create_text(data.width//2, yStart+yStep,
        text=data.username+"_",
        fill="white", font="Courier 36")

    # press 'enter' to continue
    canvas.create_text(data.width//2, yStart+2*yStep,
        text="press 'ENTER' to continue",
        fill="white", font="Courier 36")

####################################
# preScreen mode
####################################

def preScreenMousePressed(event,data):
    gap = 15
    buttonX = 250
    buttonY = 30
    centerX = buttonX//2+gap
    if (data.width//2-buttonX-gap <= event.x <= data.width//2-gap) and\
        (data.height//2-buttonY <= event.y <= data.height//2+buttonY):
        data.isOrthodox = True
        data.mode = "splashScreen"
    elif (data.width//2+gap <= event.x <= data.width//2+buttonX+gap) and\
        (data.height//2-buttonY <= event.y <= data.height//2+buttonY):
        data.isOrthodox = False
        data.mode = "splashScreen"

def preScreenKeyPressed(event,data):
    pass

def preScreenTimerFired(data):
    pass

def drawPreButtons(canvas,data,cX,cY):
    buttonWidth = data.mainButtonWidth
    buttonHeight = data.mainButtonHeight

    buttonAlign = 160
    canvas.create_rectangle(cX-buttonAlign-buttonWidth//2,cY-buttonHeight//2,
                            cX-buttonAlign+buttonWidth//2,cY+buttonHeight//2,
                            fill="PaleGreen3")
    canvas.create_text(cX-buttonAlign,cY,text="MAIN",
                        fill="gray25",font="Helvetica 24")
    
    canvas.create_rectangle(cX+buttonAlign-buttonWidth//2,cY-buttonHeight//2,
                            cX+buttonAlign+buttonWidth//2,cY+buttonHeight//2,
                            fill="dark green")
    canvas.create_text(cX+buttonAlign,cY,text="BEGIN",
                        fill="SlateGray2",font="Helvetica 24")

def preScreenRedrawAll(canvas,data):
    # black background
    canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='black', width=0)

    # fighters may practice fighting in different stances
    canvas.create_text(data.width//2,data.height//2-100,
                        text="Which stance?",
                        fill="white", font="Courier 36")

    # buttons are 250 by 60 in size
    gap = 15
    buttonX = 250
    buttonY = 30
    centerX = buttonX//2+gap
    # "yes" button
    canvas.create_rectangle(data.width//2-(buttonX+gap),data.height//2-buttonY,
                            data.width//2-gap,data.height//2+buttonY,
                            fill="dark green")
    canvas.create_text(data.width//2-centerX,data.height//2,
                        text="ORTHODOX",font="Helvetica 16",fill="SlateGray2")

    # "no" button
    canvas.create_rectangle(data.width//2+gap,data.height//2-buttonY,
                            data.width//2+buttonX+gap,data.height//2+buttonY,
                            fill="dark green")
    canvas.create_text(data.width//2+centerX,data.height//2,
                        text="SOUTHPAW",font="Helvetica 16",fill="SlateGray2")   

####################################
# splashScreen mode
####################################

def getSparButtonCenter(data):
    cX = data.width//2
    cY = 2*data.height//5
    return (cX,cY)

def getBagButtonCenter(data):
    cX = data.width//2
    cY = 3*data.height//5
    return (cX,cY)

def getComboButtonCenter(data):
    cX = data.width//2
    cY = 4*data.height//5
    return (cX,cY)

def splashScreenMousePressed(event,data):
    # center coordinates (cX, cY) of each mode's button
    sparX, sparY = getSparButtonCenter(data)
    bagX, bagY = getBagButtonCenter(data)
    comboX, comboY = getComboButtonCenter(data)

    margin = 75
    helpButtonSize = 60

    buttonWidth, buttonHeight = data.splashButtonWidth, data.splashButtonHeight

    if (sparX-buttonWidth//2 <= event.x <= sparX + buttonWidth//2) and \
        (sparY-buttonHeight//2 <= event.y <= sparY + buttonHeight//2):
        data.mode = "preSpar"


    elif (bagX-buttonWidth//2 <= event.x <= bagX + buttonWidth//2) and \
        (bagY-buttonHeight//2 <= event.y <= bagY + buttonHeight//2):
        data.mode = "preBag"

    elif (comboX-buttonWidth//2 <= event.x <= comboX + buttonWidth//2) and \
        (comboY-buttonHeight//2 <= event.y <= comboY + buttonHeight//2):
        data.mode = "preCombo"

    elif (data.width-margin-helpButtonSize <= event.x <= data.width-margin) and\
        (data.height-margin-helpButtonSize <= event.y <= data.height-margin):
        data.mode = "tutorial"

def splashScreenKeyPressed(event,data):
    pass

def splashScreenTimerFired(data):
    pass

def drawLogo(canvas,data,x,y):
    canvas.create_image(x,y, image=data.logo)

def drawSplashButtons(canvas,data):
    buttonWidth, buttonHeight = data.splashButtonWidth, data.splashButtonHeight

    sparX, sparY = getSparButtonCenter(data)
    canvas.create_rectangle(sparX-buttonWidth//2,sparY-buttonHeight//2,
                            sparX+buttonWidth//2,sparY+buttonHeight//2,
                            fill="dark green")
    canvas.create_text(sparX,sparY,text="SPAR",
                        font="Helvetica 24", fill="SlateGray2")

    bagX, bagY = getBagButtonCenter(data)
    canvas.create_rectangle(bagX-buttonWidth//2,bagY-buttonHeight//2,
                            bagX+buttonWidth//2,bagY+buttonHeight//2,
                            fill="dark green")
    canvas.create_text(bagX,bagY,text="BAG WORK",
                        font="Helvetica 24", fill="SlateGray2")

    comboX, comboY = getComboButtonCenter(data)
    canvas.create_rectangle(comboX-buttonWidth//2,comboY-buttonHeight//2,
                            comboX+buttonWidth//2,comboY+buttonHeight//2,
                            fill="dark green")  
    canvas.create_text(comboX,comboY,text="COMBOS",
                        font="Helvetica 24", fill="SlateGray2")  

    margin = 75
    helpButtonSize = 60
    canvas.create_rectangle(data.width-margin-helpButtonSize,
                            data.height-margin-helpButtonSize,
                            data.width-margin,
                            data.height-margin, fill="SlateGray2")
    canvas.create_text(data.width-margin-helpButtonSize//2,
                        data.height-margin-helpButtonSize//2,
                        text="?",
                        font="Helvetica 24", fill="gray24")  

def splashScreenRedrawAll(canvas,data):

    # black background
    canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='black', width=0)

    # sparbox in green (image)
    drawLogo(canvas,data,data.width//2,data.height//6)

    # subtitle text right below
    textSpacing = 65
    canvas.create_text(data.width//2,data.height//6+textSpacing,
                        text="master boxing single-handedly",
                        font="Courier 24", fill="SlateGray3")

    # 3 buttons
    drawSplashButtons(canvas,data)

####################################
# tutorial mode
####################################
def tutorialMousePressed(event,data):
    margin = 75
    buttonHeight = 50
    buttonWidth = 200

    if (margin <= event.x <= margin+buttonWidth) and \
        (data.height-margin-buttonHeight <=event.y<= data.height-margin):
        data.mode = "splashScreen"

def tutorialKeyPressed(event,data):
    if 1 <= int(event.char) <= 6:
        data.currInstruct = int(event.char)

def tutorialTimerFired(data):
# coach moves from neutral to punching position, stop-motion animation
    animateSpeed = 7
    data.timerCalls += 1
    if data.timerCalls % animateSpeed == 0:
        data.coachIsPunching = not data.coachIsPunching

def tutorialRedrawAll(canvas,data):
    margin = 75
    buttonHeight = 50
    buttonWidth = 200

    # instructions text
    canvas.create_text(data.width//2,margin,
        text="Press keys 1-6 to see each punch description",
        font="Courier 24", fill="SlateGray3")
    canvas.create_text(data.width//2,2*margin,
        text="Orthodox: mirror the images below",
        font="Courier 24", fill="SlateGray3")

    # back button
    canvas.create_rectangle(margin,data.height-margin-buttonHeight,
                margin+buttonWidth,data.height-margin,
                fill="dark green")
    canvas.create_text(margin+buttonWidth//2,
                        data.height-margin-buttonHeight//2,
                        text="BACK",
                        font="Helvetica 24", fill="SlateGray2") 

    # specific punch instruction
    if not data.coachIsPunching:
        canvas.create_image(data.width//2,data.height//2+margin,
            image=data.neutralImg)
    else:
        if data.currInstruct == 1:
            canvas.create_image(data.width//2,data.height//2+margin,
                image=data.jabImg)
        elif data.currInstruct == 2:
            canvas.create_image(data.width//2,data.height//2+margin,
                image=data.crossImg)
        elif data.currInstruct == 3:
            canvas.create_image(data.width//2,data.height//2+margin,
                image=data.leadHookImg)
        elif data.currInstruct == 4:
            canvas.create_image(data.width//2,data.height//2+margin,
                image=data.rearHookImg)
        elif data.currInstruct == 5:
            canvas.create_image(data.width//2,data.height//2+margin,
                image=data.leadUpperImg)
        elif data.currInstruct == 6:
            canvas.create_image(data.width//2,data.height//2+margin,
                image=data.rearUpperImg)

####################################
# preSpar mode
####################################
def preSparMousePressed(event,data):

    buttonWidth = data.mainButtonWidth
    buttonHeight = data.mainButtonHeight

    buttonAlign = 160
    lineSpacing = 75

    cX, cY = data.width//2, data.height//3+4*lineSpacing

    if (cX-buttonAlign-buttonWidth//2 <= event.x <=
                cX-buttonAlign+buttonWidth//2) and \
        (cY-buttonHeight//2 <= event.y <= cY+buttonHeight//2):
        data.mode = "splashScreen"

    elif (cX+buttonAlign-buttonWidth//2 <= event.x <=
                cX+buttonAlign+buttonWidth//2) and \
        (cY-buttonHeight//2 <= event.y <= cY+buttonHeight//2):
        data.newSparSesh = \
            sparSesh.SparSeshRuntime(data.isOrthodox,data.userInputRounds)
        data.newSparSesh.run()
        data.mode = "sparSesh"

def preSparKeyPressed(event,data):
    if event.keysym in {"Up","Right"}:
        if data.userInputRounds <= 11: # > 12 rounds is too strenuous
            data.userInputRounds += 1

    elif event.keysym in {"Down","Left"}:
        if data.userInputRounds > 1: # can't have no rounds
            data.userInputRounds -= 1

    elif event.char == "s": # speedy walkthrough for demo purposes
        data.newSparSesh = \
        sparSesh.SparSeshRuntime(data.isOrthodox,data.userInputRounds,60,30)
        data.newSparSesh.run()
        data.mode = "sparSesh"

def preSparTimerFired(data):
    pass

def preSparRedrawAll(canvas,data):
    canvas.create_text(data.width//2, data.height//4,
                text="How many rounds? Use arrow keys",
                font="Helvetica 24", fill = "SlateGray2")
    canvas.create_text(data.width//2, 2*data.height//4,
                text=str(data.userInputRounds),
                font="Helvetica 24", fill = "SlateGray2")	

    lineSpacing = 75
    mainX, mainY = data.width//2, data.height//3+4*lineSpacing
    drawPreButtons(canvas,data,mainX,mainY)

####################################
# sparSesh mode
####################################

def sparSeshMousePressed(event,data):
    pass

def sparSeshKeyPressed(event,data):
    pass

def sparSeshTimerFired(data):
    pass

def sparSeshRedrawAll(canvas,data):
    data.mode = "endScreen"
    data.prevMode = "sparSesh"
    

####################################
# preBag mode
####################################
def preBagMousePressed(event,data):
    buttonWidth = data.mainButtonWidth
    buttonHeight = data.mainButtonHeight

    buttonAlign = 160
    lineSpacing = 75

    cX, cY = data.width//2, data.height//3+4*lineSpacing

    if (cX-buttonAlign-buttonWidth//2 <= event.x <=
                cX-buttonAlign+buttonWidth//2) and \
        (cY-buttonHeight//2 <= event.y <= cY+buttonHeight//2):
        data.mode = "splashScreen"

    elif (cX+buttonAlign-buttonWidth//2 <= event.x <=
                cX+buttonAlign+buttonWidth//2) and \
        (cY-buttonHeight//2 <= event.y <= cY+buttonHeight//2):
        print("clicked")
        data.newBagSesh = bagSesh.BagSeshRuntime(data.isOrthodox)
        data.newBagSesh.run()
        data.mode = "bagSesh"

def preBagKeyPressed(event,data):
    if event.keysym in {"Up","Right"}:
        if data.userInputRounds <= 11: # > 12 rounds is heart failure
            data.userInputRounds += 1

    elif event.keysym in {"Down","Left"}:
        if data.userInputRounds > 1: # can't have no rounds
            data.userInputRounds -= 1

    elif event.char == "s": # speedy walkthrough for demo purposes
        data.newBagSesh = \
        bagSesh.BagSeshRuntime(data.isOrthodox,data.userInputRounds,60,30)
        data.newBagSesh.run()
        data.mode = "bagSesh"

def preBagTimerFired(data):
    pass

def preBagRedrawAll(canvas,data):
    canvas.create_text(data.width//2, data.height//4,
                text="How many rounds? Use arrow keys",
                font="Helvetica 24", fill = "SlateGray2")
    canvas.create_text(data.width//2, 2*data.height//4,
                text=str(data.userInputRounds),
                font="Helvetica 24", fill = "SlateGray2")   

    lineSpacing = 75
    mainX, mainY = data.width//2, data.height//3+4*lineSpacing
    drawPreButtons(canvas,data,mainX,mainY)

####################################
# bagSesh mode
####################################

def bagSeshMousePressed(event,data):
    pass

def bagSeshKeyPressed(event,data):
    pass

def bagSeshTimerFired(data):
    pass

def bagSeshRedrawAll(canvas,data):
    data.mode = "endScreen"
    data.prevMode = "bagSesh"
    

####################################
# preCombo mode
####################################
def preComboMousePressed(event,data):
    buttonWidth = data.mainButtonWidth
    buttonHeight = data.mainButtonHeight

    buttonAlign = 160
    lineSpacing = 75

    cX, cY = data.width//2, data.height//3+4*lineSpacing

    if (cX-buttonAlign-buttonWidth//2 <= event.x <=
                cX-buttonAlign+buttonWidth//2) and \
        (cY-buttonHeight//2 <= event.y <= cY+buttonHeight//2):
        data.mode = "splashScreen"

    elif (cX+buttonAlign-buttonWidth//2 <= event.x <=
                cX+buttonAlign+buttonWidth//2) and \
        (cY-buttonHeight//2 <= event.y <= cY+buttonHeight//2):
        data.newComboSesh = comboSesh.ComboSeshRuntime(data.isOrthodox)
        data.newComboSesh.run()
        data.mode = "comboSesh"

def preComboKeyPressed(event,data):
    if event.keysym in {"Up","Right"}:
        if data.userInputRounds <= 11: # > 12 rounds is too strenuous
            data.userInputRounds += 1

    elif event.keysym in {"Down","Left"}:
        if data.userInputRounds > 1: # can't have no rounds
            data.userInputRounds -= 1

    elif event.char == "s": # speedy walkthrough for demo purposes
        data.newComboSesh = \
        comboSesh.ComboSeshRuntime(data.isOrthodox,data.userInputRounds,60,30)
        data.newComboSesh.run()
        data.mode = "comboSesh"

def preComboTimerFired(data):
    pass

def preComboRedrawAll(canvas,data):
    canvas.create_text(data.width//2, data.height//4,
                text="How many rounds? Use arrow keys",
                font="Helvetica 24", fill = "SlateGray2")
    canvas.create_text(data.width//2, 2*data.height//4,
                text=str(data.userInputRounds),
                font="Helvetica 24", fill = "SlateGray2")   

    lineSpacing = 75
    mainX, mainY = data.width//2, data.height//3+4*lineSpacing
    drawPreButtons(canvas,data,mainX,mainY)
    
####################################
# comboSesh mode
####################################

def comboSeshMousePressed(event,data):
    pass

def comboSeshKeyPressed(event,data):
    pass

def comboSeshTimerFired(data):
    pass

def comboSeshRedrawAll(canvas,data):
    data.mode = "endScreen"
    data.prevMode = "comboSesh"  

####################################
# endScreen modes (spar, bag, combo)
####################################

#### end mousePressed functions ####

def endScreenMousePressed(event,data,prevMode):
# dispatches mousePressed to correct endscreen based on game mode
    prevMode = data.prevMode
    if prevMode == "sparSesh":
        sparEndMousePressed(event,data)

    elif prevMode == "bagSesh":
        bagEndMousePressed(event,data)

    elif prevMode == "comboSesh":
        comboEndMousePressed(event,data)

def sparEndMousePressed(event,data):
    buttonWidth = data.mainButtonWidth
    buttonHeight = data.mainButtonHeight

    buttonAlign = 160
    lineSpacing = 75

    cX, cY = data.width//2, data.height//3+4*lineSpacing

    if (cX-buttonAlign-buttonWidth//2 <= event.x <=
                cX-buttonAlign+buttonWidth//2) and \
        (cY-buttonHeight//2 <= event.y <= cY+buttonHeight//2):
        data.mode = "splashScreen"

    elif (cX+buttonAlign-buttonWidth//2 <= event.x <=
                cX+buttonAlign+buttonWidth//2) and \
        (cY-buttonHeight//2 <= event.y <= cY+buttonHeight//2):
        data.newSparSesh = sparSesh.SparSeshRuntime(data.isOrthodox)
        data.newSparSesh.run()
        data.mode = "sparSesh" # need to restart the runtime

def bagEndMousePressed(event,data):
    buttonWidth = data.mainButtonWidth
    buttonHeight = data.mainButtonHeight

    buttonAlign = 160
    lineSpacing = 40

    cX, cY = data.width//2, data.height//3+7.5*lineSpacing

    if (cX-buttonAlign-buttonWidth//2 <= event.x <=
                cX-buttonAlign+buttonWidth//2) and \
        (cY-buttonHeight//2 <= event.y <= cY+buttonHeight//2):
        data.mode = "splashScreen"

    elif (cX+buttonAlign-buttonWidth//2 <= event.x <=
                cX+buttonAlign+buttonWidth//2) and \
        (cY-buttonHeight//2 <= event.y <= cY+buttonHeight//2):
        data.newBagSesh = bagSesh.BagSeshRuntime(data.isOrthodox)
        data.newBagSesh.run()
        data.mode = "bagSesh" # need to restart the runtime 

def comboEndMousePressed(event,data):
    buttonWidth = data.mainButtonWidth
    buttonHeight = data.mainButtonHeight

    buttonAlign = 160
    lineSpacing = 75

    cX, cY = data.width//2, data.height//3+4*lineSpacing

    if (cX-buttonAlign-buttonWidth//2 <= event.x <=
                cX-buttonAlign+buttonWidth//2) and \
        (cY-buttonHeight//2 <= event.y <= cY+buttonHeight//2):
        data.mode = "splashScreen"

    elif (cX+buttonAlign-buttonWidth//2 <= event.x <=
                cX+buttonAlign+buttonWidth//2) and \
        (cY-buttonHeight//2 <= event.y <= cY+buttonHeight//2):
        data.newComboSesh = comboSesh.ComboSeshRuntime(data.isOrthodox)
        data.newComboSesh.run()
        data.mode = "comboSesh" # need to restart the runtime


#### write user session info functions ####
def writeSparText(data):
# each spar session makes a string of 7 lines, including \n to start
    session = data.newSparSesh
    sparContents = \
    "\nUser landed strikes: "+str(session.landedPunchCount)+"\n"+\
    "Total user strikes: "+str(session.totalPunches)+"\n"+\
    "Accuracy: %0.2f"%(session.userAccuracy)+"\n"+\
    "Bot landed strikes: "+str(session.botLanded)+"\n"+\
    "Total bot strikes: "+str(session.botTotal)+"\n"+\
    "Bot accuracy: %0.2f\n"%(session.botAccuracy)
    return sparContents

def writeBagText(data):
# each bag session makes a string of 7 lines, including \n to start
    session = data.newBagSesh
    bagContents = "\nJabs: "+str(session.numJabs)+"\n"+\
    "Crosses: "+str(session.numCrosses)+"\n"+\
    "Hooks: "+str(session.numLeftHooks+session.numRightHooks)+"\n"+\
    "Uppercuts: "+str(session.numLeftUppercuts+session.numRightUppercuts)+\
    "\n"+\
    "Total strikes: "+str(session.totalPunches)+"\n"+\
    "Accuracy: %0.2f"%(session.userAccuracy)
    return bagContents

def writeComboText(data):
# each combo session makes a string of 4 lines, including \n to start
    session = data.newComboSesh
    comboContents = "\nCorrect Punches: "+str(session.correctPunchCount)+"\n"+\
    "Total strikes: "+str(session.totalPunches)+"\n"+\
    "Accuracy: %0.2f"%(session.userAccuracy)
    return comboContents

# read file function from 15-112 website
def readFile(path):
    with open(path, "rt") as f:
        return f.read()

# write function from 15-112 website
def writeFile(path,contents):
    with open(path, "wt") as f:
        f.write(contents)

#### mail results functions ####
# attempts to email result from sparboxcoach@gmail.com
# results in Google critical security alert
# https://www.pythonforbeginners.com/code-snippets-source-code/
# using-python-to-send-email
def sendSparMail(data):    
    with open(data.username+"Spar.txt") as fp:
        msg = EmailMessage()
        msg.set_content(fp.read())

    server = smtplib.SMTP("smtp.gmail.com",587)
    server.ehlo()
    server.starttls()
    server.login("sparboxcoach@gmail.com","itrainboxers")

    server.sendmail('sparboxcoach@gmail.com','bronkie2000@gmail.com',msg)
    server.quit()

def sendBagMail(data):
    with open(data.username+"Bag.txt") as fp:
        msg = EmailMessage()
        msg.set_content(fp.read())

    server = smtplib.SMTP("smtp.gmail.com",587)
    server.ehlo()
    server.starttls()
    server.login("sparboxcoach@gmail.com","itrainboxers")

    server.sendmail('sparboxcoach@gmail.com','bronkie2000@gmail.com',msg)
    server.quit()

def sendComboMail(data):
    with open(data.username+"Combo.txt") as fp:
        msg = EmailMessage()
        msg.set_content(fp.read())

    server = smtplib.SMTP("smtp.gmail.com",587)
    server.ehlo()
    server.starttls()
    server.login("sparboxcoach@gmail.com","itrainboxers")

    server.sendmail('sparboxcoach@gmail.com','bronkie2000@gmail.com',msg)
    server.quit()

# lineplot from https://towardsdatascience.com/
# 5-quick-and-easy-data-visualizations-in-python-with-code-a2284bae952f
def lineplot(data,xData, yData,
        xLabel="Session #", yLabel="Accuracy", title=""):
    # Create the plot object
    fig, ax = plt.subplots(figsize=(data.width//2,data.height//2))

    # Plot the best fit line, set the linewidth (lw), color and
    # transparency (alpha) of the line
    ax.plot(xData, yData, lw = 2, color = '#539caf', alpha = 1)

    # Label the axes and provide a title
    ax.set_title(title)
    ax.set_xlabel(xLabel)
    ax.set_ylabel(yLabel)

    win = fig.canvas.window()
    win.setFixedSize(win.size())
    plt.show()

def getSparChart(data):
# displays user progress in accuracy over last 5 sessions for spar mode
    user = data.username
    numSeshes = 5
    xData = [i for i in range(1,6)]
    yData = []
    userHistory = data.allUsers[user][0]
    if userHistory == None: return
    for line in userHistory.splitlines():
        if line.startswith("Accuracy:"):
            stat = float(line[-4:])
            yData.append(stat)
    while len(yData) < numSeshes:
        yData.insert(0,0)
    lineplot(data,xData,yData,"Session #","Accuracy","Accuracy Over Time")

def getBagChart(data):
# displays user progress in accuracy over last 5 sessions for bag mode
    user = data.username
    numSeshes = 5
    xData = [i for i in range(1,6)]
    yData = []
    userHistory = data.allUsers[user][1]
    if userHistory == None: return
    for line in userHistory.splitlines():
        if line.startswith("Accuracy:"):
            stat = float(line[-4:])
            yData.append(stat)
    while len(yData) < numSeshes:
        yData.insert(0,0)
    lineplot(data,xData,yData,"Session #","Accuracy","Accuracy Over Time")

def getComboChart(data):
# displays user progress in accuracy over last 5 sessions for combo mode
    user = data.username
    numSeshes = 5
    xData = [i for i in range(1,6)]
    yData = []
    userHistory = data.allUsers[user][2]
    if userHistory == None: return
    for line in userHistory.splitlines():
        if line.startswith("Accuracy:"):
            stat = float(line[-4:])
            yData.append(stat)
    while len(yData) < numSeshes:
        yData.insert(0,0)
    lineplot(data,xData,yData,"Session #","Accuracy","Accuracy Over Time")

#### end keyPressed functions ####

def endScreenKeyPressed(event,data,prevMode):
# dispatches keyPressed to correct endscreen based on game mode
    prevMode = data.prevMode
    if prevMode == "sparSesh":
        sparEndKeyPressed(event,data)

    elif prevMode == "bagSesh":
        bagEndKeyPressed(event,data) 

    elif prevMode == "comboSesh":
        comboEndKeyPressed(event,data)

def sparEndKeyPressed(event,data):
    user = data.username
    if event.char == "m":
        sendSparMail(data)
    elif event.char == "s": # save results to usernameSpar.txt
        fullFileName = data.username+"Spar.txt"
        if data.allUsers[user][0] == None: # user's first time sparring
            # put the string in dictionary index 0:spar, 1:bag, 2:combo
            data.allUsers[user][0] = writeSparText(data)
                      
        else: # user has sparred before
            
            data.allUsers[user][0] = readFile(fullFileName)+writeSparText(data)
            
            # wipes oldest session
            sessionInfoLength = 7
            numSessionsStored = 5
            listForm = data.allUsers[user][0].splitlines()
            if len(listForm) > sessionInfoLength*numSessionsStored:
                listForm = listForm[sessionInfoLength:]
                
        # puts string in file
        fileContents = data.allUsers[user][0]
        writeFile(fullFileName,fileContents)
    elif event.char == "p":
        getSparChart(data)
    elif event.char == "h":
        data.hiScoreShowing = True
        

def bagEndKeyPressed(event,data):
    user = data.username
    if event.char == "m":
        sendBagMail(data) 
    elif event.char == "s": # save results to usernameSpar.txt
        if data.allUsers[user][1] == None: # user's first time sparring
            # put the string in dictionary index 0:spar, 1:bag, 2:combo
            data.allUsers[user][1] = writeBagText(data)
                      
        else: # user has done bagSesh before
            data.allUsers[user][1] = data.allUsers[user][1]+writeBagText(data)

            # wipes oldest session
            sessionInfoLength = 7
            numSessionsStored = 5
            listForm = data.allUsers[user][1].splitlines()
            if len(listForm) > sessionInfoLength*numSessionsStored:
                listForm = listForm[sessionInfoLength:]
                
        # puts string in file
        fullFileName = data.username+"Bag.txt"
        fileContents = data.allUsers[user][1]
        writeFile(fullFileName,fileContents)
    elif event.char == "p":
        getBagChart(data)
    elif event.char == "h":
        data.hiScoreShowing = True

def comboEndKeyPressed(event,data):
    user = data.username
    if event.char == "m":
        sendComboMail(data)
    elif event.char == "s": # save results to usernameSpar.txt
        if data.allUsers[user][2] == None: # user's first time sparring
            # put the string in dictionary index 0:spar, 1:bag, 2:combo
            data.allUsers[user][2] = writeComboText(data)
                      
        else: # user has done comboSesh before
            data.allUsers[user][2] = data.allUsers[user][2]+writeComboText(data)

            # wipes oldest session
            sessionInfoLength = 4
            numSessionsStored = 5
            listForm = data.allUsers[user][2].splitlines()
            if len(listForm) > sessionInfoLength*numSessionsStored:
                listForm = listForm[sessionInfoLength:]
                
        # puts string in file
        fullFileName = data.username+"Combo.txt"
        fileContents = data.allUsers[user][2]
        writeFile(fullFileName,fileContents)
    elif event.char == "p":
        getComboChart(data)
    elif event.char == "h":
        data.hiScoreShowing = True

def getBestAccuracy(contents):
    bestScore = 0
    currScore = 0
    for line in contents.splitlines():
        if line.startswith("Accuracy:"):
            currScore = float(line[-4:])
            if currScore > bestScore:
                bestScore = currScore
    return bestScore

def getHiScore(data,prevMode):
    bestUser = ""
    bestAccuracy = 0
    for filename in os.listdir():
        if filename.endswith(prevMode+".txt"):
            contents = readFile(filename)
            userHiScore = getBestAccuracy(contents)
            if userHiScore > bestAccuracy:
                bestAccuracy = userHiScore
                fileNameScraps = -1*len(prevMode+".txt")
                bestUser = filename[:fileNameScraps]

    data.hiScoreShowing = True
    return (bestUser,bestAccuracy)

def drawHiScore(canvas,data):
    if data.prevMode == "sparSesh":
        mode = "Spar"
    elif data.prevMode == "bagSesh":
        mode = "Bag"
    elif data.prevMode == "comboSesh":
        mode = "Combo"
    bestUser, bestAccuracy = getHiScore(data,mode)

    textSpace = 15
    canvas.create_text(textSpace,5*textSpace,
        text=bestUser+": "+str(bestAccuracy),
        fill="white",font="Courier 12",
        anchor="w")

def endScreenTimerFired(data,prevMode):
    prevMode = data.prevMode
    if prevMode == "splashScreen":
        pass
    elif prevMode == "sparSesh":
        pass
    elif prevMode == "bagSesh":
        pass   
    elif prevMode == "comboSesh":
        pass

def drawEndButtons(canvas,data,cX,cY):
    buttonWidth = data.mainButtonWidth
    buttonHeight = data.mainButtonHeight

    buttonAlign = 160
    canvas.create_rectangle(cX-buttonAlign-buttonWidth//2,cY-buttonHeight//2,
                            cX-buttonAlign+buttonWidth//2,cY+buttonHeight//2,
                            fill="PaleGreen3")
    canvas.create_text(cX-buttonAlign,cY,text="MAIN",
                        fill="gray25",font="Helvetica 24")
    
    canvas.create_rectangle(cX+buttonAlign-buttonWidth//2,cY-buttonHeight//2,
                            cX+buttonAlign+buttonWidth//2,cY+buttonHeight//2,
                            fill="dark green")
    canvas.create_text(cX+buttonAlign,cY,text="AGAIN",
                        fill="SlateGray2",font="Helvetica 24")

def drawKeyControlText(canvas,data):
# draws a menu of keys to press
    textSpace = 15
    emailText = "'m': mail results to Coach"
    saveText = "'s': save"
    progressText = "'p': track progress"
    hiScoreText = "'h': view high score"

    canvas.create_text(textSpace,textSpace,
        text=emailText,fill="white",font="Courier 12",anchor="w")
    canvas.create_text(textSpace,2*textSpace,
        text=saveText,fill="white",font="Courier 12",anchor="w")
    canvas.create_text(textSpace,3*textSpace,
        text=progressText,fill="white",font="Courier 12",anchor="w")
    canvas.create_text(textSpace,4*textSpace,
        text=hiScoreText,fill="white",font="Courier 12",anchor="w")

#### end redrawAll functions ####

def endScreenRedrawAll(canvas,data,prevMode):
    # sparbox in green (image)
    drawLogo(canvas,data,data.width//2,data.height//6)
    canvas.create_text(data.width//2,data.height//3,
                            text="PERFORMANCE",fill="SlateGray2",
                            font="Helvetica 36")

    drawKeyControlText(canvas,data)

    if data.hiScoreShowing:
        drawHiScore(canvas,data)

    prevMode = data.prevMode
    if prevMode == "sparSesh":
        sparEndRedrawAll(canvas,data)

    elif prevMode == "bagSesh":
        bagEndRedrawAll(canvas,data)

    elif prevMode == "comboSesh":
        comboEndRedrawAll(canvas,data)

def sparEndRedrawAll(canvas,data):
    textAlign = data.width//3
    canvas.create_text(data.width//2-textAlign,data.height//3,
                        text="USER",fill="dodger blue",
                        font="Helvetica 36")
    canvas.create_text(data.width//2+textAlign,data.height//3,
                        text="SPARBOT",fill="red3",
                        font="Helvetica 36")

    lineSpacing = 75
    canvas.create_text(data.width//2,data.height//3+lineSpacing,
                        text="Landed Strikes",fill="SlateGray2",
                        font="Courier 25")
    canvas.create_text(data.width//2-textAlign,data.height//3+lineSpacing,
                        text=str(data.newSparSesh.landedPunchCount),
                        fill="SlateGray2",
                        font="Courier 25")
    canvas.create_text(data.width//2+textAlign,data.height//3+lineSpacing,
                        text=str(data.newSparSesh.botLanded),
                        fill="SlateGray2",
                        font="Courier 25")

    canvas.create_text(data.width//2,data.height//3+2*lineSpacing,
                        text="Total Strikes",fill="SlateGray2",
                        font="Courier 25")
    canvas.create_text(data.width//2-textAlign,data.height//3+2*lineSpacing,
                        text=str(data.newSparSesh.totalPunches),
                        fill="SlateGray2",
                        font="Courier 25")
    canvas.create_text(data.width//2+textAlign,data.height//3+2*lineSpacing,
                        text=str(data.newSparSesh.botTotal),
                        fill="SlateGray2",
                        font="Courier 25")

    canvas.create_text(data.width//2,data.height//3+3*lineSpacing,
                        text="Accuracy",fill="SlateGray2",
                        font="Courier 25")
    canvas.create_text(data.width//2-textAlign,data.height//3+3*lineSpacing,
                        text="%0.2f" % (data.newSparSesh.userAccuracy),
                        fill="SlateGray2",
                        font="Courier 25")
    canvas.create_text(data.width//2+textAlign,data.height//3+3*lineSpacing,
                        text="%0.2f" % (data.newSparSesh.botAccuracy),
                        fill="SlateGray2",
                        font="Courier 25")

    mainX, mainY = data.width//2, data.height//3+4*lineSpacing
    drawEndButtons(canvas,data,mainX,mainY)

def bagEndRedrawAll(canvas,data):
    textAlign = data.width//20        
    lineSpacing = 40

    canvas.create_text(data.width//2-textAlign,data.height//3+lineSpacing,
                        text="Jabs",fill="SlateGray2",
                        font="Courier 25",anchor="e")
    canvas.create_text(data.width//2+textAlign,data.height//3+lineSpacing,
                        text=str(data.newBagSesh.numJabs),
                        fill="SlateGray2",
                        font="Courier 25",anchor="w")

    canvas.create_text(data.width//2-textAlign,data.height//3+2*lineSpacing,
                        text="Crosses",fill="SlateGray2",
                        font="Courier 25",anchor="e")
    canvas.create_text(data.width//2+textAlign,data.height//3+2*lineSpacing,
                        text=str(data.newBagSesh.numCrosses),
                        fill="SlateGray2",
                        font="Courier 25",anchor="w")

    canvas.create_text(data.width//2-textAlign,data.height//3+3*lineSpacing,
                        text="Hooks",fill="SlateGray2",
                        font="Courier 25",anchor="e")
    canvas.create_text(data.width//2+textAlign,data.height//3+3*lineSpacing,
                        text=str(data.newBagSesh.numRightHooks+\
                                data.newBagSesh.numLeftHooks),
                        fill="SlateGray2",
                        font="Courier 25",anchor="w")

    canvas.create_text(data.width//2-textAlign,data.height//3+4*lineSpacing,
                        text="Uppercuts",fill="SlateGray2",
                        font="Courier 25",anchor="e")
    canvas.create_text(data.width//2+textAlign,data.height//3+4*lineSpacing,
                        text=str(data.newBagSesh.numRightUppercuts+\
                                data.newBagSesh.numLeftUppercuts),
                        fill="SlateGray2",
                        font="Courier 25",anchor="w")

    canvas.create_text(data.width//2-textAlign,data.height//3+5*lineSpacing,
                        text="Total Strikes",fill="SlateGray2",
                        font="Courier 25",anchor="e")
    canvas.create_text(data.width//2+textAlign,data.height//3+5*lineSpacing,
                        text=str(data.newBagSesh.totalPunches),
                        fill="SlateGray2",
                        font="Courier 25",anchor="w")

    canvas.create_text(data.width//2-textAlign,data.height//3+6*lineSpacing,
                        text="Accuracy",fill="SlateGray2",
                        font="Courier 25",anchor="e")
    canvas.create_text(data.width//2+textAlign,data.height//3+6*lineSpacing,
                        text="%0.2f" % (data.newBagSesh.userAccuracy),
                        fill="SlateGray2",
                        font="Courier 25", anchor="w")

    mainX, mainY = data.width//2, data.height//3+7.5*lineSpacing
    drawEndButtons(canvas,data,mainX,mainY)

def comboEndRedrawAll(canvas,data):
    textAlign = data.width//20        
    lineSpacing = 75

    canvas.create_text(data.width//2-textAlign,data.height//3+lineSpacing,
                        text="Correct Punches",fill="SlateGray2",
                        font="Courier 25",anchor="e")
    canvas.create_text(data.width//2+textAlign,data.height//3+lineSpacing,
                        text=str(data.newComboSesh.correctPunchCount),
                        fill="SlateGray2",
                        font="Courier 25",anchor="w")

    canvas.create_text(data.width//2-textAlign,data.height//3+2*lineSpacing,
                        text="Total Punches",fill="SlateGray2",
                        font="Courier 25",anchor="e")
    canvas.create_text(data.width//2+textAlign,data.height//3+2*lineSpacing,
                        text=str(data.newComboSesh.totalPunches),
                        fill="SlateGray2",
                        font="Courier 25",anchor="w")

    canvas.create_text(data.width//2-textAlign,data.height//3+3*lineSpacing,
                        text="Accuracy",fill="SlateGray2",
                        font="Courier 25",anchor="e")
    canvas.create_text(data.width//2+textAlign,data.height//3+3*lineSpacing,
                        text="%0.2f"%(data.newComboSesh.userAccuracy),
                        fill="SlateGray2",
                        font="Courier 25",anchor="w")

    mainX, mainY = data.width//2, data.height//3+4*lineSpacing
    drawEndButtons(canvas,data,mainX,mainY)

###############################################
# used the run function as-is, from 15-112 notes
###############################################

def run(width=300, height=300):
#runs the clicker animation
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='black', width=0)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    root = Tk()
    root.resizable(width=False, height=False) # prevents resizing window
    init(data)
    # create the root and the canvas
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.configure(bd=0, highlightthickness=0)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(960,540)