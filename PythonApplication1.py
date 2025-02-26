import ast
from encodings import utf_8
from genericpath import isfile
import json
from tkinter import *
from tkinter import ttk 
from tkinter import colorchooser
import os
from os import listdir
from os.path import isfile, join
import platform
import tkinter
from tkinter.messagebox import showerror
from tkinter.font import Font
from turtle import width
from xmlrpc.client import boolean
dirname = os.path.dirname(__file__)
from functools import partial
from datetime import datetime
from difflib import SequenceMatcher
from PIL import Image, ImageEnhance, ImageTk
from pathlib import Path
import time
import statistics
import pygame
import math
import random
import serial
import threading
import colorsys

root = Tk()

font = Font(family="Hemi Head", size=13)
fontBold = Font(family="Hemi Head", size=13, weight='bold')
smallFont = Font(family="Hemi Head", size=11)
titleFont = Font(family="Hemi Head", size=45, weight="bold")
subTitleFont = Font(family="Hemi Head", size=35, weight="bold")
subSubTitleFont = Font(family="Hemi Head", size=25, weight="bold")

#spiritList = ("whisky", "whiskey", "vodka", "rum", "brandy", "gin", "tequila")

def on_escape(event=None):
    root.destroy()

def checkGarnishImagesExist(recipes):
    for recipe in recipes['recipies']:
        for garnish in str(recipe['garnish']).replace(" or ", " , ").split(','):
            temp = str(garnish).strip(' ').lstrip(' ').lower()
            if len(temp) <= 1:
                break
            if (temp[0] == 'a') & (temp[1] == ' '):
                temp = temp[2:]
            path = os.path.join(dirname, "images/garnishes/" + temp + ".png")
            if Path(path).is_file() == False:
                showerror("", "missing file: " + path)
                return False
    return True

def checkGlassImagesExist(recipes):
    for recipe in recipes['recipies']:
        path = os.path.join(dirname, "images/glasses/" + recipe['glassType'].split(' ')[0] + ".png")
        if Path(path).is_file() == False:
                showerror("", "missing file: " + path)
                return False
    return True

class Application(Frame):

    mainBGColour = '#111111'
    secondaryBGColour = '#333333'
    mainFGColour = '#EEEEEE'
    halfDisabledFGColour = '#444444'
    disabledFGColour = '#222222'
    mainBGColourDark = '#040404'
    secondaryBGColourDark = '#111111'
    mainFGColourDark = '#444444'
    halfDisabledFGColourDark = '#444444'
    disabledFGColourDark = '#222222'

    lastActive = datetime.now()

    seasons = set([])
    names = set([])
    spiritList = set([])
    ingredients = set([])
    ingredientsInStock = dict()
    ingredientsLEDPosition = dict()
    ingredientsColour = dict()
    ingredientsAlcohol = dict()
    ingredientsColourStrength = dict()
    ingredientsType = dict()
    glassTypes = set([])
    garnishes = ([])
    overflowImage = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/overflow.png")), Image.BICUBIC)
    overflowImageSmall = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/overflowSmall.png")), Image.BICUBIC)
    starImageOff = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/star.png")).resize((43, 43), Image.BICUBIC))
    starImageOn = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/starOn.png")).resize((43, 43), Image.BICUBIC))
    smallStar = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/starSmall.png")).resize((15, 15), Image.BICUBIC))
    smallStarDark = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/starSmallDark.png")).resize((15, 15), Image.BICUBIC))
    sortButton = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/sort.png")), Image.BICUBIC)
    recipeColours = dict()
    recipeButtonImages = dict()
    recipeButtonImagesHalfDisabled = dict()
    recipeButtonImagesDisabled = dict()
    recipeButtonImagesDark = dict()
    recipeButtonFiles = dict()
    recipeButtonFilesDark = dict()

    pygame.mixer.init() 
    pygame.mixer.music.set_volume(1.0)
    
    recipesScroll = 0
    firstTimeOpening = True
    recipeList = []
    filterValues = ('Any', 'Any', 'Any', '')
    alphabet = 'abcdefghijklmnopqrstuvwxyz'

    overlay = None
    overlayImage = None
    mainFrameCanvas = None

    networkSymbol = None

    def __init__(self, root):
        super().__init__(root, bg=self.mainBGColour)

        self.f = open(os.path.join(dirname, "recipes.JSON"), mode='r', encoding='utf-8-sig')
        self.recipes = json.load(self.f)

        self.f = open(os.path.join(dirname, "ingredients.JSON"), mode='r', encoding='utf-8-sig')
        tempIngredients = json.load(self.f)

        self.networkSymbol = Label(root, font=font, text='»', bg=self.mainBGColour, fg='#00DD00')
        self.networkSymbol.place(x=1004, y=-25)


        for ingredient in tempIngredients['ingredients']:
            self.ingredientsInStock.update({ingredient['name']:ingredient['inStock']})
            self.ingredientsLEDPosition.update({ingredient['name']:(ingredient['LEDStrip'], ingredient['LEDIndex'])})
            self.ingredientsColour.update({ingredient['name']:ingredient['Colour']})
            self.ingredientsAlcohol.update({ingredient['name']:ingredient['alcohol']})
            self.ingredientsColourStrength.update({ingredient['name']:ingredient['colourStrength']})
            self.ingredientsType.update({ingredient['name']:ingredient['type']})
            
        checkGarnishImagesExist(self.recipes)
        checkGlassImagesExist(self.recipes)

        self.getSearchables(self.recipes)

        self.currentPageIndex = 0
        self.pages = [self.Page0, self.Page1, self.Page2, self.Page3]

        self.mainFrame = self
        root.bind('<Motion>', self.mouseMove)
        root.bind('<ButtonRelease-1>', self.mouseUp)
        root.bind("<ButtonPress-1>", self.rootMouseDown)
        self.mainFrame.configure(bg=self.mainBGColour)
        self.mainFrame.pack(fill=BOTH, expand=True)
        self.mainFrame.columnconfigure(0, weight=1)
        self.mainFrame.rowconfigure(0, weight=1)

        self.mainFrameCanvas = Canvas(self.mainFrame, width=1024, height=600, bg=self.mainBGColour, highlightthickness=0)
        self.mainFrameCanvas.place(x=0, y=0)

        self.pages[self.currentPageIndex]()

        try:
            if(platform.system() == 'Windows'):
                self.SerialObj = serial.Serial('COM5')
            else:
                self.SerialObj = serial.Serial('/dev/ttyUSB0')

            self.SerialObj.baudrate = 115200
            self.SerialObj.bytesize = 8
            self.SerialObj.parity  ='N'
            self.SerialObj.stopbits = 1
            self.SerialObj.timeout = 5
            self.SerialObj.flush()
            time.sleep(1)

        except Exception as error:
           self.SerialObj = None
           print("Lighting Arduino not found! Error: ", error)
           self.networkSymbol.configure(fg='#DD0000')
           self.networkSymbol.place(y=0)

    scrolling = root
    mouseIsDown = False
    initialMouseY = 0
    scrollVelocity = 0
    hasScrolled = False
    def mouseMove(self, event):
        if self.mouseIsDown == True:
            scrollOffset = root.winfo_pointery() - self.initialMouseY
            if scrollOffset > 0:
                self.scrollVelocity = max(self.scrollVelocity, scrollOffset*1.5)
            else:
                self.scrollVelocity = min(self.scrollVelocity, scrollOffset*1.5)
            
            self.initialMouseY = root.winfo_pointery()
            self.scrolling.yview_scroll(int(scrollOffset)*-1, "units")
            self.moveScrollBar()

    def mouseDown(self, widget, isText, event):
        if(self.isDark == True):
            self.goLight()
            return
        self.lastActive = datetime.now()
        self.mouseIsDown = True
        self.scrolling = widget
        self.initialMouseY = root.winfo_pointery()
        self.scrollVelocity = 0
        self.hasScrolled = False
        root.after(150, self.setHasScrolled)

    def rootMouseDown(self, event):
        if(self.isDark == True):
            self.goLight()
            return
        self.lastActive = datetime.now()
        self.keyboardClickCheck(event)

    def setHasScrolled(self):
        if self.mouseIsDown == True:
            self.hasScrolled = True

    def mouseUp(self, event):
        if(self.isDark == True):
            self.goLight()
            return
        self.lastActive = datetime.now()
        self.mouseIsDown = False
        if (self.scrolling == self.midPayne) & (self.currentPageIndex == 0):
            self.clickRecipeCanvas(event)
        if (self.scrolling == self.midPayne) & (self.currentPageIndex == 2):
            self.clickIngredient(event)
        if(self.currentPageIndex == 3):
            self.releaseConfigCanvas(event)

    waitingForArduino = False
    thr = None
    currentMsg = ""
    def update(self):
        if self.scrollVelocity > 0:
            self.scrollVelocity = max(0, self.scrollVelocity - 1.5)
        elif self.scrollVelocity < 0:
            self.scrollVelocity = min(0, self.scrollVelocity + 1.5)
        now = datetime.now()
        dtString = now.strftime("%H:%M:%S")
        applicationInstance.setTimeString(dtString)
        root.after(16, self.update)

        if self.mouseIsDown == False:
            if self.scrolling != root:
                
                if (self.scrollVelocity == 0):
                    self.scrolling = root
                else:
                    self.scrolling.yview_scroll(int(self.scrollVelocity)*-1, "units")
                    self.moveScrollBar()
        
        sinceActive = now - self.lastActive
        if((sinceActive.seconds / 60) >= self.currentTimeout):
            if(self.isDark == False):
                self.goDark()
        
        if(self.waitingForArduino == False):
            if(len(self.ArduinoMessageQueue) > 0):
                self.currentMsg = self.ArduinoMessageQueue.pop(0)
                self.thr = threading.Thread(target=self.sendToArduinoAndGetResponse, args=(), kwargs={})
                self.waitingForArduino = True
                self.thr.start()
                

    def sendToArduinoAndGetResponse(self):
        
        self.networkSymbol.place(y=0)
        x = 0
        while x < 100:
            self.SerialObj.write(self.currentMsg.encode('utf-8'))
            print("Sending: " + str(self.currentMsg.encode('utf-8')))

            ReceivedString = self.SerialObj.readline()
            x = x + 1
            if(ReceivedString.__contains__(b"!") == False):
                break
                
        print("Recieve: " + str(ReceivedString))
        self.waitingForArduino = False
        self.networkSymbol.place(y=-25)


    isDark = False
    def goDark(self):
        self.homepage(False)
        self.getRecipesByCategory('Any')
        self.isDark = True

        self.titleLabel.configure(fg=self.mainFGColourDark)
        self.dateTimeLabel.configure(fg=self.mainFGColourDark)

        self.midPayne.configure(bg=self.mainBGColourDark)
        self.topPayne.configure(bg=self.mainBGColourDark)
        self.titleLabel.configure(bg=self.mainBGColourDark)
        self.dateTimeLabel.configure(bg=self.mainBGColourDark)
        self.upDownBtnCanvas.configure(bg=self.mainBGColourDark)
        self.midPayneLeftCanvas.configure(bg=self.mainBGColourDark)
        self.midPayneContainerContainer.configure(bg=self.mainBGColourDark)
        self.mainFrameCanvas.configure(bg=self.mainBGColourDark)
        self.dateTimeFrame.configure(bg=self.mainBGColourDark)
        self.recipeScrollBarCanvas.configure(bg=self.mainBGColourDark)

        for i in self.recipeButtons.keys():
            self.midPayne.itemconfig(self.recipeButtons[i], image=self.recipeButtonImagesDark.get(i))
            self.midPayne.itemconfig(self.recipeTexts[i], fill=self.mainFGColourDark)
        
        for j in self.recipeStars.values():
            for k in j:
                self.midPayne.itemconfig(k, image=self.smallStarDark)

        self.midPayneLeftCanvas.itemconfig(self.searchButton, image=self.imgSearchDark)
        self.midPayneLeftCanvas.itemconfig(self.seasonsButton, image=self.imgSeasonsDark)
        self.midPayneLeftCanvas.itemconfig(self.spiritsButton, image=self.imgSpiritsDark)
        self.midPayneLeftCanvas.itemconfig(self.glassTypesButton, image=self.imgGlassTypeDark)
        self.midPayneLeftCanvas.itemconfig(self.menuButton, image=self.imgMenuButtonDark)

        self.upDownBtnCanvas.itemconfig(self.upButton, image=self.upImageDark)
        self.upDownBtnCanvas.itemconfig(self.downButton, image=self.downImageDark)
        self.recipeScrollBarCanvas.itemconfig(self.bar, fill=self.mainFGColourDark, outline=self.mainFGColourDark)
        self.recipeScrollBarCanvas.itemconfig(self.barBack, fill=self.mainFGColourDark, outline=self.mainFGColourDark)

        self.titleFrame.configure(bg=self.mainBGColourDark)
        self.networkSymbol.configure(bg=self.mainBGColourDark)
        

        self.sendMessageToArduino("fadeOut")

    def goLight(self):
        if(self.currentPageIndex == 0):
            self.isDark = False
            self.lastActive = datetime.now()

            self.titleLabel.configure(fg=self.mainFGColour)
            self.dateTimeLabel.configure(fg=self.mainFGColour)

            self.midPayne.configure(bg=self.mainBGColour)
            self.topPayne.configure(bg=self.mainBGColour)
            self.titleLabel.configure(bg=self.mainBGColour)
            self.dateTimeLabel.configure(bg=self.mainBGColour)
            self.upDownBtnCanvas.configure(bg=self.mainBGColour)
            self.midPayneLeftCanvas.configure(bg=self.mainBGColour)
            self.midPayneContainerContainer.configure(bg=self.mainBGColour)
            self.mainFrameCanvas.configure(bg=self.mainBGColour)
            self.dateTimeFrame.configure(bg=self.mainBGColour)
            self.recipeScrollBarCanvas.configure(bg=self.mainBGColour)

            for i in self.recipeButtons.keys():
                if(self.recipeCanBeMade[i] == 2):
                    colour = self.mainFGColour
                    img = self.recipeButtonImages[i]
                elif(self.recipeCanBeMade[i] == 1):
                    colour = self.halfDisabledFGColourDark
                    img = self.recipeButtonImagesHalfDisabled[i]
                else:
                    colour = self.disabledFGColourDark
                    img = self.recipeButtonImagesDisabled[i]

                self.midPayne.itemconfig(self.recipeButtons[i], image=img)
                self.midPayne.itemconfig(self.recipeTexts[i], fill=colour)

            for j in self.recipeStars.keys():
                if(self.recipeCanBeMade[j] == 2):
                    for k in self.recipeStars.get(j):
                        self.midPayne.itemconfig(k, image=self.smallStar)
                else:
                    for k in self.recipeStars.get(j):
                        self.midPayne.itemconfig(k, image=self.smallStarDark)

            self.midPayneLeftCanvas.itemconfig(self.searchButton, image=self.imgSearch)
            self.midPayneLeftCanvas.itemconfig(self.seasonsButton, image=self.imgSeasons)
            self.midPayneLeftCanvas.itemconfig(self.spiritsButton, image=self.imgSpirits)
            self.midPayneLeftCanvas.itemconfig(self.glassTypesButton, image=self.imgGlassType)
            self.midPayneLeftCanvas.itemconfig(self.menuButton, image=self.imgMenuButton)

            self.upDownBtnCanvas.itemconfig(self.upButton, image=self.upImage)
            self.upDownBtnCanvas.itemconfig(self.downButton, image=self.downImage)
            self.recipeScrollBarCanvas.itemconfig(self.bar, fill=self.mainFGColour, outline=self.mainFGColour)
            self.recipeScrollBarCanvas.itemconfig(self.barBack, fill=self.mainFGColour, outline=self.mainFGColour)

            self.titleFrame.configure(bg=self.mainBGColour)
            self.networkSymbol.configure(bg=self.mainBGColour)

            self.sendMessageToArduino("fadeIn")

    def getSearchables(self, recipes):

        seasons2 = set([])
        names2 = set([])
        ingredients2 = set([])
        spirits = set([])
        glassTypes2 = set([])
        garnishes2 = ([])

        for recipe in recipes['recipies']:
            temp = recipe['season']
            if len(temp) > 1:
                seasons2.add(temp)

            temp = recipe['name']
            if len(temp) > 1:
                names2.add(temp)

            temp = recipe['glassType']
            if len(temp) > 1:
                glassTypes2.add(temp)

            for garnish in str.split(recipe['garnish'], ','):
                temp = str.strip(garnish, ' ')
                if len(temp) > 1:
                    garnishes2.append(str.lower(temp))
            
            for ingredient in recipe['ingredients']:
                if len(ingredient['name']) > 1:
                    ingredients2.add(ingredient['name'])

                    if(self.ingredientsType.get(ingredient['name'], "1") == "0"):
                        self.spiritList.add(ingredient['name'])
                        spirits.add(ingredient['name'])
                    
                    #temp = self.getIfIngredientIsSpirit(ingredient['name'])
                    #if temp != "":
                        #spirits.add(temp)
            self.recipeButtonImages[recipe['name']] = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/cocktails/buttons/" + recipe['ID'] + ".jpg")), Image.BICUBIC)
            self.recipeButtonImagesHalfDisabled[recipe['name']] = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/cocktails/buttons/halfDisabled/" + recipe['ID'] + ".jpg")), Image.BICUBIC)
            self.recipeButtonImagesDisabled[recipe['name']] = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/cocktails/buttons/disabled/" + recipe['ID'] + ".jpg")), Image.BICUBIC)
            self.recipeButtonImagesDark[recipe['name']] = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/cocktails/buttons/dark/" + recipe['ID'] + ".jpg")), Image.BICUBIC)

            self.seasons = sorted(seasons2)
            if self.seasons.__contains__('Any') == False:
                self.seasons.insert(0, 'Any')
            self.names = sorted(names2)
            self.ingredients = sorted(ingredients2)
            self.spirits = sorted(spirits)
            if self.spirits.__contains__('Any') == False:
                self.spirits.insert(0, 'Any')
            self.glassTypes = sorted(glassTypes2)
            if self.glassTypes.__contains__('Any') == False:
                self.glassTypes.insert(0, 'Any')
            self.garnishes = sorted(garnishes2)
    
    def recipeIngredientsMising(self, recipe):
        rtn = 0
        almostString = 'almost'
        for ingredient in recipe['ingredients']:
            if (self.ingredientsInStock.get(ingredient['name'], 0)) != '1':
                rtn = rtn + 1
                if(self.ingredientsType.get(ingredient['name']) != "3"):
                    almostString = ''
        return (rtn, almostString)

    keyboard = None
    keyCanvas = None
    keys = []
    keyTexts = []
    keyboardOpen = False
    searchTerm = StringVar()
    keyWidth = 75
    keyHeight = 50
    def openKeyboard(self):
        self.keyboard = Frame(self.mainFrameCanvas)
        self.keyboard.place(x=10, y=307)
        
        self.keyCanvas = Canvas(self.keyboard, width=1005, height=285, highlightthickness=0, bg='#222222')
        self.keyCanvas.pack(fill='both')

        self.searchTerm.trace("w", lambda name, index, mode, searchTerm=self.searchTerm: self.updateSearchBox(searchTerm))
        self.keyboardTextEntry = Entry(self.keyCanvas, font=subTitleFont, textvariable=self.searchTerm, bg=self.mainBGColour, bd=0, fg=self.mainFGColour)
        self.keyboardTextEntry.place(x=15, y=10, height=40, width=975)

        for i in range(0, 10):
            self.keys.append(self.keyCanvas.create_rectangle((i*self.keyWidth)+15, 55, ((i+1)*self.keyWidth)+15, self.keyHeight+55, fill=self.secondaryBGColour))
            self.keyTexts.append(self.keyCanvas.create_text(((i*self.keyWidth)+15)+(self.keyWidth/2), (self.keyHeight/2)+55, width=self.keyWidth, text=i, font=subSubTitleFont, fill=self.mainFGColour))

        for i in range(0, 13):
            self.keys.append(self.keyCanvas.create_rectangle((i*self.keyWidth)+15, self.keyHeight+55, ((i+1)*self.keyWidth)+15, (self.keyHeight*2)+55, fill=self.secondaryBGColour))
            self.keyTexts.append(self.keyCanvas.create_text(((i*self.keyWidth)+15)+(self.keyWidth/2), self.keyHeight+(self.keyHeight/2)+55, width=self.keyWidth, text=self.alphabet[i], font=subSubTitleFont, fill=self.mainFGColour))
            self.keys.append(self.keyCanvas.create_rectangle((i*self.keyWidth)+15, (self.keyHeight*2)+55, ((i+1)*self.keyWidth)+15, (self.keyHeight*3)+55, fill=self.secondaryBGColour))
            self.keyTexts.append(self.keyCanvas.create_text(((i*self.keyWidth)+15)+(self.keyWidth/2), (self.keyHeight*2)+(self.keyHeight/2)+55, width=self.keyWidth, text=self.alphabet[i+13], font=subSubTitleFont, fill=self.mainFGColour))
        
        self.keys.append(self.keyCanvas.create_rectangle(self.keyWidth+15,  (self.keyHeight*3)+55, (self.keyWidth*3)+15,  (self.keyHeight*4)+55, fill=self.secondaryBGColour))
        self.keyTexts.append(self.keyCanvas.create_text((self.keyWidth*2)+15, (self.keyHeight*3)+(self.keyHeight/2)+55, width=150, text='Delete', font=subSubTitleFont, fill=self.mainFGColour))

        self.keys.append(self.keyCanvas.create_rectangle((self.keyWidth*4)+15,  (self.keyHeight*3)+55, (self.keyWidth*9)+15,  (self.keyHeight*4)+55, fill=self.secondaryBGColour))
        self.keyTexts.append(self.keyCanvas.create_text((self.keyWidth*6.5)+15, (self.keyHeight*3)+(self.keyHeight/2)+55, width=375, text='Space', font=subSubTitleFont, fill=self.mainFGColour))

        self.keys.append(self.keyCanvas.create_rectangle((self.keyWidth*10)+15,  (self.keyHeight*3)+55, (self.keyWidth*12)+15,  (self.keyHeight*4)+55, fill=self.secondaryBGColour))
        self.keyTexts.append(self.keyCanvas.create_text((self.keyWidth*11)+15, (self.keyHeight*3)+(self.keyHeight/2)+55, width=150, text='Clear', font=subSubTitleFont, fill=self.mainFGColour))
        Misc.lift(self.keyboard)
        self.keyboardOpen = True

    def keyboardClickCheck(self, event):
        if(self.keyboardOpen == True):
            if(event.widget == self.keyCanvas):

                if((event.y > 55) & (event.y <= (self.keyHeight)+55) & (event.x > 15) & (event.x < (self.keyWidth * 10)+15)):
                    self.searchTerm.set(self.searchTerm.get() + str(math.floor((event.x - 15) / self.keyWidth)))
                elif((event.y > self.keyHeight+55) & (event.y <= (self.keyHeight*2)+55) & (event.x > 15) & (event.x < (self.keyWidth * 13)+15)):
                    self.searchTerm.set(self.searchTerm.get() + self.alphabet[math.floor((event.x - 15) / self.keyWidth)])
                elif((event.y > (self.keyHeight*2)+55) & (event.y <= (self.keyHeight*3)+55) & (event.x > 15) & (event.x < (self.keyWidth * 13)+15)):
                    self.searchTerm.set(self.searchTerm.get() + self.alphabet[(math.floor((event.x - 15) / self.keyWidth)) + 13])
                elif((event.y > (self.keyHeight*3)+55) & (event.y <= (self.keyHeight*4)+55)):
                    if((event.x > self.keyWidth+15) & (event.x <= (self.keyWidth*3)+15)):
                        self.searchTerm.set(self.searchTerm.get()[:-1])
                        if(len(self.searchTerm.get()) <= 0):
                            self.midPayneLeftCanvas.itemconfig(self.searchButton, image=self.imgSearchOn)
                    elif((event.x > (self.keyWidth*4)+15) & (event.x <= (self.keyWidth*9)+15)):
                        self.searchTerm.set(self.searchTerm.get() + ' ')
                    elif((event.x > (self.keyWidth*10)+15) & (event.x <= (self.keyWidth*12)+15)):
                        self.searchTerm.set('')
                        self.closeKeyboard()
                self.keyboardTextEntry.icursor(len(self.searchTerm.get()))

        if(self.currentPageIndex == 0):
            if(self.searchTerm.get() != ''):
                self.setCurrentFilter('search')
                self.midPayneLeftCanvas.itemconfig(self.seasonsButton, image=self.imgSeasons)
                self.midPayneLeftCanvas.itemconfig(self.spiritsButton, image=self.imgSpirits)
                self.midPayneLeftCanvas.itemconfig(self.glassTypesButton, image=self.imgGlassType)
            else:
                if(self.currentFilter == 'search'):
                    self.setCurrentFilter('')
                
                

    def closeKeyboard(self):
        if(self.keyboard != None):
            self.keyboard.place_forget()
            self.keyboard = None
            self.keyCanvas = None
            root.focus()
            self.keyboardOpen = False
            self.midPayneLeftCanvas.itemconfig(self.searchButton, image=self.imgSearch)
            #self.currentFilter = ''

    def getRecipesByCategory(self, season):
        self.recipeList = []
        for recipe in self.recipes['recipies']:
            if (recipe['season'] == season) | (season == 'None') | (season == 'Any'):
                self.recipeList.append(recipe)
        self.addRecipeButtons(self.recipeList)


    def getRecipesBySpirit(self, spirit):
        self.recipeList = []
        for recipe in self.recipes['recipies']:
            for ing in recipe['ingredients']:
                if str(ing['name']).lower().__contains__(spirit.lower()) | (spirit == 'Any'):
                    self.recipeList.append(recipe)
                    break
        self.addRecipeButtons(self.recipeList)

    def getRecipesByGlassType(self, glassType):
        self.recipeList = []
        for recipe in self.recipes['recipies']:
            if (recipe['glassType'] == glassType) | (glassType == 'Any'):
                self.recipeList.append(recipe)
        self.addRecipeButtons(self.recipeList)

    def updateSearchBox(self, searchTerm):
        if(searchTerm.get() != ''):
            self.filterValues = ('Any', 'Any', 'Any', searchTerm.get())
        else:
            self.filterValues = (self.filterValues[0], self.filterValues[1], self.filterValues[2], '')
        self.recipeList = []
        search = str.lower(str(searchTerm.get()))
        for recipe in self.recipes['recipies']:
            recipeNameString = str.lower(recipe['name'][:len(search)])
            ratio = SequenceMatcher(None, recipeNameString, search).ratio()
            if (ratio > 0.8):
                self.recipeList.append(recipe)
        self.addRecipeButtons(self.recipeList)

    def orderRecipeListByInStock(self, recipes):
        RecipeListInStock = []
        RecipeListNotInStock = []
        for recipe in recipes:
            if self.recipeIngredientsMising(recipe)[0] == 0:
                RecipeListInStock.append(recipe)
            else:
                RecipeListNotInStock.append(recipe)
        return (RecipeListInStock, RecipeListNotInStock)

    def getNormalizedQuantity(self, quant, unit):

        if(unit == 'oz'):
            num = 0.1
            for i in str(quant):
                if(i.isdigit()):
                    num += float(i)
                elif(i == '½'):
                    num += 0.5
                elif(i == '¼'):
                    num += 0.25
                elif(i == '¾'):
                    num += 0.75
                elif(i == '⅓'):
                    num += 0.33
                elif(i == '⅔'):
                    num += 0.66
                elif(i == '⅛'):
                    num += 0.125
                elif(i == '⅜'):
                    num += 0.375
                elif(i == '⅝'):
                    num += 0.625
                elif(i == '⅞'):
                    num += 0.875
            return float(num)
        return 0.5

    def ingredientColorNormalizedVibrancy(self, colour):
        colour = HexToRGB(colour)
        return max(min((statistics.stdev(colour) / 128), 1.0), 0.1)

    def getRecipeColour(self, recipe):
        print("")
        RGB = [0, 0, 0]
        ingredientsCount = 0
        d = dict()

        for ingredient in recipe['ingredients']:
            strength = 0.05
            if(self.ingredientsColour.get(ingredient['name'], '#000000')[1:] != "000000"):
                match self.ingredientsType.get(ingredient['name']):
                    case "0":
                        strength = 0.75
                    case "1":
                        strength = 0.75
                    case "2":
                        strength = 1
                    case "3":
                        strength = 0.15

                strength = strength * self.getNormalizedQuantity(ingredient['quantity'], ingredient['unit'])
                vibrancy = self.ingredientColorNormalizedVibrancy(self.ingredientsColour.get(ingredient['name']))
                strength = strength * vibrancy
                match self.ingredientsColourStrength.get(ingredient['name']):
                    case "0":
                        strength = strength * 0.1
                    case "1":
                        strength = strength * 0.4
                    case "2":
                        strength = strength * 1
                #strength = strength * (int(self.ingredientsColourStrength.get(ingredient['name'])) + 1) / 3
                alteredSaturation = HexSetSaturation(self.ingredientsColour.get(ingredient['name']), vibrancy)
                d[alteredSaturation[1:]] = strength


        d_items = sorted(d.items())
        tot_weight = sum(d.values())
        red = int(sum([int(k[:2], 16)*v for k, v in d_items])/tot_weight)
        green = int(sum([int(k[2:4], 16)*v for k, v in d_items])/tot_weight)
        blue = int(sum([int(k[4:6], 16)*v for k, v in d_items])/tot_weight)
        zpad = lambda x: x if len(x)==2 else '0' + x

        #return HexSetSaturation("#" + zpad(hex(red)[2:]) + zpad(hex(green)[2:]) + zpad(hex(blue)[2:]), 1)
        return "#" + zpad(hex(red)[2:]) + zpad(hex(green)[2:]) + zpad(hex(blue)[2:])

    recipeButtons = dict()
    recipeTextBacks = dict()  
    recipeTexts = dict()  
    recipeStars = dict()
    recipeCanBeMade = dict()
    recipeButtonAreas = []
    recipeMissingIngredientsText = dict()  

    def sortRecipes(self, recipes):
        sortedRecipes = []
        if(self.currentSortIndex == 0): #name
            sortedRecipes = sorted(recipes, key=lambda x: x['name'], reverse=False)
        elif(self.currentSortIndex == 1): #rating
            sortedRecipes = sorted(recipes, key=lambda x: x['stars'], reverse=True)
        elif(self.currentSortIndex == 2): #lastOpened
            sortedRecipes = sorted(recipes, key=lambda x: x['lastAccessed'], reverse=True)
        elif(self.currentSortIndex == 3): #strength
            sortedRecipes = sorted(recipes, key=lambda x: x['strength'], reverse=True)
        return sortedRecipes

    
    def addRecipeButtons(self, recipes):
        self.recipeButtonAreas.clear()
        orderedRecipesInStock = self.sortRecipes(self.orderRecipeListByInStock(recipes)[0])
        orderedRecipesNotInStock = self.sortRecipes(self.orderRecipeListByInStock(recipes)[1])
        orderedRecipes = orderedRecipesInStock + orderedRecipesNotInStock


        for child in self.recipeButtons.values():
            self.midPayne.delete(child)
        for child in self.recipeTextBacks.values():
            self.midPayne.delete(child)
        for child in self.recipeTexts.values():
            self.midPayne.delete(child)
        for child in self.recipeMissingIngredientsText.values():
            self.midPayne.delete(child)
        for child in self.recipeStars.values():
            for star in child:
                self.midPayne.delete(star)
            
        self.recipeButtons.clear()

        self.w = 190
        self.h = 100
        self.rows = 1
        self.top = 5
        self.left = 5
        self.buttonImages = {};
        x = 0
        for recipe in orderedRecipes:
            if (x % 4 == 0) & (x > 0):
                self.left=5
                self.top = self.top + self.h + 10
                self.rows = self.rows + 1

            action_with_arg = partial(self.openRecipe, recipe)
            mouse_action_with_arg = partial(self.mouseDown, self.midPayne, False)
            

            missingIngredients = self.recipeIngredientsMising(recipe)
            if missingIngredients[0] == 0:
                colour = self.mainFGColour
                img = self.recipeButtonImages.get(recipe['name'])
                self.recipeCanBeMade[recipe['name']] = 2
                missingText = ''
            else:
                missingText = '-'+str(missingIngredients[0])

                if(missingIngredients[1] == 'almost'):
                    img = self.recipeButtonImagesHalfDisabled.get(recipe['name'])
                    colour = self.halfDisabledFGColour
                    self.recipeCanBeMade[recipe['name']] = 1
                else:
                    img = self.recipeButtonImagesDisabled.get(recipe['name'])
                    colour = self.disabledFGColour
                    self.recipeCanBeMade[recipe['name']] = 0

            self.recipeButtons[recipe['name']] = self.midPayne.create_image(self.left, self.top, anchor='nw', image=img)
            self.recipeTextBacks[recipe['name']] = self.midPayne.create_text(self.left + 17, self.top + 17, width=self.w-25, anchor='nw', justify=LEFT, font=fontBold, fill='#000000', text=recipe['name'])
            self.recipeTexts[recipe['name']] = self.midPayne.create_text(self.left + 15, self.top + 15, width=self.w-25, anchor='nw', justify=LEFT, font=fontBold, fill=colour, text=recipe['name']+' ('+recipe['strength']+')')
            self.recipeButtonAreas.append(((self.left, self.top, self.w, self.h), recipe))
            self.recipeMissingIngredientsText[recipe['name']] = self.midPayne.create_text(self.left + 170, self.top + 70, width=self.w-25, anchor='ne', justify=LEFT, font=fontBold, fill=colour, text=missingText)

            self.recipeStars[recipe['name']] = []
            if missingIngredients[0] == 0:
                for i in range(0, int(recipe['stars'])):
                    self.recipeStars[recipe['name']].append(self.midPayne.create_image((self.left+(i*17)+15), self.top+75, anchor='nw', image=self.smallStar))
            else:
                for i in range(0, int(recipe['stars'])):
                    self.recipeStars[recipe['name']].append(self.midPayne.create_image((self.left+(i*17)+15), self.top+75, anchor='nw', image=self.smallStarDark))

            self.left = self.left+self.w+10;
            x = x + 1
        self.midPayne.configure(scrollregion=(0, 0, ((self.w * 4) + 25), max((((self.h * self.rows) + (10 * (self.rows + 1)))-5), self.midPayneContainer.winfo_height())))


    def clickRecipeCanvas(self, event):
        x = event.x
        y = self.midPayne.canvasy(event.y)
        for btn in self.recipeButtonAreas:
            if ((x > btn[0][0]) & (x < btn[0][0] + btn[0][2])):
                if ((y > btn[0][1]) & (y < btn[0][1] + btn[0][3])):
                    self.openRecipe(btn[1])
                    return

    def setTimeString(self, timeString):
        if self.currentPageIndex == 0:
            self.dateTimeLabel.configure(text=timeString)
    
    def clickUpDownCanvas(self, event):
        print(event.y)
        if(self.isDark == True):
            self.goLight()
            return
        self.lastActive = datetime.now()
        if (event.x > 0 & event.x < 75):
            if((event.y > 10) & (event.y <= 85)):
                self.recipesMove(-315)
                return
            elif((event.y > 370) & (event.y <= 470)):
                self.recipesMove(315)
                return

    def holdUpDownCanvasScrollBar(self, event):
        ratio = self.midPayne.winfo_height() / (self.midPayne.bbox("all")[3] - self.midPayne.bbox("all")[1])
        location =  ((event.y-5) * (1 - ratio)) / 306
        self.recipeMoveTo(location, False)

    def clickUpDownCanvasScrollBar(self, event):
        ratio = self.midPayne.winfo_height() / (self.midPayne.bbox("all")[3] - self.midPayne.bbox("all")[1])
        location =  ((event.y-5) * (1 - ratio)) / 306
        self.recipeMoveTo(location)

    def clickLeftButtonCanvas(self, event):
        if(self.isDark == True):
            self.goLight()
            return
        self.lastActive = datetime.now()
        if((event.y > 10) & (event.y <= 85)):
            self.openSearch()
        elif((event.y > 125) & (event.y <= 200)):
            self.openSeasons()
        elif((event.y > 200) & (event.y <= 275)):
            self.openSpirits()
        elif((event.y > 275) & (event.y <= 350)):
            self.openGlassTypes()
        elif((event.y > 390) & (event.y <= 465)):
            self.openMenu()

    def openSearch(self):
        if(self.pickerCanvas != None):
            self.closePickerBox('search')
            self.pickerType = ''

        if(self.keyboard == None):
            self.openKeyboard()
            self.midPayneLeftCanvas.itemconfig(self.searchButton, image=self.imgSearchOn)
        else:
            #self.searchTerm.set('')
            self.closeKeyboard()
            self.midPayneLeftCanvas.itemconfig(self.searchButton, image=self.imgSearch)

    def pickerClick(self, options, itemWidth, event):
        col = math.floor(event.x / itemWidth)
        if(((math.floor(event.y / 45))+(col*10)) >= len(options)):
            return

        self.pickerString.set(options[(math.floor(event.y / 45))+(col*10)])

        if(self.pickerType == 'seasons'):
            self.pickCategory()
            self.closePickerBox('seasons')
        elif(self.pickerType == 'spirits'):
            self.pickSpirit()
            self.closePickerBox('spirits')
        elif(self.pickerType == 'glassTypes'):
            self.pickGlassType()
            self.closePickerBox('glassTypes')
        elif(self.pickerType == 'menu'):
            self.pickMenu()
        

    pickerCanvas = None
    pickerType = ''
    pickerString = None
    menuCheckImage = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/menuUnchecked.png")).resize((30, 30), Image.BICUBIC))
    menuCheckImageChecked = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/menuChecked.png")).resize((30, 30), Image.BICUBIC))
    def openPickerBox(self, options, XPos, YPos, string):
        if(self.keyboard != None):
            self.searchTerm.set('')
            self.closeKeyboard()
            self.midPayneLeftCanvas.itemconfig(self.searchButton, image=self.imgSearch)

        self.pickerString = string
        self.pickerCanvas = Canvas(self.mainFrameCanvas, width=261, height=400, bg='#000000', highlightthickness=0)
        itemWidth = 260
        action_with_arg = partial(self.pickerClick, options, itemWidth)
        self.pickerCanvas.bind('<ButtonPress-1>', action_with_arg)
        x = 0
        y = 0
        
        cols = 1
        for item in options:
            self.pickerCanvas.create_rectangle((x*itemWidth)+(x*5), (y*45), ((x*itemWidth)+(x*5))+itemWidth, ((y*45)+40), fill='#222222')
            if(item.__contains__('|') == True):
                self.pickerCanvas.create_text(((x*itemWidth)+(x*5))+40, (y*45) + 20, width=itemWidth, anchor='w', fill=self.mainFGColour, font=font, text=item.split('|')[0])
                if(item.split('|')[1] == 'ON'):
                    self.pickerCanvas.create_image(((x*itemWidth)+(x*5))+5, (y*45) + 5, anchor='nw', image=self.menuCheckImageChecked)
                else:
                    self.pickerCanvas.create_image(((x*itemWidth)+(x*5))+5, (y*45) + 5, anchor='nw', image=self.menuCheckImage)
            else:
                self.pickerCanvas.create_text(((x*itemWidth)+(x*5))+40, (y*45) + 20, width=itemWidth, anchor='w', fill=self.mainFGColour, font=font, text=item.title())
            y = y + 1
            if(y >= 10):
                x = x + 1
                y = 0
                cols = cols + 1
        
        self.pickerCanvas.configure(height=(min((x*10)+y, 10)*45)-4, width=((itemWidth*cols + ((cols-1)*5))+1))
        self.pickerCanvas.place(x=XPos, y=YPos)

    def closePickerBox(self, opening=None):
        if(self.pickerCanvas != None):
            self.pickerCanvas.place_forget()
            self.pickerCanvas = None
            self.midPayneLeftCanvas.itemconfig(self.menuButton, image=self.imgMenuButton)
            self.pickerType = ''
        if(opening != 'search'):
            if(self.filterValues[3] == ''):
                self.midPayneLeftCanvas.itemconfig(self.searchButton, image=self.imgSearch)
        if(opening != 'seasons'):
            if(self.filterValues[0] == 'Any'):
                self.midPayneLeftCanvas.itemconfig(self.seasonsButton, image=self.imgSeasons)
        if(opening != 'spirits'):
            if(self.filterValues[1] == 'Any'):
                self.midPayneLeftCanvas.itemconfig(self.spiritsButton, image=self.imgSpirits)
        if(opening != 'glassTypes'):
            if(self.filterValues[2] == 'Any'):
                self.midPayneLeftCanvas.itemconfig(self.glassTypesButton, image=self.imgGlassType)

    currentFilter = ''
    def setCurrentFilter(self, newFilter):
        if(self.currentPageIndex != 0):
            return
        currentFilter = newFilter

        if(newFilter == 'search'):
            self.midPayneLeftCanvas.itemconfig(self.searchButton, image=self.imgSearchOpen)
        if(newFilter == 'seasons'):
            self.midPayneLeftCanvas.itemconfig(self.seasonsButton, image=self.imgSeasonsOpen)
        if(newFilter == 'spirits'):
            self.midPayneLeftCanvas.itemconfig(self.spiritsButton, image=self.imgSpiritsOpen)
        if(newFilter == 'glassTypes'):
            self.midPayneLeftCanvas.itemconfig(self.glassTypesButton, image=self.imgGlassTypeOpen)

    categoryString = StringVar()
    def openSeasons(self):
        formerPickerType = self.pickerType
        if(self.pickerCanvas != None):
            self.closePickerBox()

        if(formerPickerType != 'seasons'):
            self.openPickerBox(self.seasons, 110, 130, self.categoryString)
            self.pickerType = 'seasons'
            self.midPayneLeftCanvas.itemconfig(self.seasonsButton, image=self.imgSeasonsOn)
        else:
            self.pickerType = ''
            if(self.filterValues[0] == 'Any'):
                self.midPayneLeftCanvas.itemconfig(self.seasonsButton, image=self.imgSeasons)
            else:
                self.midPayneLeftCanvas.itemconfig(self.seasonsButton, image=self.imgSeasonsOpen)

    ingredientsString = StringVar() 
    def openSpirits(self):
        formerPickerType = self.pickerType
        if(self.pickerCanvas != None):
            self.closePickerBox()

        if(formerPickerType != 'spirits'):
            self.openPickerBox(self.spirits, 110, 95, self.ingredientsString)
            self.pickerType = 'spirits'
            self.midPayneLeftCanvas.itemconfig(self.spiritsButton, image=self.imgSpiritsOn)
        else:
            self.pickerType = ''
            if(self.filterValues[1] == 'Any'):
                self.midPayneLeftCanvas.itemconfig(self.spiritsButton, image=self.imgSpirits)
            else:
                self.midPayneLeftCanvas.itemconfig(self.spiritsButton, image=self.imgSpiritsOpen)

    glassTypeString = StringVar() 
    def openGlassTypes(self):
        formerPickerType = self.pickerType
        if(self.pickerCanvas != None):
            self.closePickerBox()

        if(formerPickerType != 'glassTypes'):
            self.openPickerBox(self.glassTypes, 110, 210, self.glassTypeString)
            self.pickerType = 'glassTypes'
            self.midPayneLeftCanvas.itemconfig(self.glassTypesButton, image=self.imgGlassTypeOn)
        else:
            self.pickerType = ''
            if(self.filterValues[2] == 'Any'):
                self.midPayneLeftCanvas.itemconfig(self.glassTypesButton, image=self.imgGlassType)
            else:
                self.midPayneLeftCanvas.itemconfig(self.glassTypesButton, image=self.imgGlassTypeOpen)

    
    menuString = StringVar()
    sortingOptions = ['Name', 'Rating', 'Last Opened', 'strength']
    currentSortIndex = 0
    def openMenu(self):
        overrideStr = '|OFF'
        if(self.MainLightsOverride == True):
            overrideStr = '|ON'
        menuItems = ['Ingredients Manager', 'Configuration Page', 'Lights Override'+overrideStr, 'Sort by: '+self.sortingOptions[self.currentSortIndex]]

        formerPickerType = self.pickerType
        if(self.pickerCanvas != None):
            self.closePickerBox()

        if(formerPickerType != 'menu'):
            self.openPickerBox(menuItems, 110, 395, self.menuString)
            self.pickerType = 'menu'
            self.midPayneLeftCanvas.itemconfig(self.menuButton, image=self.imgMenuButtonOn)
        else:
            self.pickerType = ''

    #homepage
    def Page0(self):
        self.scrolling = root
        self.topPayne = Canvas(self.mainFrameCanvas, highlightthickness=0, bg=self.mainBGColour, width=1024, height=70);
        self.titleFrame = Frame(self.topPayne, bg=self.mainBGColour)
        self.titleLabel = Label(self.titleFrame, font=titleFont, text="Cocktails 'n shit", bg=self.mainBGColour, fg=self.mainFGColour)
        self.titleLabel.pack(side=BOTTOM, padx=20)
        self.titleFrame.pack(side=LEFT, fill='y', padx=10, pady=0)

        self.dateTimeFrame = Frame(self.topPayne, bg=self.mainBGColour)
        self.dateTimeLabel = Label(self.dateTimeFrame, font=subSubTitleFont, anchor='nw', width=7, bg=self.mainBGColour, fg=self.mainFGColour, text="00:00:00")
        self.dateTimeLabel.pack(side=TOP)
        self.dateTimeFrame.pack(side=RIGHT, fill='y', padx=35, pady=10)
        self.topPayne.pack(fill='x')
        self.topPayne.pack_propagate(0)

        self.midPayneContainerContainer = Frame(self.mainFrameCanvas, bg=self.mainBGColour)
        self.midPayneContainer = Frame(self.midPayneContainerContainer)
        self.midPayne = Canvas(self.midPayneContainer, highlightthickness=0, bg=self.mainBGColour, scrollregion="0 0 2000 1000", width=805, height=500)
        self.midPayne.configure(yscrollincrement='1')
        mouse_action_with_arg = partial(self.mouseDown, self.midPayne, False)
        self.midPayne.bind('<ButtonPress-1>', mouse_action_with_arg)
        self.midPayne.bind('<Leave>', self.mouseUp)

        self.midPayne.bind("<MouseWheel>", self.scrollMainPageRecipes)
        self.midPayne.pack()

        self.upDownBtnCanvas = Canvas(self.midPayneContainerContainer, bg=self.mainBGColour, borderwidth=0, highlightthickness=0, width=80)
        self.upDownBtnCanvas.bind("<ButtonPress-1>", self.clickUpDownCanvas)
        self.upImage = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/up.png")), Image.BICUBIC)
        self.upImageDark = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/upDark.png")), Image.BICUBIC)
        self.upButton = self.upDownBtnCanvas.create_image(0, 6, anchor='nw', image=self.upImage)
        self.downImage = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/down.png")), Image.BICUBIC)
        self.downImageDark = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/downDark.png")), Image.BICUBIC)
        self.downButton = self.upDownBtnCanvas.create_image(0, 395, anchor='nw', image=self.downImage)
        self.recipeScrollBarCanvas = Canvas(self.upDownBtnCanvas, bg=self.mainBGColour, borderwidth=0, highlightthickness=0, width=75, height=319)
        self.recipeScrollBarCanvas.bind("<B1-Motion>", self.holdUpDownCanvasScrollBar)
        self.recipeScrollBarCanvas.bind("<ButtonRelease-1>", self.clickUpDownCanvasScrollBar)
        self.barBack = self.recipeScrollBarCanvas.create_rectangle(37, 0, 38, 345, fill='#cccccc', outline='#cccccc')
        self.bar = self.recipeScrollBarCanvas.create_rectangle(27, 3, 47, 4, fill='#cccccc', outline='#cccccc')
        self.recipeScrollBarCanvas.pack(pady = 79)
        self.upDownBtnCanvas.pack(side=RIGHT, fill='y', padx=10)

        self.midPayneContainer.pack(side=RIGHT)
        
        self.midPayneLeftCanvas = Canvas(self.midPayneContainerContainer, bg=self.mainBGColour, borderwidth=0, highlightthickness=0, width=75, height=475)
        
        self.imgSearch = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/search.png")), Image.BICUBIC)
        self.imgSearchDark = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/searchDark.png")), Image.BICUBIC)
        self.imgSearchOn = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/search_on.png")), Image.BICUBIC)
        self.imgSearchOpen = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/search_open.png")), Image.BICUBIC)
        self.searchButton = self.midPayneLeftCanvas.create_image(0, 10, anchor='nw', image=self.imgSearch)

        self.imgSeasons = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/season.png")), Image.BICUBIC)
        self.imgSeasonsDark = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/seasonDark.png")), Image.BICUBIC)
        self.imgSeasonsOn = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/season_on.png")), Image.BICUBIC)
        self.imgSeasonsOpen = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/season_open.png")), Image.BICUBIC)
        self.seasonsButton = self.midPayneLeftCanvas.create_image(0, 125, anchor='nw', image=self.imgSeasons)

        self.imgSpirits = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/spirit.png")), Image.BICUBIC)
        self.imgSpiritsDark = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/spiritDark.png")), Image.BICUBIC)
        self.imgSpiritsOn = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/spirit_on.png")), Image.BICUBIC)
        self.imgSpiritsOpen = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/spirit_open.png")), Image.BICUBIC)
        self.spiritsButton = self.midPayneLeftCanvas.create_image(0, 200, anchor='nw', image=self.imgSpirits)

        self.imgGlassType = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/glassType.png")), Image.BICUBIC)
        self.imgGlassTypeDark = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/glassTypeDark.png")), Image.BICUBIC)
        self.imgGlassTypeOn = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/glassType_on.png")), Image.BICUBIC)
        self.imgGlassTypeOpen = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/glassType_open.png")), Image.BICUBIC)
        self.glassTypesButton = self.midPayneLeftCanvas.create_image(0, 275, anchor='nw', image=self.imgGlassType)

        self.imgMenuButton = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/menu.png")), Image.BICUBIC)
        self.imgMenuButtonDark = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/menuDark.png")), Image.BICUBIC)
        self.imgMenuButtonOn = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/menu_on.png")), Image.BICUBIC)
        self.menuButton = self.midPayneLeftCanvas.create_image(0, 390, anchor='nw', image=self.imgMenuButton)

        self.midPayneLeftCanvas.bind('<ButtonPress-1>', self.clickLeftButtonCanvas)
        self.midPayneLeftCanvas.pack(pady=5, padx=20, side=LEFT, anchor='nw')

        self.midPayneContainerContainer.pack(pady=5, side=RIGHT)


        if(self.firstTimeOpening == True):
            self.getRecipesByCategory('Any')
            self.firstTimeOpening = False
        else:
            self.addRecipeButtons(self.recipeList)
            self.categoryString.set(self.filterValues[0])
            self.ingredientsString.set(self.filterValues[1])
            self.glassTypeString.set(self.filterValues[2])
            self.searchTerm.set(self.filterValues[3])

    def clickTopPayne(self, event):
        if((event.y > 15) & (event.y <= 60)):
            if((event.x > 810) & (event.x <= 855) & (self.currentPageIndex == 1)):
                self.randomRecipe()
            elif((event.x > 880) & (event.x <= 1000)):
                self.homepage(True)

    #recipe page
    def Page1(self):
        self.scrolling = root
        self.topPayne = Canvas(self.mainFrameCanvas, highlightthickness=0, bg=self.mainBGColour, width=1050, height=75);

        self.topPayne.pack(side=TOP)
        self.topPayne.pack_propagate(0)

        self.imgShuffleButton = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/shuffle.png")), Image.BICUBIC)
        self.topPayne.create_image(820, 15, anchor='nw', image=self.imgShuffleButton)

        self.imgReturnButton = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/home.png")), Image.BICUBIC)
        self.topPayne.create_image(880, 15, anchor='nw', image=self.imgReturnButton)
        self.topPayne.bind('<ButtonPress-1>', self.clickTopPayne)

        self.middleContainer = Frame(self.mainFrameCanvas, bg=self.mainBGColour)

        self.leftPaynesContainer = Frame(self.middleContainer, bg=self.mainBGColour)
        self.bottomLeftPayneContainer = Frame(self.leftPaynesContainer, bg=self.mainBGColour)
        self.bottomLeftPayne = Canvas(self.bottomLeftPayneContainer, highlightthickness=0, bg=self.mainBGColour, scrollregion="0 0 2000 110", width=315, height=114)
        self.bottomLeftPayne.configure(yscrollincrement='1')
        self.bottomLeftPayne.bind("<MouseWheel>", self.scrollRecipeIngredients)
        self.cocktailIngredients = Canvas(self.bottomLeftPayne, width=300, height=110, bg=self.mainBGColour, highlightthickness=0)
        mouse_action_with_arg = partial(self.mouseDown, self.bottomLeftPayne, True)
        self.cocktailIngredients.bind('<ButtonPress-1>', mouse_action_with_arg)
        self.cocktailIngredients.bind('<Leave>', self.mouseUp)
        self.cocktailIngredients.bind("<MouseWheel>", self.scrollRecipeIngredients)
        self.bottomLeftPayne.create_window((9, 5), anchor=NW, window=self.cocktailIngredients)
        self.bottomLeftPayne.pack()

        self.overFlowContainerSmall = Canvas(self.bottomLeftPayneContainer, bg=self.mainBGColour, width=315, height=15, highlightthickness=0)
        self.overFlowContainerSmall.create_rectangle(0, 0, 315, 15, fill=self.mainFGColour, outline=self.mainFGColour)
        self.overFlowContainerSmall.create_rectangle(4, 0, 312, 15, fill=self.mainBGColour, outline=self.mainBGColour)
        self.overFlowContainerSmall.pack(side=BOTTOM)

        self.bottomLeftPayneContainer.pack(side=TOP, padx=0, pady=0)

        self.underLeftPayneContainer = Frame(self.leftPaynesContainer, bg=self.mainBGColour)
        self.underLeftPayne = Canvas(self.underLeftPayneContainer, highlightthickness=0, bg=self.mainBGColour, height=380, width=315)
        
        

        self.underLeftPayne.create_rectangle(0, 0, 315, 52, fill=self.mainFGColour, outline=self.mainFGColour)
        self.underLeftPayne.create_rectangle(4, 2, 312, 51, fill=self.mainBGColour, outline=self.mainBGColour)
        self.underLeftPayne.bind('<ButtonPress-1>', self.clickUnderLeftPayne)

        self.underLeftPayne.create_rectangle(0, 52, 315, 115, fill=self.mainFGColour, outline=self.mainFGColour)
        self.underLeftPayne.create_rectangle(4, 54, 312, 115, fill=self.mainBGColour, outline=self.mainBGColour)
        
        self.underLeftPayne.pack()
        self.underLeftPayne.pack_propagate(0)
        self.underLeftPayneContainer.pack(side=BOTTOM, padx=0, pady=0)

        self.leftPaynesContainer.pack(side=LEFT, padx=5)

        self.bottomRightPayneContainer = Frame(self.middleContainer, bg=self.mainBGColour)
        self.bottomRightPayne = Canvas(self.bottomRightPayneContainer, highlightthickness=0, bg=self.mainBGColour, scrollregion="0 0 2000 1000", width=700, height=475)
        self.bottomRightPayne.configure(yscrollincrement='1')
        self.bottomRightPayne.bind("<MouseWheel>", self.scrollRecipeSteps)
        #self.cocktailSteps = Text(self.bottomRightPayne, font=font, width=66, bg=self.mainBGColour, fg=self.mainFGColour, borderwidth=0, bd=0, wrap=WORD, cursor='arrow')
        self.cocktailSteps = Canvas(self.bottomRightPayne, width=665, height=440, bg=self.mainBGColour, highlightthickness=0)
        mouse_action_with_arg = partial(self.mouseDown, self.bottomRightPayne, True)
        self.cocktailSteps.bind('<ButtonPress-1>', mouse_action_with_arg)
        self.cocktailSteps.bind('<Leave>', self.mouseUp)
        self.cocktailSteps.bind("<MouseWheel>", self.scrollRecipeSteps)
        self.bottomRightPayne.create_window((5, 5), anchor=NW, window=self.cocktailSteps)
        self.bottomRightPayne.pack(padx=8, side=TOP)

        self.overFlowContainer = Canvas(self.bottomRightPayneContainer, bg=self.mainBGColour, width=700, height=30, highlightthickness=0)
        self.overFlowContainer.pack(padx=8, side=BOTTOM)

        self.bottomRightPayneContainer.pack(side=RIGHT, padx=5)

        self.middleContainer.pack(side=TOP)

        self.bottomPayneContainer = Frame(self.mainFrameCanvas, bg=self.mainBGColour)
        self.bottomPayne = Canvas(self.bottomPayneContainer, highlightthickness=0, bg=self.mainBGColour, width=1050, height=20);
        self.bottomPayne.pack()
        self.bottomPayneContainer.pack(side=BOTTOM)

    #ingredients page
    def Page2(self):
        self.scrolling = root
        self.topPayne = Canvas(self.mainFrameCanvas, highlightthickness=0, bg=self.mainBGColour, width=1024, height=70);
        self.titleFrame = Frame(self.topPayne, bg=self.mainBGColour)
        self.titleLabel = Label(self.titleFrame, font=titleFont, text="Ingredients", bg=self.mainBGColour, fg=self.mainFGColour)
        self.titleLabel.pack(side=TOP, padx=20)
        self.titleFrame.pack(side=LEFT, fill='y', padx=10, pady=0)

        self.imgReturnButton = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/home.png")), Image.BICUBIC)
        self.topPayne.create_image(880, 15, anchor='nw', image=self.imgReturnButton)
        self.topPayne.bind('<ButtonPress-1>', self.clickTopPayne)

        self.topPayne.pack(fill='x')
        self.topPayne.pack_propagate(0)

        self.topMidPayneCanvas = Canvas(self.mainFrameCanvas, width='1024', height='50', highlightthickness=0, bg=self.mainBGColour)
        self.topMidPayneCanvas.create_text(150, 30, width=90, font=font, anchor='n', fill=self.mainFGColour, text='In Stock')
        self.topMidPayneCanvas.create_text(300, 30, width=90, font=font, anchor='n', fill=self.mainFGColour, text='Name')
        self.topMidPayneCanvas.create_text(750, 30, width=90, font=font, anchor='n', fill=self.mainFGColour, text='Colour')
        self.topMidPayneCanvas.create_text(850, 30, width=90, font=font, anchor='n', fill=self.mainFGColour, text='LED Strip')
        self.topMidPayneCanvas.create_text(950, 30, width=90, font=font, anchor='n', fill=self.mainFGColour, text='LED Index')
        self.topMidPayneCanvas.pack(pady=10)

        self.midPayneContainerContainer = Frame(self.mainFrameCanvas, bg=self.mainBGColour)
        self.midPayneContainer = Frame(self.midPayneContainerContainer)
        self.leftPayne = Canvas(self.midPayneContainer, highlightthickness=0, bg=self.mainBGColour, width=100, height=442)
        self.leftPayne.pack(side=LEFT)
        self.midPayne = Canvas(self.midPayneContainer, highlightthickness=0, bg=self.mainBGColour, scrollregion="0 0 2000 1000", width=900, height=442)
        self.midPayne.configure(yscrollincrement='1')
        mouse_action_with_arg = partial(self.mouseDown, self.midPayne, False)
        self.midPayne.bind('<ButtonPress-1>', mouse_action_with_arg)
        self.midPayne.bind('<Leave>', self.mouseUp)
       
        self.leftPayne.create_rectangle(0, 4, 75, 442, fill='#0000ff')
        for i in range(26):
            self.leftPayne.create_rectangle(0, (i*17), 90, ((i*17)+17), fill='#222222')
            self.leftPayne.create_text(45, (i*17)+8, width=90, font=smallFont, fill=self.mainFGColour, text=self.alphabet[i])
        self.leftPayne.bind('<ButtonPress-1>', self.clickAlphabet)

        x = 0
        self.itemHeight = 60
        self.itemSpacing = 10
        
        self.ingredientRows = dict()
        self.ingredientInStockClickAreas = []
        self.ingredientCheckBoxes = dict()
        self.ingredientLEDStripButtons = dict()
        self.ingredientLEDIndexButtons = dict()
        self.ingredientColourButtons = dict()
        self.ingredientsData = []

        itemYPos = 0
        self.unCheckImage = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/unCheck.png")), Image.BICUBIC)
        self.checkImage = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/check.png")), Image.BICUBIC)
        for ingredient in self.ingredients:
            if self.garnishes.__contains__(str.lower(str.rstrip(ingredient, 's'))) == False:

                checked = self.ingredientsInStock.get(ingredient, 0)
                ledStrip = self.ingredientsLEDPosition.get(ingredient, (0,0))[0]
                ledIndex = self.ingredientsLEDPosition.get(ingredient, (0,0))[1]
                colour = self.ingredientsColour.get(ingredient, '#ffffff')
                ingType = self.ingredientsType.get(ingredient, 3)
                alcohol = self.ingredientsAlcohol.get(ingredient, "1")
                colourStrength = self.ingredientsColourStrength.get(ingredient, "1")
                

                tpl = (ingredient, checked, ledStrip, ledIndex, colour, ingType, alcohol, colourStrength)
                self.ingredientsData.append(tpl)

                self.drawIngredientRow(ingredient, itemYPos, self.itemHeight)
                x = x + 1
                itemYPos = itemYPos + self.itemHeight + self.itemSpacing

        self.midPayne.configure(scrollregion=(0, 0, 1000, max(itemYPos, self.midPayneContainer.winfo_height())))
        self.midPayne.pack(side=RIGHT)

        self.midPayneContainer.pack(side=LEFT)
        self.midPayneContainerContainer.pack()

    timeoutBarRect = (320, 50, 720, 70)

    mainBrightnessBarRect = (320, 90, 720, 110)
    sideBrightnessBarRect = (320, 130, 720, 150)
    warmthBarRect = (320, 170, 720, 190)

    barLightsOnRect = (320, 210, 340, 230)
    screenLightsOnRect = (700, 210, 720, 230)
    mainLightsOnRect = (320, 250, 340, 270)

    currentTimeout = 5
    currentMainBrightnessPercent = 25
    currentSideBrightnessPercent = 25
    currentWarmthPercent = 75
    currentBarLightChecked = True
    currentScreenLightChecked = True
    currentMainLightChecked = True

    #config page
    def Page3(self):
        self.scrolling = root
        self.topPayne = Canvas(self.mainFrameCanvas, highlightthickness=0, bg=self.mainBGColour, width=1024, height=70);
        self.titleFrame = Frame(self.topPayne, bg=self.mainBGColour)
        self.titleLabel = Label(self.titleFrame, font=titleFont, text="Configuration", bg=self.mainBGColour, fg=self.mainFGColour)
        self.titleLabel.pack(side=TOP, padx=20)
        self.titleFrame.pack(side=LEFT, fill='y', padx=10, pady=0)

        self.imgReturnButton = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/home.png")), Image.BICUBIC)
        self.topPayne.create_image(880, 15, anchor='nw', image=self.imgReturnButton)
        self.topPayne.bind('<ButtonPress-1>', self.clickTopPayne)

        self.topPayne.pack(fill='x')
        self.topPayne.pack_propagate(0)

        self.midPayneContainer = Canvas(self.mainFrameCanvas, width=1004, height=500, bg='#222222', highlightthickness=0)
        self.midPayneContainer.bind('<ButtonPress-1>', self.clickConfigCanvas)
        self.midPayneContainer.bind('<Motion>', self.dragConfigCanvas)

        self.midPayneContainer.create_text(self.timeoutBarRect[0]-10, self.timeoutBarRect[1], width=250, anchor='ne', font=font, fill=self.mainFGColour, text='Sleep:')
        self.midPayneContainer.create_rectangle(self.timeoutBarRect[0]-2, self.timeoutBarRect[1]-2, self.timeoutBarRect[2]+2, self.timeoutBarRect[3]+2, fill='#000000', outline='#000000')
        self.timeoutBar = self.midPayneContainer.create_rectangle(self.getBarActualWidth(self.timeoutBarRect, self.currentTimeout, 60), fill='#cccccc', outline='#cccccc')
        self.timeoutText = self.midPayneContainer.create_text(self.timeoutBarRect[0]+410, self.timeoutBarRect[1], width=250, anchor='nw', font=font, fill=self.mainFGColour, text=str(self.currentTimeout)+' Minutes')

        self.midPayneContainer.create_text(self.mainBrightnessBarRect[0]-10, self.mainBrightnessBarRect[1], width=250, anchor='ne', font=font, fill=self.mainFGColour, text='Main brightness:')
        self.midPayneContainer.create_rectangle(self.mainBrightnessBarRect[0]-2, self.mainBrightnessBarRect[1]-2, self.mainBrightnessBarRect[2]+2, self.mainBrightnessBarRect[3]+2, fill='#000000', outline='#000000')
        self.mainBrightnessBar = self.midPayneContainer.create_rectangle(self.getBarActualWidth(self.mainBrightnessBarRect, self.currentMainBrightnessPercent), fill='#cccccc', outline='#cccccc')
        self.mainBrightnessText = self.midPayneContainer.create_text(self.mainBrightnessBarRect[0]+410, self.mainBrightnessBarRect[1], width=50, anchor='nw', font=font, fill=self.mainFGColour, text=str(self.currentMainBrightnessPercent)+'%')

        self.midPayneContainer.create_text(self.sideBrightnessBarRect[0]-10, self.sideBrightnessBarRect[1], width=250, anchor='ne', font=font, fill=self.mainFGColour, text='Colour brightness:')
        self.midPayneContainer.create_rectangle(self.sideBrightnessBarRect[0]-2, self.sideBrightnessBarRect[1]-2, self.sideBrightnessBarRect[2]+2, self.sideBrightnessBarRect[3]+2, fill='#000000', outline='#000000')
        self.sideBrightnessBar = self.midPayneContainer.create_rectangle(self.getBarActualWidth(self.sideBrightnessBarRect, self.currentSideBrightnessPercent), fill='#cccccc', outline='#cccccc')
        self.sideBrightnessText = self.midPayneContainer.create_text(self.sideBrightnessBarRect[0]+410, self.sideBrightnessBarRect[1], width=50, anchor='nw', font=font, fill=self.mainFGColour, text=str(self.currentSideBrightnessPercent)+'%')

        self.midPayneContainer.create_text(self.warmthBarRect[0]-10, self.warmthBarRect[1], width=250, anchor='ne', font=font, fill=self.mainFGColour, text='Warmth:')
        self.midPayneContainer.create_rectangle(self.warmthBarRect[0]-2, self.warmthBarRect[1]-2, self.warmthBarRect[2]+2, self.warmthBarRect[3]+2, fill='#000000', outline='#000000')
        self.warmthBar = self.midPayneContainer.create_rectangle(self.getBarActualWidth(self.warmthBarRect, self.currentWarmthPercent), fill='#cccccc', outline='#cccccc')
        self.warmthText = self.midPayneContainer.create_text(self.warmthBarRect[0]+410, self.warmthBarRect[1], width=50, anchor='nw', font=font, fill=self.mainFGColour, text=str(self.currentWarmthPercent)+'%')

        self.midPayneContainer.create_text(self.barLightsOnRect[0]-10, self.barLightsOnRect[1], width=250, anchor='ne', font=font, fill=self.mainFGColour, text='Bar Lights:')
        self.midPayneContainer.create_rectangle(self.barLightsOnRect[0]-2, self.barLightsOnRect[1]-2, self.barLightsOnRect[2]+2, self.barLightsOnRect[3]+2, fill='#000000', outline='#000000')
        if(self.currentBarLightChecked == True):
            self.barLightsOnCheck = self.midPayneContainer.create_rectangle(self.barLightsOnRect[0], self.barLightsOnRect[1], self.barLightsOnRect[2], self.barLightsOnRect[3], fill='#cccccc', outline='#cccccc')

        self.midPayneContainer.create_text(self.screenLightsOnRect[0]-10, self.screenLightsOnRect[1], width=250, anchor='ne', font=font, fill=self.mainFGColour, text='Screen Lights:')
        self.midPayneContainer.create_rectangle(self.screenLightsOnRect[0]-2, self.screenLightsOnRect[1]-2, self.screenLightsOnRect[2]+2, self.screenLightsOnRect[3]+2, fill='#000000', outline='#000000')
        if(self.currentScreenLightChecked == True):
            self.screenLightsOnCheck = self.midPayneContainer.create_rectangle(self.screenLightsOnRect[0], self.screenLightsOnRect[1], self.screenLightsOnRect[2], self.screenLightsOnRect[3], fill='#cccccc', outline='#cccccc')

        self.midPayneContainer.create_text(self.mainLightsOnRect[0]-10, self.mainLightsOnRect[1], width=250, anchor='ne', font=font, fill=self.mainFGColour, text='Main Lights:')
        self.midPayneContainer.create_rectangle(self.mainLightsOnRect[0]-2, self.mainLightsOnRect[1]-2, self.mainLightsOnRect[2]+2, self.mainLightsOnRect[3]+2, fill='#000000', outline='#000000')
        if(self.currentMainLightChecked == True):
            self.mainLightsOnCheck = self.midPayneContainer.create_rectangle(self.mainLightsOnRect[0], self.mainLightsOnRect[1], self.mainLightsOnRect[2], self.mainLightsOnRect[3], fill='#cccccc', outline='#cccccc')

        self.midPayneContainer.pack(padx=10, pady=5)

    def clickUnderLeftPayne(self, event):
        if((event.x > 4) & (event.x <= 312)):
            if((event.y > 2) & (event.y <= 50)):
                clickedStar = max(1, min(6, int((event.x - 4) / 52)+1))
                self.changeRecipeStars(self.currentRecipe['name'], clickedStar)


    clickedConfigBar = ''
    def clickConfigCanvas(self, event):
        self.clickedConfigBar = ''

        percent = self.getIfMouseIsInBar(event, self.timeoutBarRect)
        if(percent > 0):
            self.clickedConfigBar = 'timeout'
            self.dragConfigCanvas(event)
            return
        percent = self.getIfMouseIsInBar(event, self.mainBrightnessBarRect)
        if(percent > 0):
            self.clickedConfigBar = 'mainBrightness'
            self.dragConfigCanvas(event)
            return
        percent = self.getIfMouseIsInBar(event, self.sideBrightnessBarRect)
        if(percent > 0):
            self.clickedConfigBar = 'sideBrightness'
            self.dragConfigCanvas(event)
            return
        percent = self.getIfMouseIsInBar(event, self.warmthBarRect)
        if(percent > 0):
            self.clickedConfigBar = 'warmth'
            self.dragConfigCanvas(event)
            return
        percent = self.getIfMouseIsInBar(event, self.barLightsOnRect)
        if(percent > 0):
            self.currentBarLightChecked = not self.currentBarLightChecked
            self.configChanges['currentBarLightChecked'] = 1
            if(self.currentBarLightChecked == True):
                self.barLightsOnCheck = self.midPayneContainer.create_rectangle(self.barLightsOnRect[0], self.barLightsOnRect[1], self.barLightsOnRect[2], self.barLightsOnRect[3], fill='#cccccc', outline='#cccccc')
            else:
                self.midPayneContainer.delete(self.barLightsOnCheck)
            return
        percent = self.getIfMouseIsInBar(event, self.screenLightsOnRect)
        if(percent > 0):
            self.currentScreenLightChecked = not self.currentScreenLightChecked
            self.configChanges['currentScreenLightChecked'] = 1
            if(self.currentScreenLightChecked == True):
                self.screenLightsOnCheck = self.midPayneContainer.create_rectangle(self.screenLightsOnRect[0], self.screenLightsOnRect[1], self.screenLightsOnRect[2], self.screenLightsOnRect[3], fill='#cccccc', outline='#cccccc')
            else:
                self.midPayneContainer.delete(self.screenLightsOnCheck)
            return
        percent = self.getIfMouseIsInBar(event, self.mainLightsOnRect)
        if(percent > 0):
            self.currentMainLightChecked = not self.currentMainLightChecked
            self.configChanges['currentMainLightChecked'] = 1
            if(self.currentMainLightChecked == True):
                self.mainLightsOnCheck = self.midPayneContainer.create_rectangle(self.mainLightsOnRect[0], self.mainLightsOnRect[1], self.mainLightsOnRect[2], self.mainLightsOnRect[3], fill='#cccccc', outline='#cccccc')
            else:
                self.midPayneContainer.delete(self.mainLightsOnCheck)
            return


    def dragConfigCanvas(self, event):
        if(self.clickedConfigBar == 'timeout'):
            tup = self.drawConfigBar(event.x, self.midPayneContainer, self.timeoutBarRect, self.timeoutBar, self.currentTimeout, self.timeoutText, ' Minutes', 1, 60)
            self.currentTimeout = tup[0]
            self.configChanges['currentTimeout'] = 1
            self.timeoutBar = tup[1]

        if(self.clickedConfigBar == 'mainBrightness'):
            tup = self.drawConfigBar(event.x, self.midPayneContainer, self.mainBrightnessBarRect, self.mainBrightnessBar, self.currentMainBrightnessPercent, self.mainBrightnessText)
            self.currentMainBrightnessPercent = tup[0]
            self.configChanges['currentMainBrightnessPercent'] = 1
            self.mainBrightnessBar = tup[1]

        if(self.clickedConfigBar == 'sideBrightness'):
            tup = self.drawConfigBar(event.x, self.midPayneContainer, self.sideBrightnessBarRect, self.sideBrightnessBar, self.currentSideBrightnessPercent, self.sideBrightnessText)
            self.currentSideBrightnessPercent = tup[0] 
            self.configChanges['currentSideBrightnessPercent'] = 1
            self.sideBrightnessBar = tup[1]

        if(self.clickedConfigBar == 'warmth'):
            tup = self.drawConfigBar(event.x, self.midPayneContainer, self.warmthBarRect, self.warmthBar, self.currentWarmthPercent, self.warmthText)
            self.currentWarmthPercent = tup[0] 
            self.configChanges['currentWarmthPercent'] = 1
            self.warmthBar = tup[1]
            
    def drawConfigBar(self, mouseX, container, barRect, bar, value, text, stringSuffix='%', minValue=0, maxValue=100):
        total = barRect[2] - barRect[0]
        new = mouseX - barRect[0]
        percent = min(maxValue, max(minValue, ((new / total) * (maxValue-minValue))))
        value = round(percent)
        container.delete(bar)
        bar = container.create_rectangle(self.getBarActualWidth(barRect, value, maxValue), fill='#cccccc', outline='#cccccc')
        container.itemconfig(text, text=str(value)+str(stringSuffix))
        return (value, bar)


    def releaseConfigCanvas(self, event):
        self.clickedConfigBar = ''
        self.updateArduinoConfigs()
            

    def getBarActualWidth(self, bar, value, maxValue=100):
        newWidth = ((bar[2] - bar[0]) / maxValue) * value
        return (bar[0], bar[1], bar[0] + newWidth, bar[3])

    def getIfMouseIsInBar(self, mouseEvent, bar):
        isIn = -1
        if((mouseEvent.x > bar[0]) & (mouseEvent.x <= bar[2])):
            if((mouseEvent.y > bar[1]) & (mouseEvent.y <= bar[3])):
                total = bar[2] - bar[0]
                new = mouseEvent.x - bar[0]
                isIn = ((new / total) * 100)
        return isIn

    def updateArduinoConfigs(self):
        if(self.configChanges['currentMainBrightnessPercent'] == 1):
            self.sendMessageToArduino("MBR"+str(self.currentMainBrightnessPercent))

        if(self.configChanges['currentSideBrightnessPercent'] == 1):
            self.sendMessageToArduino("SBR"+str(self.currentSideBrightnessPercent))

        if(self.configChanges['currentWarmthPercent'] == 1):
            self.sendMessageToArduino("WAR"+str(self.currentWarmthPercent))

        if(self.configChanges['currentBarLightChecked'] == 1):
            if(self.currentBarLightChecked == True):
                self.sendMessageToArduino("BLC1")
            else:
                self.sendMessageToArduino("BLC0")

        if(self.configChanges['currentScreenLightChecked'] == 1):
            if(self.currentScreenLightChecked == True):
                self.sendMessageToArduino("SLC1")
            else:
                self.sendMessageToArduino("SLC0")
        
        if(self.configChanges['currentMainLightChecked'] == 1):
            if(self.currentMainLightChecked == True):
                self.sendMessageToArduino("MLC1")
            else:
                self.sendMessageToArduino("MLC0")
        self.saveConfig()
        return

    configChanges = None
    def loadConfig(self, forceUpdate=0):
        f = open(os.path.join(dirname, "config.JSON"), "r")
        config = json.load(f)
        self.currentTimeout = int(config['currentTimeout'])
        self.currentMainBrightnessPercent = int(config['currentMainBrightnessPercent'])
        self.currentSideBrightnessPercent = int(config['currentSideBrightnessPercent'])
        self.currentWarmthPercent = int(config['currentWarmthPercent'])
        self.currentBarLightChecked = config['currentBarLightChecked'] == 'True'
        self.currentScreenLightChecked = config['currentScreenLightChecked'] == 'True'
        self.currentMainLightChecked = config['currentMainLightChecked'] == 'True'
        
        self.configChanges = dict(currentTimeout = forceUpdate,
                                  currentMainBrightnessPercent = forceUpdate, 
                                  currentSideBrightnessPercent = forceUpdate, 
                                  currentWarmthPercent = forceUpdate, 
                                  currentBarLightChecked = forceUpdate, 
                                  currentScreenLightChecked = forceUpdate, 
                                  currentMainLightChecked = forceUpdate, 
                                  )

    def saveConfig(self):
        JSONString = '{'
        JSONString = JSONString + '"currentTimeout": "'+str(self.currentTimeout)+'",'
        JSONString = JSONString + '"currentMainBrightnessPercent": "'+str(self.currentMainBrightnessPercent)+'",'
        JSONString = JSONString + '"currentSideBrightnessPercent": "'+str(self.currentSideBrightnessPercent)+'",'
        JSONString = JSONString + '"currentWarmthPercent": "'+str(self.currentWarmthPercent)+'",'
        JSONString = JSONString + '"currentBarLightChecked": "'+str(self.currentBarLightChecked)+'",'
        JSONString = JSONString + '"currentScreenLightChecked": "'+str(self.currentScreenLightChecked)+'",'
        JSONString = JSONString + '"currentMainLightChecked": "'+str(self.currentMainLightChecked)+'"'
        JSONString = JSONString + '}'

        f = open(os.path.join(dirname, "config.JSON"), "w")
        f.write(JSONString)
        f.close()

        self.configChanges = dict(currentTimeout = 0,
                                  currentMainBrightnessPercent = 0, 
                                  currentSideBrightnessPercent = 0, 
                                  currentWarmthPercent = 0, 
                                  currentBarLightChecked = 0, 
                                  currentScreenLightChecked = 0, 
                                  currentMainLightChecked = 0, 
                                  )

    def changeRecipeStars(self, recipeName, stars):

        f = open(os.path.join(dirname, "recipes.JSON"), mode='r', encoding='utf-8-sig')
        recipesJSON = json.load(f)

        for i in recipesJSON['recipies']:
            if(i['name'] == recipeName):
                i['stars'] = str(stars)

        self.recipes = recipesJSON
        f.close()

        for i in range(0, 6):
            if(i < stars):
                self.underLeftPayne.itemconfig(self.imageStars[i], image=self.starImageOn)
            else:
                self.underLeftPayne.itemconfig(self.imageStars[i], image=self.starImageOff)
            

        f = open(os.path.join(dirname, "recipes.JSON"), "w", encoding='utf-8')
        f.write(json.dumps(recipesJSON))
        f.close()

    def updateRecipeLastAccessed(self, recipeName):
        f = open(os.path.join(dirname, "recipes.JSON"), mode='r', encoding='utf-8-sig')
        recipesJSON = json.load(f)
                
        for i in recipesJSON['recipies']:
            if(i['name'] == recipeName):
                i['lastAccessed'] = str(time.time())
                

        self.recipes = recipesJSON
        f.close()

        f = open(os.path.join(dirname, "recipes.JSON"), "w", encoding='utf-8')
        f.write(json.dumps(recipesJSON))
        f.close()

    def drawIngredientRow(self, name, yPos, height):
        if name in self.ingredientRows:
            for i in self.ingredientRows[name]:
                self.midPayne.delete(i)

        for i in self.ingredientsData:
            if (i[0] == name):
                checked = i[1]
                LEDStrip = i[2]
                LEDIndex = i[3]
                colour = i[4]
                ingType = i[5]
                alcohol = i[6]
                colourStrength = i[7]
                

        if checked == '1':
            img = self.checkImage
            textColour = '#00ff00'
        else:
            img = self.unCheckImage
            textColour = '#ff0000'
        rowBack = self.midPayne.create_rectangle(0, yPos, 1000, (yPos+height), fill=self.secondaryBGColour, outline=self.secondaryBGColour, tags='back')
        self.ingredientInStockClickAreas.append(((0, yPos, 1000, height), name))
        self.midPayne.lower('back')
        rowName = self.midPayne.create_text(140, yPos+15, anchor='nw', text=name, font=subSubTitleFont, fill=textColour)
        self.ingredientCheckBoxes[name] = self.midPayne.create_image(20, yPos+5, anchor='nw', image=img)

        self.ingredientColourButtons[name] = self.midPayne.create_rectangle(600, yPos+10, 675, yPos+height-10, fill=colour)

        self.ingredientLEDStripButtons[name] = self.midPayne.create_rectangle(700, yPos+10, 775, yPos+height-10, fill=self.secondaryBGColour)
        string = LEDStrip
        if(str(LEDStrip) == "0"):
            string = "-"
        rowLEDStripText = self.midPayne.create_text(737, yPos+30, width=100, font=subSubTitleFont, fill=self.mainFGColour, text=string)

        self.ingredientLEDIndexButtons[name] = self.midPayne.create_rectangle(800, yPos+10, 875, yPos+height-10, fill=self.secondaryBGColour)
        string = LEDIndex
        if(str(LEDIndex) == "0"):
            string = "-"
        rowLEDIndexText = self.midPayne.create_text(837, yPos+30, width=100, font=subSubTitleFont, fill=self.mainFGColour, text=string)

        tup=(rowBack, rowName, self.ingredientCheckBoxes[name], self.ingredientColourButtons[name], self.ingredientLEDStripButtons[name], self.ingredientLEDIndexButtons[name], rowLEDStripText, rowLEDIndexText)
        self.ingredientRows[name] = tup

    def clickAlphabet(self, event):
        x = 0
        for i in self.ingredientsData:
            if(str(i[0][0]).lower() == self.alphabet[math.floor(event.y / 17)]):
                self.moveToIngredient(x)
                return
            x = x + 1

        x = len(self.ingredientsData)
        for i in reversed(self.ingredientsData):
            if(str(i[0][0]).lower() < self.alphabet[math.floor(event.y / 17)-1]):
                self.moveToIngredient(x)
                return
            x = x - 1
        self.moveToIngredient(0)

    def moveToIngredient(self, x):
        totalHeight = self.midPayne.bbox('all')[3]
        scrollTo = ((self.itemHeight + self.itemSpacing) * x)
        self.midPayne.yview_moveto(float(scrollTo+1) / totalHeight)
        return

    def clickIngredient(self, event):
        if (abs(self.scrollVelocity) < 0.1) & (self.hasScrolled == False):
            x = event.x
            y = self.midPayne.canvasy(event.y)
            if(self.numberPickerClickArea != None):
                if ((x > self.numberPickerClickArea[0]) & (x < self.numberPickerClickArea[2])):
                    if ((y > self.numberPickerClickArea[1]) & (y < self.numberPickerClickArea[3])):
                        start = self.numberPickerClickArea[4]
                        end = self.numberPickerClickArea[5]
                        bHeight = (self.numberPickerClickArea[3] - self.numberPickerClickArea[1]) / ((end+1)-start)
                        numberValue = (math.floor((y - self.numberPickerClickArea[1]) / bHeight) + start)
                        
                        match self.numberPickerClickArea[6]:
                            case 'LEDStrip':
                                self.ingredientSelectLEDStrip(self.numberPickerClickArea[7], numberValue, self.numberPickerClickArea[8], self.numberPickerClickArea[9])                                
                            case 'LEDIndex':
                                self.ingredientSelectLEDIndex(self.numberPickerClickArea[7], numberValue, self.numberPickerClickArea[8], self.numberPickerClickArea[9])
                                
                        self.closeNumberPicker(self.numberPickerID)
                        return
            self.closeNumberPicker(None)
            
            for clickArea in self.ingredientInStockClickAreas:
                if ((y > clickArea[0][1]) & (y < clickArea[0][1] + clickArea[0][3])):
                    if ((x > clickArea[0][0]) & (x < clickArea[0][0] + 575)):
                        self.ingredientSelectCheck(clickArea)
                        return
                    if ((x > clickArea[0][0] + 600) & (x < clickArea[0][0] + 675)):
                        self.ingredientSelectColour(clickArea)
                        return
                    if ((x > clickArea[0][0] + 700) & (x < clickArea[0][0] + 775)):
                        tup = (clickArea[0][0] + 700, clickArea[0][1], clickArea[0][0] + 775, clickArea[0][1] + clickArea[0][3])
                        self.openNumberPicker(0, 2, tup[0], tup[1], clickArea[1]+'a', 'LEDStrip', clickArea[1], clickArea[0][1], clickArea[0][3])
                        return
                    if ((x > clickArea[0][0] + 800) & (x < clickArea[0][0] + 875)):
                        tup = (clickArea[0][0] + 800, clickArea[0][1], clickArea[0][0] + 875, clickArea[0][1] + clickArea[0][3])
                        self.openNumberPicker(0, 15, tup[0], tup[1], clickArea[1]+'b', 'LEDIndex', clickArea[1], clickArea[0][1], clickArea[0][3])
                        return

        
    def ingredientSelectCheck(self, clickArea):
        self.midPayne.delete(self.ingredientCheckBoxes[clickArea[1]])
        x = 0
        for i in self.ingredientsData:
            if (i[0] == clickArea[1]):
                if (i[1] == '1'):
                    temp = '0'
                else:
                    temp = '1'
                tpl = (i[0], temp, i[2], i[3], i[4], i[5], i[6], i[7])
                self.ingredientsData[x] = tpl
                self.updateIngredientsFile()
                self.drawIngredientRow(clickArea[1], clickArea[0][1], clickArea[0][3])
                return
            x = x + 1

    def ingredientSelectColour(self, clickArea):
        self.pickColor(clickArea)
        return

    def ingredientSelectLEDStrip(self, name, value, rowYPos, rowHeight):
        x = 0
        for i in self.ingredientsData:
            if (i[0] == name):
                tpl = (i[0], i[1], value, i[3], i[4], i[5], i[6], i[7])
                self.ingredientsData[x] = tpl
                self.updateIngredientsFile()
                self.drawIngredientRow(name, rowYPos, rowHeight)
            x = x + 1
        return

    def ingredientSelectLEDIndex(self, name, value, rowYPos, rowHeight):
        x = 0
        for i in self.ingredientsData:
            if (i[0] == name):
                tpl = (i[0], i[1], i[2], value, i[4], i[5], i[6], i[7])
                self.ingredientsData[x] = tpl
                self.updateIngredientsFile()
                self.drawIngredientRow(name, rowYPos, rowHeight)
            x = x + 1
        return

    numberPickerRect = None
    numberPickerID = None
    numberPickerClickArea = None
    numberPickButtons = []
    numberPickText = []
    def openNumberPicker(self, start, end, xPos, yPos, ID, callback, ingredientName, rowYPos, rowHeight): 
        bHeight = 55

        if(self.closeNumberPicker(ID) == True):

            self.midPayne.update()
            yPos = yPos + 50
            totalHeight = (((end+1) - start) * bHeight)
            containerHeight = self.midPayne.bbox('all')[3]

            if(int((yPos + totalHeight)) > int(containerHeight)):
                yPos = containerHeight - totalHeight

            self.numberPickerRect = self.midPayne.create_rectangle(xPos, yPos, xPos+75, yPos + totalHeight, fill='#ff0000')
            self.numberPickerID = ID
            tup = (xPos, yPos, xPos+75, yPos+(((end+1) - start) * bHeight), start, end, callback, ingredientName, rowYPos, rowHeight)
            self.numberPickerClickArea = tup
            x = 0
            for i in range(start, end+1):
                self.numberPickButtons.append(self.midPayne.create_rectangle(xPos-5, (yPos + (bHeight * x)), xPos+80, (yPos + ((bHeight * x) + bHeight)), fill='#222222'))
                string = str(i)
                if(i == 0):
                    string = "-"
                self.numberPickText.append(self.midPayne.create_text((xPos + 37), (yPos + (bHeight * x) + 28), width=75, font=subSubTitleFont, fill=self.mainFGColour, text=string))
                x = x + 1
        return
    

    def closeNumberPicker(self, ID):
        rtn = True
        if(ID == self.numberPickerID):
            self.numberPickerID = None
            rtn = False
        if(self.numberPickerRect != None):
            self.midPayne.delete(self.numberPickerRect)
            self.numberPickerRect = None
            self.numberPickerClickArea = None
        for i in self.numberPickButtons:
            self.midPayne.delete(i)
        for i in self.numberPickText:
            self.midPayne.delete(i)
        return rtn

    def pickColor(self, clickArea):
        colourCode = colorchooser.askcolor(title = "Choose color")[1]
        if colourCode != None:
            x = 0
            for i in self.ingredientsData:  
                if (i[0] == clickArea[1]):
                    tpl = (i[0], i[1], i[2], i[3], str(colourCode), i[5])
                    self.ingredientsData[x] = tpl
                    self.updateIngredientsFile()
                    self.drawIngredientRow(clickArea[1], clickArea[0][1], clickArea[0][3])
                    return
                x = x + 1

    def selectIngredientLabel(self, index, event):
        if self.hasScrolled == False:
            self.checkBoxes[index].toggle()
            self.updateIngredientsFile()

    def updateIngredientsFileLED(self, event):
        self.updateIngredientsFile()

    def updateIngredientsFile(self):
        self.ingredientsInStock.clear()
        self.ingredientsLEDPosition.clear()
        self.ingredientsColour.clear()
        self.ingredientsAlcohol.clear()
        self.ingredientsColourStrength.clear()
        JSONString = '{"ingredients": ['
        for i in self.ingredientsData:
            print(i)
            temp = i[4]
            if type(temp) != str:
                temp = '#ffffff'
            JSONString = JSONString + '{"name": "' + i[0] + '",'
            JSONString = JSONString + '"inStock": "' + str(i[1]) + '",'
            JSONString = JSONString + '"LEDStrip": "' + str(i[2]) + '",'
            JSONString = JSONString + '"LEDIndex": "' + str(i[3]) + '",'
            JSONString = JSONString + '"Colour": "' + temp + '",'
            JSONString = JSONString + '"alcohol": "' + str(i[6]) + '",'
            JSONString = JSONString + '"colourStrength": "' + str(i[7]) + '",'
            JSONString = JSONString + '"type": "' + str(i[5]) + '"},'

            self.ingredientsInStock.update({str(i[0]):str(i[1])})
            self.ingredientsLEDPosition.update({str(i[0]):(str(i[2]), str(i[3]))})
            self.ingredientsColour.update({str(i[0]):temp})
            self.ingredientsAlcohol.update({str(i[0]):str(i[6])})
            self.ingredientsColourStrength.update({str(i[0]):str(i[7])})
        JSONString = JSONString[:-1]
        JSONString = JSONString + ']}'
        f = open(os.path.join(dirname, "ingredients.JSON"), "w", encoding='utf-8')
        f.write(JSONString)
        f.close()

    def homepage(self, makeNoise):
        if(makeNoise):
            pygame.mixer.music.load(os.path.join(dirname, "closeRecipe.mp3"))
            pygame.mixer.music.play()
        self.sendMessageToArduino("RGBDEF")
        self.sendMessageToArduino("INGCLR")
        self.currentPageIndex = 0
        self.currentRecipe = None
        self.lastActive = datetime.now()
        for child in self.mainFrameCanvas.winfo_children():
            child.destroy()
        self.keyboard = None
        self.pickerCanvas = None
        self.pages[self.currentPageIndex]()
        self.midPayne.yview_moveto(self.recipesScroll)
        self.moveScrollBar()

        if (self.filterValues[0] != 'Any'):
            self.getRecipesByCategory(self.filterValues[0])
            self.midPayneLeftCanvas.itemconfig(self.seasonsButton, image=self.imgSeasonsOpen)
        elif(self.filterValues[1] != 'Any'):
            self.getRecipesBySpirit(self.filterValues[1])
            self.midPayneLeftCanvas.itemconfig(self.spiritsButton, image=self.imgSpiritsOpen)
        elif(self.filterValues[2] != 'Any'):
            self.getRecipesByGlassType(self.filterValues[2])
            self.midPayneLeftCanvas.itemconfig(self.glassTypesButton, image=self.imgGlassTypeOpen)
        elif(self.filterValues[3] != ''):
            self.searchTerm.set(self.filterValues[3])
            self.midPayneLeftCanvas.itemconfig(self.glassTypesButton, image=self.imgGlassTypeOpen)
        else:
            self.getRecipesByCategory('Any')

    def recipesMove(self, direction):
        pygame.mixer.music.load(os.path.join(dirname, "click.mp3"))
        pygame.mixer.music.play()
        self.midPayne.yview_scroll(int(direction), "units")
        self.moveScrollBar()
        
    def recipeMoveTo(self, location, makeSound=True):
        if(makeSound):
            pygame.mixer.music.load(os.path.join(dirname, "click.mp3"))
            pygame.mixer.music.play()
        self.midPayne.yview_moveto(float(location))
        self.moveScrollBar()

    def moveScrollBar(self):
        if self.currentPageIndex == 0:
            size = (self.midPayne.yview()[1] - self.midPayne.yview()[0])
            alpha = (self.midPayne.yview()[0]-0)/max(0.00001, ((1 - (size))-0)*(1-0)+0)
            self.recipeScrollBarCanvas.delete(self.bar)
            self.bar = self.recipeScrollBarCanvas.create_rectangle(27, (alpha * 310) + 3, 47, (alpha * 310) + 4, fill='#cccccc', outline='#cccccc')


    def scrollMainPageRecipes(self, event):
        self.midPayne.yview_scroll(int(-1*(event.delta/120)), "units")

    def scrollRecipeIngredients(self, event):
        self.bottomLeftPayne.yview_scroll(int(-1*(event.delta/120)), "units")

    def scrollRecipeSteps(self, event):
        self.bottomRightPayne.yview_scroll(int(-1*(event.delta/120)), "units")

    def pickCategory(self):
        self.midPayneLeftCanvas.itemconfig(self.seasonsButton, image=self.imgSeasons)
        self.midPayneLeftCanvas.itemconfig(self.spiritsButton, image=self.imgSpirits)
        self.midPayneLeftCanvas.itemconfig(self.glassTypesButton, image=self.imgGlassType)

        self.ingredientsString.set("Any")
        self.glassTypeString.set("Any")
        self.filterValues = (self.categoryString.get(), 'Any', 'Any', '')
        self.searchTerm.set('')
        if(self.categoryString.get() == 'Any'):
            self.setCurrentFilter('')
        else:
            self.setCurrentFilter('seasons')
        self.getRecipesByCategory(self.categoryString.get())

    def pickSpirit(self):
        self.midPayneLeftCanvas.itemconfig(self.seasonsButton, image=self.imgSeasons)
        self.midPayneLeftCanvas.itemconfig(self.spiritsButton, image=self.imgSpirits)
        self.midPayneLeftCanvas.itemconfig(self.glassTypesButton, image=self.imgGlassType)

        self.categoryString.set("Any")
        self.glassTypeString.set("Any")
        self.filterValues = ('Any', self.ingredientsString.get(), 'Any', '')
        self.searchTerm.set('')
        if(self.ingredientsString.get() == 'Any'):
            self.setCurrentFilter('')
        else:
            self.setCurrentFilter('spirits')
        self.getRecipesBySpirit(self.ingredientsString.get())

    def pickGlassType(self):
        self.midPayneLeftCanvas.itemconfig(self.seasonsButton, image=self.imgSeasons)
        self.midPayneLeftCanvas.itemconfig(self.spiritsButton, image=self.imgSpirits)
        self.midPayneLeftCanvas.itemconfig(self.glassTypesButton, image=self.imgGlassType)

        self.categoryString.set("Any")
        self.ingredientsString.set("Any")
        self.filterValues = ('Any', 'Any', self.glassTypeString.get(), '')
        self.searchTerm.set('')
        if(self.glassTypeString.get() == 'Any'):
            self.setCurrentFilter('')
        else:
            self.setCurrentFilter('glassTypes')
        self.getRecipesByGlassType(self.glassTypeString.get())

    def pickMenu(self):
        option = self.menuString.get()
        if(option.__contains__('Ingredients')):
            self.closePickerBox()
            self.openIngredientsManager()
        elif(option.__contains__('Lights Override')):
            self.clickLightsOn()
        elif(option.__contains__('Configuration')):
            self.closePickerBox()
            self.openConfigPage()
        elif(option.__contains__('Sort')):
            self.changeSort()


    def changeSort(self):
        self.currentSortIndex = self.currentSortIndex + 1
        if(self.currentSortIndex >= len(self.sortingOptions)):
            self.currentSortIndex = 0

        self.openMenu()
        self.openMenu()

        self.addRecipeButtons(self.recipeList)
        return

    MainLightsOverride = False
    def clickLightsOn(self):
        self.MainLightsOverride = not self.MainLightsOverride
        if(self.MainLightsOverride == True):
            self.sendMessageToArduino("MLO1")
        else:
            self.sendMessageToArduino("MLO0")
        self.closePickerBox()
        self.openMenu()

    def randomRecipe(self):
        self.openRecipe(self.recipes['recipies'][random.randint(0, len(self.recipes['recipies'])-1)]);

    currentRecipe = None
    def openRecipe(self, recipe):
        if (((abs(self.scrollVelocity) < 0.1) & (self.hasScrolled == False)) | (self.currentPageIndex == 1)):
            pygame.mixer.music.load(os.path.join(dirname, "openRecipe.mp3"))
            pygame.mixer.music.play()
            if(self.currentPageIndex == 0):
                self.recipesScroll = self.midPayne.yview()[0]
           
            self.currentRecipe = recipe
            self.updateRecipeLastAccessed(recipe['name'])

            self.mouseIsDown = False
            self.currentPageIndex = 1
            self.lastActive = datetime.now()
            for child in self.mainFrameCanvas.winfo_children():
                child.destroy()
            self.pages[self.currentPageIndex]()

            recipeColour = self.getRecipeColour(recipe)
            self.sendMessageToArduino("RGB"+recipeColour)
            #self.sendMessageToArduino("RGB"+HexSetSaturation(recipeColour, 1))

            ingredientsLights = dict()
            ingredientsLightsString = ''
            for ingredient in recipe['ingredients']:
                ledStrip = int(self.ingredientsLEDPosition.get(ingredient['name'], (0,0))[0])-1
                ledIndex = int(self.ingredientsLEDPosition.get(ingredient['name'], (0,0))[1])-1
                if((ledStrip >= 0) & (ledIndex >= 0)):
                    ingredientsLightsString += str(ledStrip) + ':' + str(ledIndex) + '|'
                    ingredientsLights[ingredient['name']] = (ledStrip, ledIndex)
            ingredientsLightsString = ingredientsLightsString[:-1]

            self.sendMessageToArduino("ING"+ingredientsLightsString)


            width = self.winfo_width()
            height = self.winfo_height()
            (r1,g1,b1) = self.winfo_rgb(recipeColour)
            (r2,g2,b2) = self.winfo_rgb(self.mainBGColour)
            r_ratio = float(r2-r1) / (width-250)
            g_ratio = float(g2-g1) / (width-250)
            b_ratio = float(b2-b1) / (width-250)
            for i in range(0, width-250, 10):
                nr = int(r1 + (r_ratio * i))
                ng = int(g1 + (g_ratio * i))
                nb = int(b1 + (b_ratio * i))
                color = "#%4.4x%4.4x%4.4x" % (nr,ng,nb)
                self.topPayne.create_rectangle(i, 0, i+9, 100, tags=("gradient",), fill=color, outline=color)
                self.bottomPayne.create_rectangle(i, 0, i+9, 20, tags=("gradient",), fill=color, outline=color)
            self.topPayne.lower("gradient")
            self.bottomPayne.lower("gradient")
            self.topPayne.create_rectangle(0,72,width, 75, fill='#cccccc', outline='#cccccc')
            self.bottomPayne.create_rectangle(0,0,width, 2, fill='#cccccc', outline='#cccccc')

            x = 30
            y = -3
            titleShadow1 = self.topPayne.create_text(x+2,y-2, text=recipe['name'], font=titleFont, anchor='nw', fill=self.mainBGColour)
            titleShadow2 = self.topPayne.create_text(x-2,y+2, text=recipe['name'], font=titleFont, anchor='nw', fill=self.mainBGColour)
            titleShadow3 = self.topPayne.create_text(x,y-2, text=recipe['name'], font=titleFont, anchor='nw', fill=self.mainBGColour)
            titleShadow4 = self.topPayne.create_text(x+4,y+4, text=recipe['name'], font=titleFont, anchor='nw', fill=self.mainBGColour)
            titleShadow5 = self.topPayne.create_text(x-2,y, text=recipe['name'], font=titleFont, anchor='nw', fill=self.mainBGColour)
            titleShadow6 = self.topPayne.create_text(x,y+2, text=recipe['name'], font=titleFont, anchor='nw', fill=self.mainBGColour)
            titleShadow7 = self.topPayne.create_text(x+4,y+4, text=recipe['name'], font=titleFont, anchor='nw', fill=self.mainBGColour)
            #self.topPayne.create_text(30,8, text=recipe['name'], font=titleFont, anchor='nw', fill=self.mainBGColour)
            
            newString = recipe['name']
            titleText = self.topPayne.create_text(x, y, text=recipe['name'], font=titleFont, anchor='nw', fill='#cccccc')
            titleWidth = self.topPayne.bbox(titleText)[2] - self.topPayne.bbox(titleText)[0]
            if(titleWidth > 700):
                while(titleWidth > 700):
                    newString = newString[:-1]
                    self.topPayne.itemconfig(titleText, text=newString)
                    titleWidth = self.topPayne.bbox(titleText)[2] - self.topPayne.bbox(titleText)[0]
                newString = newString + "..."
                self.topPayne.itemconfig(titleText, text=newString)
                self.topPayne.itemconfig(titleShadow1, text=newString)
                self.topPayne.itemconfig(titleShadow2, text=newString)
                self.topPayne.itemconfig(titleShadow3, text=newString)
                self.topPayne.itemconfig(titleShadow4, text=newString)
                self.topPayne.itemconfig(titleShadow5, text=newString)
                self.topPayne.itemconfig(titleShadow6, text=newString)
                self.topPayne.itemconfig(titleShadow7, text=newString)


            ingredientString = ''
            quantitiesString = ''
            i = 0
            for ingredient in recipe['ingredients']:
                dots = ""
                for x in range(28 - (len(ingredient['name'][:18]) + len(ingredient['quantity']) + len(ingredient['unit']))):
                    dots = dots + "."
                    colour = '#ff0000'
                    string = "- "
                    if (self.ingredientsInStock.get(ingredient['name'], 0) == '1'):
                        colour = '#00ff00'
                        string = "+ "
                    elif (self.garnishes.__contains__(str.lower(str.rstrip(ingredient['name'], 's'))) == True):
                        colour = '#00ff00'
                        string = "+ "

                ingredientsLightsString = ""
                if(ingredientsLights.get(ingredient['name'])):
                    ingredientsLightsString += "¤\n"

                ingredientString = ingredientString + ingredient['name'][:28] + "\n"
                quantitiesString = quantitiesString + ingredient['quantity'] + " " + ingredient['unit'] + "\n"
                lineHeight = smallFont.metrics("linespace")
                self.cocktailIngredients.create_text(294, (i*lineHeight), text=ingredientsLightsString, anchor='n', fill='#ffff00', font=smallFont, width=20)
                self.cocktailIngredients.create_text(5, (i*lineHeight), text=string, anchor='n', fill=colour, font=smallFont, width=20)
                i = i+1
            ingredientString = ingredientString[:-1]
            quantitiesString = quantitiesString[:-1]
            ingredientText = self.cocktailIngredients.create_text(15, 0, text=ingredientString, anchor='nw', fill=self.mainFGColour, font=smallFont, width=295, justify='left')
            ingredientWidth = self.cocktailIngredients.bbox(ingredientText)[2] - self.cocktailIngredients.bbox(ingredientText)[0]
            newString = ingredientString
            if(ingredientWidth > 185):
                while(ingredientWidth > 185):
                    newString = newString[:-1]
                    self.cocktailIngredients.itemconfig(ingredientText, text=newString)
                    ingredientWidth = self.cocktailIngredients.bbox(ingredientText)[2] - self.cocktailIngredients.bbox(ingredientText)[0]
                newString = newString + "..."
                self.cocktailIngredients.itemconfig(ingredientText, text=newString)

            quantitiesText = self.cocktailIngredients.create_text(286, 0, text=quantitiesString, anchor='ne', fill=self.mainFGColour, font=smallFont, width=270, justify='right')
            #bulletsText = self.cocktailIngredients.create_text(15, 0, text=bulletsString, anchor='n', fill=self.mainFGColour, font=font, width=20)
            self.cocktailIngredients.configure(height=max((self.cocktailIngredients.bbox(ingredientText)[3] - self.cocktailIngredients.bbox(ingredientText)[1]), self.bottomLeftPayne.winfo_height()))
            height = max((self.cocktailIngredients.bbox(ingredientText)[3] - self.cocktailIngredients.bbox(ingredientText)[1])+5, 114)
            self.bottomLeftPayne.configure(scrollregion=(0, 0, 1000, height))
            
            self.bottomLeftPayne.create_rectangle(0, 0, 315, height, fill=self.mainFGColour, outline=self.mainFGColour)
            self.bottomLeftPayne.create_rectangle(4, 0, 312, height, fill=self.mainBGColour, outline=self.mainBGColour)

            if((self.cocktailIngredients.bbox(ingredientText)[3] - self.cocktailIngredients.bbox(ingredientText)[1]) > 114):
                 self.overFlowContainerSmall.create_image(4, 0, anchor='nw', image=self.overflowImageSmall)

            stepsString = ''
            for step in recipe['steps']:
                stepsString = stepsString + "  • " + step['name'] + "\n" + step['text'] + "\n\n"
            stepsString = stepsString[:-1]

            stepsText = self.cocktailSteps.create_text(332, 0, text=stepsString, anchor='n', fill=self.mainFGColour, font=font, width=665)
            self.cocktailSteps.configure(height=max((self.cocktailSteps.bbox(stepsText)[3] - self.cocktailSteps.bbox(stepsText)[1]), self.bottomRightPayne.winfo_height()))
            self.bottomRightPayne.configure(scrollregion=(0, 0, 1000, max((self.cocktailSteps.bbox(stepsText)[3] - self.cocktailSteps.bbox(stepsText)[1]), 465)))

            if((self.cocktailSteps.bbox(stepsText)[3] - self.cocktailSteps.bbox(stepsText)[1]) > 465):
                 self.overFlowContainer.create_image(0, 0, anchor='nw', image=self.overflowImage)

            self.imageStars = []
            for i in self.recipes['recipies']:
                if(i['name'] == recipe['name']):
                    starsNum = int(i['stars'])

            for i in range(0, 6):
                if(i < starsNum):
                    self.imageStars.append(self.underLeftPayne.create_image((i*52)+7, 5, anchor='nw', image=self.starImageOn))
                else:
                    self.imageStars.append(self.underLeftPayne.create_image((i*52)+7, 5, anchor='nw', image=self.starImageOff))
            

            self.imgGlass = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/glasses/" + recipe['glassType'].split(' ')[0] + ".png")).resize((61, 61), Image.BICUBIC))
            self.underLeftPayne.create_image(7, 54, anchor='nw', image=self.imgGlass)
        
            self.imgCocktail = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/cocktails/" + recipe['ID'] + ".jpg")).resize((315, 255), Image.BICUBIC))
            self.underLeftPayne.create_image(0, 115, anchor='nw', image=self.imgCocktail)

            self.imgGarnishes = []
            x = 0
            for garnish in str(recipe['garnish']).replace(" or ", " , ").split(','):
                if(x < 4):
                    temp = str(garnish).strip(' ').lstrip(' ').lower()
                    if len(temp) <= 1:
                        break
                    if (temp[0] == 'a') & (temp[1] == ' '):
                        temp = temp[2:]
                    self.imgGarnishes.append(ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/garnishes/" + temp + ".png")).resize((61, 61), Image.BICUBIC)))
                    self.underLeftPayne.create_image((252 - (x * 61)) , 54, anchor='nw', image=self.imgGarnishes[len(self.imgGarnishes)-1])
                    x = x + 1

    def openIngredientsManager(self):
        pygame.mixer.music.load(os.path.join(dirname, "openRecipe.mp3"))
        pygame.mixer.music.play()
        self.currentPageIndex = 2
        self.lastActive = datetime.now()
        for child in self.mainFrameCanvas.winfo_children():
            child.destroy()
        self.pages[self.currentPageIndex]()

    def openConfigPage(self):
        pygame.mixer.music.load(os.path.join(dirname, "openRecipe.mp3"))
        pygame.mixer.music.play()
        self.currentPageIndex = 3
        self.lastActive = datetime.now()
        for child in self.mainFrameCanvas.winfo_children():
            child.destroy()
        self.pages[self.currentPageIndex]()

    ArduinoMessageQueue = []
    def sendMessageToArduino(self, message):
        if(self.SerialObj != None):
            msg = message + '>'
            self.ArduinoMessageQueue.append(msg)

def HexToRGB(rgb):
    if (type(rgb) != str):
        return (0, 0, 0)
    if ((len(rgb) == 0) | (rgb[0] != '#')):
        return (0, 0, 0)
    rgb = str.lstrip(rgb, '#')
    return tuple(int(rgb[i:i+2], 16) for i in (0, 2, 4))

def HexSetSaturation(oldHex, newSat):
    rgb = HexToRGB(oldHex)
    hsv = colorsys.rgb_to_hsv((rgb[0]/255), (rgb[1]/255), (rgb[2]/255))
    hsv = (hsv[0], newSat, hsv[2])
    rgb = colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2])
    return RGBToHex(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))

def RGBToHex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

def interpolate(x1: float, x2: float, y1: float, y2: float, x: float):
    """Perform linear interpolation for x between (x1,y1) and (x2,y2) """
    return ((y2 - y1) * x + x2 * y1 - x1 * y2) / (x2 - x1)

def tintImage(image, colour, mask):
    rgb = HexToRGB(colour)
    newImage = PhotoImage(width=image.width(), height=image.height())
    newImageDark = PhotoImage(width=image.width(), height=image.height())
    for x in range(newImage.width()):
        for y in range(newImage.height()):
            if((mask.get(x,y)[0] == 0) & (mask.get(x,y)[1] == 0) & (mask.get(x,y)[2] == 0)):
                r = max(min(255, (image.get(x,y)[0] + rgb[0])/2) - 64, 0)
                g = max(min(255, (image.get(x,y)[1] + rgb[1])/2) - 64, 0)
                b = max(min(255, (image.get(x,y)[2] + rgb[2])/2) - 64, 0)
            else:
                r = mask.get(x,y)[0]
                g = mask.get(x,y)[1]
                b = mask.get(x,y)[2]

            newImage.put("#%02x%02x%02x" % (int(r), int(g), int(b)), (x, y))
            newImageDark.put("#%02x%02x%02x" % (int(r/4), int(g/4), int(b/4)), (x, y))

    return (newImage, newImageDark)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

root.bind("<Escape>", on_escape)
root.wm_geometry("1024x600")
root.resizable(width=False, height=False)
applicationInstance = Application(root)

applicationInstance.sendMessageToArduino("asdasd")
applicationInstance.loadConfig(1)
applicationInstance.updateArduinoConfigs()
applicationInstance.goLight()

root.flipFlop = False
root.clkLastState = None
if(platform.system() != 'Windows'):
    root.after(250, lambda: root.wm_attributes('-fullscreen', 'true'))
    root.after(250, lambda: root.wm_attributes('-topmost', 'true'))
    root.config(cursor='none')

    from RPi import GPIO
    GPIO.setmode(GPIO.BCM)
    step = 100
    clk = 17
    dt = 18
    
    GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    root.clkLastState = GPIO.input(clk)

    def spinEncoder(channel):
        if(applicationInstance.currentPageIndex == 0):
            clkState = GPIO.input(clk)
            dtState = GPIO.input(dt)
            if clkState != root.clkLastState:
                if(root.flipFlop == False):
                    if dtState != clkState:
                        applicationInstance.recipesMove(step)
                    else:
                        applicationInstance.recipesMove(step*-1)
                root.flipFlop = not root.flipFlop
            root.clkLastState = clkState

    GPIO.add_event_detect(clk, GPIO.FALLING, callback=spinEncoder, bouncetime=25)
    GPIO.add_event_detect(dt, GPIO.FALLING, callback=spinEncoder, bouncetime=25)

root.after(1000, applicationInstance.update)
root.mainloop()