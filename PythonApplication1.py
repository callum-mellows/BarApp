import ast
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
dirname = os.path.dirname(__file__)
from functools import partial
from datetime import datetime
from difflib import SequenceMatcher
from PIL import Image, ImageEnhance, ImageTk
from pathlib import Path
import time
import pygame
import math
import random

root = Tk()

font = Font(family="BPtypewrite", size=13)
fontBold = Font(family="BPtypewrite", size=14, weight='bold')
smallFont = Font(family="BPtypewrite", size=8)
titleFont = Font(family="BPtypewrite", size=40, weight="bold")
subTitleFont = Font(family="BPtypewrite", size=20, weight="bold")
subSubTitleFont = Font(family="BPtypewrite", size=15, weight="bold")

spiritList = ("whisky", "whiskey", "vodka", "rum", "brandy", "gin", "tequila")


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
    disabledFGColour = '#333333'

    mainBGColourDark = '#040404'
    secondaryBGColourDark = '#111111'
    mainFGColourDark = '#444444'
    disabledFGColourDark = '#333333'

    sleepSeconds = 300
    lastActive = datetime.now()

    seasons = set([])
    names = set([])
    ingredients = set([])
    ingredientsInStock = dict()
    ingredientsLEDPosition = dict()
    ingredientsColour = dict()
    glassTypes = set([])
    garnishes = ([])
    overflowImage = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/overflow.png")), Image.BICUBIC)
    overflowImageSmall = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/overflowSmall.png")), Image.BICUBIC)
    recipeColours = dict()
    recipeButtonImages = dict()
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

    def __init__(self, root):
        super().__init__(root, bg=self.mainBGColour)

        self.f = open(os.path.join(dirname, "recipes.JSON"), "r")
        self.recipes = json.load(self.f)

        self.f = open(os.path.join(dirname, "ingredients.JSON"), "r")
        tempIngredients = json.load(self.f)

        for ingredient in tempIngredients['ingredients']:
            self.ingredientsInStock.update({ingredient['name']:ingredient['inStock']})
            self.ingredientsLEDPosition.update({ingredient['name']:(ingredient['LEDStrip'], ingredient['LEDIndex'])})
            self.ingredientsColour.update({ingredient['name']:ingredient['Colour']})
            
        checkGarnishImagesExist(self.recipes)
        checkGlassImagesExist(self.recipes)

        self.getSearchables(self.recipes)

        self.currentPageIndex = 0
        self.pages = [self.Page0, self.Page1, self.Page2]

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
    
    scrolling = root
    mouseIsDown = False
    initialMouseY = 0
    scrollVelocity = 0
    hasScrolled = False
    def mouseMove(self, event):
        if self.mouseIsDown == True:
            scrollOffset = root.winfo_pointery() - self.initialMouseY
            if scrollOffset > 0:
                self.scrollVelocity = max(self.scrollVelocity, scrollOffset)
            else:
                self.scrollVelocity = min(self.scrollVelocity, scrollOffset)
            
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

    def update(self):
        if self.scrollVelocity > 0:
            self.scrollVelocity = max(0, self.scrollVelocity - 2)
        elif self.scrollVelocity < 0:
            self.scrollVelocity = min(0, self.scrollVelocity + 2)
        now = datetime.now()
        dtString = now.strftime("%d/%m/%Y %H:%M:%S")
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
        if(sinceActive.seconds >= self.sleepSeconds):
            if(self.isDark == False):
                self.goDark()

    isDark = False
    def goDark(self):
        self.homepage()

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

        self.midPayneLeftCanvas.itemconfig(self.searchButton, image=self.imgSearchDark)
        self.midPayneLeftCanvas.itemconfig(self.seasonsButton, image=self.imgSeasonsDark)
        self.midPayneLeftCanvas.itemconfig(self.spiritsButton, image=self.imgSpiritsDark)
        self.midPayneLeftCanvas.itemconfig(self.glassTypesButton, image=self.imgGlassTypeDark)
        self.midPayneLeftCanvas.itemconfig(self.ingredientsButton, image=self.imgIngredientManagerDark)

        self.upDownBtnCanvas.itemconfig(self.upButton, image=self.upImageDark)
        self.upDownBtnCanvas.itemconfig(self.downButton, image=self.downImageDark)
        self.recipeScrollBarCanvas.itemconfig(self.bar, fill=self.mainFGColourDark, outline=self.mainFGColourDark)
        self.recipeScrollBarCanvas.itemconfig(self.barBack, fill=self.mainFGColourDark, outline=self.mainFGColourDark)


    def goLight(self):
        print("light")
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
            self.midPayne.itemconfig(self.recipeButtons[i], image=self.recipeButtonImages.get(i))
            self.midPayne.itemconfig(self.recipeTexts[i], fill=self.mainFGColour)

        self.midPayneLeftCanvas.itemconfig(self.searchButton, image=self.imgSearch)
        self.midPayneLeftCanvas.itemconfig(self.seasonsButton, image=self.imgSeasons)
        self.midPayneLeftCanvas.itemconfig(self.spiritsButton, image=self.imgSpirits)
        self.midPayneLeftCanvas.itemconfig(self.glassTypesButton, image=self.imgGlassType)
        self.midPayneLeftCanvas.itemconfig(self.ingredientsButton, image=self.imgIngredientManager)

        self.upDownBtnCanvas.itemconfig(self.upButton, image=self.upImage)
        self.upDownBtnCanvas.itemconfig(self.downButton, image=self.downImage)
        self.recipeScrollBarCanvas.itemconfig(self.bar, fill=self.mainFGColour, outline=self.mainFGColour)
        self.recipeScrollBarCanvas.itemconfig(self.barBack, fill=self.mainFGColour, outline=self.mainFGColour)

    def getIfIngredientIsSpirit(self, ing):
        for word in str(ing).split(' '):
            for spirit in spiritList:
                if spirit.__contains__(str(word).lower()):
                    return spirit
        return ""

    def getSearchables(self, recipes):

        buttonFileDir = os.path.join(dirname, "images/cocktails/buttons")
        buttonFiles = [f for f in listdir(buttonFileDir) if isfile(join(buttonFileDir, f))]
        for file in buttonFiles:
            self.recipeButtonFiles[file.split('_')[0]] = (file.split('_')[1].split('.')[0], ImageTk.PhotoImage(Image.open(buttonFileDir + '/' + file), Image.BICUBIC))
            self.recipeButtonFilesDark[file.split('_')[0]] = (file.split('_')[1].split('.')[0], ImageTk.PhotoImage(Image.open(buttonFileDir + '/dark/' + file), Image.BICUBIC))

        seasons2 = set([])
        names2 = set([])
        ingredients2 = set([])
        spirits = set([])
        glassTypes2 = set([])
        garnishes2 = ([])
        recipeButton = PhotoImage(file = os.path.join(dirname, "images/buttons/recipeButton.png"))
        recipeButtonMask = PhotoImage(file = os.path.join(dirname, "images/buttons/recipeButtonMask.png"))
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
                    
                    temp = self.getIfIngredientIsSpirit(ingredient['name'])
                    if temp != "":
                        spirits.add(temp)

            found = False
            self.recipeColours[recipe['name']] = self.getRecipeColour(recipe)
            if(self.recipeButtonFiles.__contains__(recipe['ID'])):
                if(self.recipeButtonFiles[recipe['ID']][0] == self.recipeColours[recipe['name']]):
                    self.recipeButtonImages[recipe['name']] = self.recipeButtonFiles[recipe['ID']][1]
                    self.recipeButtonImagesDark[recipe['name']] = self.recipeButtonFilesDark[recipe['ID']][1]
                    found = True
                else:
                    os.remove(buttonFileDir + '/' + recipe['ID'] + '_' + self.recipeButtonFiles[recipe['ID']][0] + '.png')
                    os.remove(buttonFileDir + '/dark/' + recipe['ID'] + '_' + self.recipeButtonFiles[recipe['ID']][0] + '.png')
                
            if(found == False):
                buttonImg = tintImage(recipeButton, self.recipeColours[recipe['name']], recipeButtonMask)
                self.recipeButtonImages[recipe['name']] = buttonImg[0]
                self.recipeButtonImagesDark[recipe['name']] = buttonImg[1]
                self.recipeButtonImages[recipe['name']].write(buttonFileDir + '/' + recipe['ID'] + '_' + self.recipeColours[recipe['name']] + '.png', format='png')
                self.recipeButtonImagesDark[recipe['name']].write(buttonFileDir + '/dark/' + recipe['ID'] + '_' + self.recipeColours[recipe['name']] + '.png', format='png')
            

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
    
    def recipeIngredientsInStock(self, recipe):
        for ingredient in recipe['ingredients']:
            if (self.ingredientsInStock.get(ingredient['name'], 0)) != '1':
                return False
        return True

    keyboard = None
    keyCanvas = None
    keys = []
    keyTexts = []
    keyboardOpen = False
    searchTerm = StringVar()
    def openKeyboard(self):
        self.keyboard = Frame(self.mainFrameCanvas)
        self.keyboard.place(x=10, y=307)
        
        self.keyCanvas = Canvas(self.keyboard, width=1005, height=285, highlightthickness=0, bg='#222222')
        self.keyCanvas.pack(fill='both')

        self.searchTerm.trace("w", lambda name, index, mode, searchTerm=self.searchTerm: self.updateSearchBox(searchTerm))
        self.keyboardTextEntry = Entry(self.keyCanvas, font=subTitleFont, textvariable=self.searchTerm, bg=self.mainBGColour, bd=0, fg=self.mainFGColour)
        self.keyboardTextEntry.place(x=15, y=10, height=40, width=975)

        for i in range(0, 13):
            self.keys.append(self.keyCanvas.create_rectangle((i*75)+15, 55, ((i+1)*75)+15, 130, fill=self.secondaryBGColour))
            self.keyTexts.append(self.keyCanvas.create_text(((i*75)+15)+37, 92, width=75, text=self.alphabet[i], font=titleFont, fill=self.mainFGColour))
            self.keys.append(self.keyCanvas.create_rectangle((i*75)+15, 130, ((i+1)*75)+15, 205, fill=self.secondaryBGColour))
            self.keyTexts.append(self.keyCanvas.create_text(((i*75)+15)+37, 167, width=75, text=self.alphabet[i+13], font=titleFont, fill=self.mainFGColour))
        
        self.keys.append(self.keyCanvas.create_rectangle(90, 205, 240, 280, fill=self.secondaryBGColour))
        self.keyTexts.append(self.keyCanvas.create_text(165, 242, width=150, text='🠜', font=titleFont, fill=self.mainFGColour))

        self.keys.append(self.keyCanvas.create_rectangle(315, 205, 690, 280, fill=self.secondaryBGColour))
        self.keyTexts.append(self.keyCanvas.create_text(492, 242, width=375, text='Space', font=titleFont, fill=self.mainFGColour))

        self.keys.append(self.keyCanvas.create_rectangle(765, 205, 915, 280, fill=self.secondaryBGColour))
        self.keyTexts.append(self.keyCanvas.create_text(840, 242, width=150, text='🡃', font=titleFont, fill=self.mainFGColour))
        Misc.lift(self.keyboard)
        self.keyboardOpen = True

    def keyboardClickCheck(self, event):
        if(self.keyboardOpen == True):
            if(event.widget == self.keyCanvas):

                if((event.y > 55) & (event.y <= 130) & (event.x > 5) & (event.x < 980)):
                    self.searchTerm.set(self.searchTerm.get() + self.alphabet[math.floor((event.x - 5) / 75)])
                elif((event.y > 130) & (event.y <= 205) & (event.x > 5) & (event.x < 980)):
                    self.searchTerm.set(self.searchTerm.get() + self.alphabet[(math.floor((event.x - 5) / 75)) + 13])
                elif((event.y > 205) & (event.y <= 280)):
                    if((event.x > 80) & (event.x <= 230)):
                        self.searchTerm.set(self.searchTerm.get()[:-1])
                    elif((event.x > 305) & (event.x <= 680)):
                        self.searchTerm.set(self.searchTerm.get() + ' ')
                    elif((event.x > 755) & (event.x <= 905)):
                        self.searchTerm.set('')
                        self.closeKeyboard()
                self.keyboardTextEntry.icursor(len(self.searchTerm.get()))
                return
            #self.closeKeyboard()

    def closeKeyboard(self):
        if(self.keyboard != None):
            self.keyboard.place_forget()
            self.keyboard = None
            self.keyCanvas = None
            root.focus()
            self.keyboardOpen = False

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
                if str(ing['name']).lower().__contains__(spirit) | (spirit == 'Any'):
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
        self.filterValues = ('Any', 'Any', 'Any', searchTerm.get())
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
            if self.recipeIngredientsInStock(recipe) == True:
                RecipeListInStock.append(recipe)
            else:
                RecipeListNotInStock.append(recipe)
        return RecipeListInStock + RecipeListNotInStock

    def getRecipeColour(self, recipe):
        RGB = [0, 0, 0]
        ingredientsCount = 0
        for ingredient in recipe['ingredients']:
            ingredientsCount = ingredientsCount + 1
            tempRGB = HexToRGB(self.ingredientsColour.get(ingredient['name']))
            RGB[0] = RGB[0] + tempRGB[0]
            RGB[1] = RGB[1] + tempRGB[1]
            RGB[2] = RGB[2] + tempRGB[2]
        RGB[0] = RGB[0] / max(ingredientsCount, 1)
        RGB[1] = RGB[1] / max(ingredientsCount, 1)
        RGB[2] = RGB[2] / max(ingredientsCount, 1)
        return RGBToHex(int(RGB[0]), int(RGB[1]), int(RGB[2]))

    recipeButtons = dict()  
    recipeTexts = dict()  
    recipeButtonAreas = []
    
    def addRecipeButtons(self, recipes):
        self.recipeButtonAreas.clear()
        orderedRecipes = self.orderRecipeListByInStock(recipes)

        for child in self.recipeButtons.values():
            self.midPayne.delete(child)
        for child in self.recipeTexts.values():
            self.midPayne.delete(child)
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
            #self.buttonImages[recipe['ID']] = PhotoImage(file = os.path.join(dirname, "images/cocktails/buttons/"+recipe['ID']+".jpg"))

            if self.recipeIngredientsInStock(recipe) == True:
                colour = self.mainFGColour
            else:
                colour = self.disabledFGColour

            self.recipeButtons[recipe['name']] = self.midPayne.create_image(self.left, self.top, anchor='nw', image=self.recipeButtonImages.get(recipe['name']))
            self.recipeTexts[recipe['name']] = self.midPayne.create_text(self.left + 15, self.top + 15, width=self.w-25, anchor='nw', justify=LEFT, font=fontBold, fill=colour, text=recipe['name'])
            self.recipeButtonAreas.append(((self.left, self.top, self.w, self.h), recipe))

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
        if(self.isDark == True):
            self.goLight()
            return
        self.lastActive = datetime.now()
        if (event.x > 0 & event.x < 75):
            if((event.y > 10) & (event.y < 85)):
                self.recipesMove(-105)
                return
            if((event.y > 370) & (event.y < 445)):
                self.recipesMove(105)
                return

    def clickLeftButtonCanvas(self, event):
        if(self.isDark == True):
            self.goLight()
            return
        self.lastActive = datetime.now()
        if(event.y <= 75):
            self.openSearch()
        elif((event.y > 100) & (event.y <= 175)):
            self.openSeasons()
        elif((event.y > 200) & (event.y <= 275)):
            self.openSpirits()
        elif((event.y > 300) & (event.y <= 375)):
            self.openGlassTypes()
        elif((event.y > 400) & (event.y <= 475)):
            self.openIngredientsManager()

    def openSearch(self):
        if(self.pickerCanvas != None):
            self.closePickerBox()
            self.pickerType = ''

        if(self.keyboard == None):
            self.openKeyboard()
            self.midPayneLeftCanvas.itemconfig(self.searchButton, image=self.imgSearchOn)
        else:
            self.searchTerm.set('')
            self.closeKeyboard()
            self.midPayneLeftCanvas.itemconfig(self.searchButton, image=self.imgSearch)

    def pickerClick(self, options, event):
        self.pickerString.set(options[math.floor(event.y / 40)])
        if(self.pickerType == 'seasons'):
            self.pickCategory()
        elif(self.pickerType == 'spirits'):
            self.pickSpirit()
        elif(self.pickerType == 'glassTypes'):
            self.pickGlassType()
        self.closePickerBox()

    pickerCanvas = None
    pickerType = ''
    pickerString = None
    def openPickerBox(self, options, XPos, YPos, string):
        if(self.keyboard != None):
            self.searchTerm.set('')
            self.closeKeyboard()
            self.midPayneLeftCanvas.itemconfig(self.searchButton, image=self.imgSearch)

        self.pickerString = string
        self.pickerCanvas = Canvas(self.mainFrameCanvas, width=200, height=400, bg='#ff0000', highlightthickness=0)
        action_with_arg = partial(self.pickerClick, options)
        self.pickerCanvas.bind('<ButtonPress-1>', action_with_arg)
        x = 0
        for item in options:
            self.pickerCanvas.create_rectangle(0, x * 40, 200, (x + 1) * 40, fill='#222222')
            self.pickerCanvas.create_text(100, (x*40) + 20, width=200, fill=self.mainFGColour, font=font, text=item)
            x = x + 1
        self.pickerCanvas.configure(height=x*40)
        self.pickerCanvas.place(x=XPos, y=(YPos - (x*10)))

    def closePickerBox(self):
        if(self.pickerCanvas != None):
            self.pickerCanvas.place_forget()
            self.pickerCanvas = None
            self.midPayneLeftCanvas.itemconfig(self.seasonsButton, image=self.imgSeasons)
            self.midPayneLeftCanvas.itemconfig(self.spiritsButton, image=self.imgSpirits)
            self.midPayneLeftCanvas.itemconfig(self.glassTypesButton, image=self.imgGlassType)
            self.pickerType = ''

    categoryString = StringVar()
    def openSeasons(self):
        if(self.pickerCanvas != None):
            self.closePickerBox()

        if(self.pickerType != 'seasons'):
            self.openPickerBox(self.seasons, 110, 137, self.categoryString)
            self.pickerType = 'seasons'
            self.midPayneLeftCanvas.itemconfig(self.seasonsButton, image=self.imgSeasonsOn)
        else:
            self.pickerType = ''

    ingredientsString = StringVar() 
    def openSpirits(self):
        if(self.pickerCanvas != None):
            self.closePickerBox()

        if(self.pickerType != 'spirits'):
            self.openPickerBox(self.spirits, 110, 237, self.ingredientsString)
            self.pickerType = 'spirits'
            self.midPayneLeftCanvas.itemconfig(self.spiritsButton, image=self.imgSpiritsOn)
        else:
            self.pickerType = ''

    glassTypeString = StringVar() 
    def openGlassTypes(self):
        if(self.pickerCanvas != None):
            self.closePickerBox()

        if(self.pickerType != 'glassTypes'):
            self.openPickerBox(self.glassTypes, 110, 337, self.glassTypeString)
            self.pickerType = 'glassTypes'
            self.midPayneLeftCanvas.itemconfig(self.glassTypesButton, image=self.imgGlassTypeOn)
        else:
            self.pickerType = ''

    def Page0(self):

        self.topPayne = Canvas(self.mainFrameCanvas, highlightthickness=0, bg=self.mainBGColour, width=1024, height=70);
        self.titleFrame = Frame(self.topPayne, bg=self.mainBGColour)
        self.titleLabel = Label(self.titleFrame, font=titleFont, text="Cocktails 'n shit", bg=self.mainBGColour, fg=self.mainFGColour)
        self.titleLabel.pack(side=BOTTOM)
        self.titleFrame.pack(side=LEFT, fill='y', padx=10, pady=0)
        self.dateTimeFrame = Frame(self.topPayne, bg=self.mainBGColour)
        self.dateTimeLabel = Label(self.dateTimeFrame, font=subSubTitleFont, anchor='n', bg=self.mainBGColour, fg=self.mainFGColour, text="00/00/0000 00:00:00")
        self.dateTimeLabel.pack(side=TOP)
        self.dateTimeFrame.pack(side=RIGHT, fill='y', padx=10, pady=10)
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
        self.upButton = self.upDownBtnCanvas.create_image(0, 10, anchor='nw', image=self.upImage)
        self.downImage = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/down.png")), Image.BICUBIC)
        self.downImageDark = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/downDark.png")), Image.BICUBIC)
        self.downButton = self.upDownBtnCanvas.create_image(0, 370, anchor='nw', image=self.downImage)
        self.recipeScrollBarCanvas = Canvas(self.upDownBtnCanvas, bg=self.mainBGColour, borderwidth=0, highlightthickness=0, width=75, height=290)
        self.barBack = self.recipeScrollBarCanvas.create_rectangle(35, 0, 39, 320, fill='#cccccc', outline='#cccccc')
        self.bar = self.recipeScrollBarCanvas.create_rectangle(17, 3, 57, 5, fill='#cccccc', outline='#cccccc')
        self.recipeScrollBarCanvas.pack(pady = 83)
        self.upDownBtnCanvas.pack(side=RIGHT, fill='y', padx=10)

        self.midPayneContainer.pack(side=RIGHT)
        
        self.midPayneLeftCanvas = Canvas(self.midPayneContainerContainer, bg=self.mainBGColour, borderwidth=0, highlightthickness=0, width=75, height=475)
        
        self.imgSearch = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/search.png")), Image.BICUBIC)
        self.imgSearchDark = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/searchDark.png")), Image.BICUBIC)
        self.imgSearchOn = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/search_on.png")), Image.BICUBIC)
        self.searchButton = self.midPayneLeftCanvas.create_image(0, 0, anchor='nw', image=self.imgSearch)

        self.imgSeasons = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/season.png")), Image.BICUBIC)
        self.imgSeasonsDark = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/seasonDark.png")), Image.BICUBIC)
        self.imgSeasonsOn = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/season_on.png")), Image.BICUBIC)
        self.seasonsButton = self.midPayneLeftCanvas.create_image(0, 100, anchor='nw', image=self.imgSeasons)

        self.imgSpirits = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/spirit.png")), Image.BICUBIC)
        self.imgSpiritsDark = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/spiritDark.png")), Image.BICUBIC)
        self.imgSpiritsOn = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/spirit_on.png")), Image.BICUBIC)
        self.spiritsButton = self.midPayneLeftCanvas.create_image(0, 200, anchor='nw', image=self.imgSpirits)

        self.imgGlassType = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/glassType.png")), Image.BICUBIC)
        self.imgGlassTypeDark = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/glassTypeDark.png")), Image.BICUBIC)
        self.imgGlassTypeOn = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/glassType_on.png")), Image.BICUBIC)
        self.glassTypesButton = self.midPayneLeftCanvas.create_image(0, 300, anchor='nw', image=self.imgGlassType)

        self.imgIngredientManager = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/ingredients.png")), Image.BICUBIC)
        self.imgIngredientManagerDark = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/ingredientsDark.png")), Image.BICUBIC)
        self.imgIngredientManagerOn = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/ingredients_on.png")), Image.BICUBIC)
        self.ingredientsButton = self.midPayneLeftCanvas.create_image(0, 400, anchor='nw', image=self.imgIngredientManager)

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
            if((event.x > 810) & (event.x <= 855)):
                self.randomRecipe()
            elif((event.x > 880) & (event.x <= 1000)):
                self.homepage()

    def Page1(self):

        self.topPayne = Canvas(self.mainFrameCanvas, highlightthickness=0, bg=self.mainBGColour, width=1050, height=75);

        self.topPayne.pack(side=TOP)
        self.topPayne.pack_propagate(0)

        self.imgShuffleButton = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/shuffle.png")), Image.BICUBIC)
        self.topPayne.create_image(810, 15, anchor='nw', image=self.imgShuffleButton)

        self.imgReturnButton = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/buttons/home.png")), Image.BICUBIC)
        self.topPayne.create_image(880, 15, anchor='nw', image=self.imgReturnButton)
        self.topPayne.bind('<ButtonPress-1>', self.clickTopPayne)

        # self.btn = Button(self.topPayne, text="Return", font=subSubTitleFont, command=self.homepage)
        # self.btn.pack(side=RIGHT, padx=25, pady=10)

        # self.btn2 = Button(self.topPayne, text=u"\U0001F500", font=subSubTitleFont, command=self.randomRecipe)
        # self.btn2.pack(side=RIGHT, padx=25, pady=10)

        self.middleContainer = Frame(self.mainFrameCanvas, bg=self.mainBGColour)

        self.leftPaynesContainer = Frame(self.middleContainer)
        self.bottomLeftPayneContainer = Frame(self.leftPaynesContainer, bg=self.mainBGColour)
        self.bottomLeftPayne = Canvas(self.bottomLeftPayneContainer, highlightthickness=0, bg=self.mainBGColour, scrollregion="0 0 2000 500", width=315, height=140)
        self.bottomLeftPayne.configure(yscrollincrement='1')
        self.bottomLeftPayne.bind("<MouseWheel>", self.scrollRecipeIngredients)
        self.cocktailIngredients = Canvas(self.bottomLeftPayne, width=310, height=130, bg=self.mainBGColour, highlightthickness=0)
        mouse_action_with_arg = partial(self.mouseDown, self.bottomLeftPayne, True)
        self.cocktailIngredients.bind('<ButtonPress-1>', mouse_action_with_arg)
        self.cocktailIngredients.bind('<Leave>', self.mouseUp)
        self.cocktailIngredients.bind("<MouseWheel>", self.scrollRecipeIngredients)
        self.bottomLeftPayne.create_window((5, 10), anchor=NW, window=self.cocktailIngredients)
        self.bottomLeftPayne.pack()

        self.overFlowContainerSmall = Canvas(self.bottomLeftPayneContainer, bg=self.mainBGColour, width=315, height=15, highlightthickness=0)
        self.overFlowContainerSmall.pack(side=BOTTOM)

        self.bottomLeftPayneContainer.pack(side=TOP, padx=0, pady=0)

        self.underLeftPayneContainer = Frame(self.leftPaynesContainer, bg=self.mainBGColour)
        self.underLeftPayne = Canvas(self.underLeftPayneContainer, highlightthickness=0, bg=self.mainBGColour, height=350, width=315)

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

    def Page2(self):
        self.topPayne = Canvas(self.mainFrameCanvas, highlightthickness=0, bg=self.mainBGColour, width=1024, height=100);
        self.titleFrame = Frame(self.topPayne, bg=self.mainBGColour)
        self.titleLabel = Label(self.titleFrame, font=titleFont, text="Ingredients", bg=self.mainBGColour, fg=self.mainFGColour)
        self.titleLabel.pack(side=TOP)
        self.titleFrame.pack(side=LEFT, fill='y', padx=10, pady=0)
        self.btn = Button(self.topPayne, text="Return", font=subSubTitleFont, command=self.homepage)
        self.btn.pack(side=RIGHT, padx=25, pady=25)
        self.topPayne.pack(fill='x')
        self.topPayne.pack_propagate(0)

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

                tpl = (ingredient, checked, ledStrip, ledIndex, colour)
                self.ingredientsData.append(tpl)

                self.drawIngredientRow(ingredient, itemYPos, self.itemHeight)
                x = x + 1
                itemYPos = itemYPos + self.itemHeight + self.itemSpacing

        self.midPayne.configure(scrollregion=(0, 0, 1000, max(itemYPos, self.midPayneContainer.winfo_height())))
        self.midPayne.pack(side=RIGHT)

        self.midPayneContainer.pack(side=LEFT)
        self.midPayneContainerContainer.pack(pady=5)

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
        rowLEDStripText = self.midPayne.create_text(737, yPos+30, width=100, font=subSubTitleFont, fill=self.mainFGColour, text=LEDStrip)

        self.ingredientLEDIndexButtons[name] = self.midPayne.create_rectangle(800, yPos+10, 875, yPos+height-10, fill=self.secondaryBGColour)
        rowLEDIndexText = self.midPayne.create_text(837, yPos+30, width=100, font=subSubTitleFont, fill=self.mainFGColour, text=LEDIndex)

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
                        self.openNumberPicker(1, 5, tup[0], tup[1], clickArea[1]+'a', 'LEDStrip', clickArea[1], clickArea[0][1], clickArea[0][3])
                        return
                    if ((x > clickArea[0][0] + 800) & (x < clickArea[0][0] + 875)):
                        tup = (clickArea[0][0] + 800, clickArea[0][1], clickArea[0][0] + 875, clickArea[0][1] + clickArea[0][3])
                        self.openNumberPicker(1, 15, tup[0], tup[1], clickArea[1]+'b', 'LEDIndex', clickArea[1], clickArea[0][1], clickArea[0][3])
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
                tpl = (i[0], temp, i[2], i[3], i[4])
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
                tpl = (i[0], i[1], value, i[3], i[4])
                self.ingredientsData[x] = tpl
                self.updateIngredientsFile()
                self.drawIngredientRow(name, rowYPos, rowHeight)
            x = x + 1
        return

    def ingredientSelectLEDIndex(self, name, value, rowYPos, rowHeight):
        x = 0
        for i in self.ingredientsData:
            if (i[0] == name):
                tpl = (i[0], i[1], i[2], value, i[4])
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
        bHeight = 35

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
                self.numberPickButtons.append(self.midPayne.create_rectangle(xPos, (yPos + (bHeight * x)), xPos+75, (yPos + ((bHeight * x) + bHeight)), fill='#222222'))
                self.numberPickText.append(self.midPayne.create_text((xPos + 37), (yPos + (bHeight * x) + 20), width=75, font=subSubTitleFont, fill=self.mainFGColour, text=i))
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
                    tpl = (i[0], i[1], i[2], i[3], str(colourCode))
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
        JSONString = '{"ingredients": ['
        for i in self.ingredientsData:
            temp = i[4]
            if type(temp) != str:
                temp = '#ffffff'
            JSONString = JSONString + '{"name": "' + i[0] + '",'
            JSONString = JSONString + '"inStock": "' + str(i[1]) + '",'
            JSONString = JSONString + '"LEDStrip": "' + str(i[2]) + '",'
            JSONString = JSONString + '"LEDIndex": "' + str(i[3]) + '",'
            JSONString = JSONString + '"Colour": "' + temp + '"},'

            self.ingredientsInStock.update({str(i[0]):str(i[1])})
            self.ingredientsLEDPosition.update({str(i[0]):(str(i[2]), str(i[3]))})
            self.ingredientsColour.update({str(i[0]):temp})
        JSONString = JSONString[:-1]
        JSONString = JSONString + ']}'
        f = open(os.path.join(dirname, "ingredients.JSON"), "w")
        f.write(JSONString)
        f.close()

    def homepage(self):
        pygame.mixer.music.load(os.path.join(dirname, "closeRecipe.mp3"))
        pygame.mixer.music.play()
        self.currentPageIndex = 0
        self.lastActive = datetime.now()
        for child in self.mainFrameCanvas.winfo_children():
            child.destroy()
        self.keyboard = None
        self.pickerCanvas = None
        self.pages[self.currentPageIndex]()
        self.midPayne.yview_moveto(self.recipesScroll)
        self.moveScrollBar()

    def recipesMove(self, direction):
        pygame.mixer.music.load(os.path.join(dirname, "click.mp3"))
        pygame.mixer.music.play()
        self.midPayne.yview_scroll(int(direction), "units")
        self.moveScrollBar()
        

    def moveScrollBar(self):
        if self.currentPageIndex == 0:
            size = (self.midPayne.yview()[1] - self.midPayne.yview()[0])
            alpha = (self.midPayne.yview()[0]-0)/max(0.00001, ((1 - (size))-0)*(1-0)+0)
            self.recipeScrollBarCanvas.delete(self.bar)
            self.bar = self.recipeScrollBarCanvas.create_rectangle(17, (alpha * 276) + 3, 57, (alpha * 276) + 5, fill='#cccccc', outline='#cccccc')


    def scrollMainPageRecipes(self, event):
        self.midPayne.yview_scroll(int(-1*(event.delta/120)), "units")

    def scrollRecipeIngredients(self, event):
        self.bottomLeftPayne.yview_scroll(int(-1*(event.delta/120)), "units")

    def scrollRecipeSteps(self, event):
        self.bottomRightPayne.yview_scroll(int(-1*(event.delta/120)), "units")

    def pickCategory(self):
        self.ingredientsString.set("Any")
        self.glassTypeString.set("Any")
        self.filterValues = (self.categoryString.get(), 'Any', 'Any', '')
        self.getRecipesByCategory(self.categoryString.get())

    def pickSpirit(self):
        self.categoryString.set("Any")
        self.glassTypeString.set("Any")
        self.filterValues = ('Any', self.ingredientsString.get(), 'Any', '')
        self.getRecipesBySpirit(self.ingredientsString.get())

    def pickGlassType(self):
        self.categoryString.set("Any")
        self.ingredientsString.set("Any")
        self.filterValues = ('Any', 'Any', self.glassTypeString.get(), '')
        self.getRecipesByGlassType(self.glassTypeString.get())

    def randomRecipe(self):
        self.openRecipe(self.recipes['recipies'][random.randint(0, len(self.recipes['recipies'])-1)]);

    def openRecipe(self, recipe):
        if (((abs(self.scrollVelocity) < 0.1) & (self.hasScrolled == False)) | (self.currentPageIndex == 1)):
            pygame.mixer.music.load(os.path.join(dirname, "openRecipe.mp3"))
            pygame.mixer.music.play()
            if(self.currentPageIndex == 0):
                self.recipesScroll = self.midPayne.yview()[0]
           
            #self.closeKeyboard()
            #self.closePickerBox()

            self.mouseIsDown = False
            self.currentPageIndex = 1
            self.lastActive = datetime.now()
            for child in self.mainFrameCanvas.winfo_children():
                child.destroy()
            self.pages[self.currentPageIndex]()

            recipeColour = self.getRecipeColour(recipe)

            width = self.winfo_width()
            height = self.winfo_height()
            (r1,g1,b1) = self.winfo_rgb(recipeColour)
            (r2,g2,b2) = self.winfo_rgb('#000000')
            r_ratio = float(r2-r1) / width
            g_ratio = float(g2-g1) / width
            b_ratio = float(b2-b1) / width
            for i in range(0, width, 10):
                nr = int(r1 + (r_ratio * i))
                ng = int(g1 + (g_ratio * i))
                nb = int(b1 + (b_ratio * i))
                color = "#%4.4x%4.4x%4.4x" % (nr,ng,nb)
                #self.topPayne.create_line(i, 0, i+1, 100, tags=("gradient",), fill=color)
                self.topPayne.create_rectangle(i, 0, i+9, 100, tags=("gradient",), fill=color, outline=color)
                #self.bottomPayne.create_line(i, 0, i, 20, tags=("gradient",), fill=color)
                self.bottomPayne.create_rectangle(i, 0, i+9, 20, tags=("gradient",), fill=color, outline=color)
            self.topPayne.lower("gradient")
            self.bottomPayne.lower("gradient")
            self.topPayne.create_rectangle(0,72,width, 75, fill='#cccccc', outline='#cccccc')
            self.bottomPayne.create_rectangle(0,0,width, 2, fill='#cccccc', outline='#cccccc')

            self.topPayne.create_text(32,4, text=recipe['name'], font=titleFont, anchor='nw', fill=self.mainBGColour)
            self.topPayne.create_text(28,8, text=recipe['name'], font=titleFont, anchor='nw', fill=self.mainBGColour)
            self.topPayne.create_text(30,4, text=recipe['name'], font=titleFont, anchor='nw', fill=self.mainBGColour)
            self.topPayne.create_text(34,10, text=recipe['name'], font=titleFont, anchor='nw', fill=self.mainBGColour)
            self.topPayne.create_text(28,6, text=recipe['name'], font=titleFont, anchor='nw', fill=self.mainBGColour)
            self.topPayne.create_text(30,8, text=recipe['name'], font=titleFont, anchor='nw', fill=self.mainBGColour)
            self.topPayne.create_text(34,10, text=recipe['name'], font=titleFont, anchor='nw', fill=self.mainBGColour)
            #self.topPayne.create_text(30,8, text=recipe['name'], font=titleFont, anchor='nw', fill=self.mainBGColour)
            
            self.topPayne.create_text(30,6, text=recipe['name'], font=titleFont, anchor='nw', fill='#cccccc')
        
            bulletsString = ''
            ingredientString = ''
            i = 0
            for ingredient in recipe['ingredients']:
                dots = ""
                for x in range(28 - (len(ingredient['name'][:18]) + len(ingredient['quantity']) + len(ingredient['unit']))):
                    dots = dots + "."
                    colour = '#ff0000'
                    string = "\u2610 "
                    if (self.ingredientsInStock.get(ingredient['name'], 0) == '1'):
                        colour = '#00ff00'
                        string = "\u2611 "
                    elif (self.garnishes.__contains__(str.lower(str.rstrip(ingredient['name'], 's'))) == True):
                        colour = '#00ff00'
                        string = "\u2611 "


                ingredientString = ingredientString + ingredient['name'][:18] + dots + ingredient['quantity'] + ingredient['unit'] + "\n"
                lineHeight = font.metrics("linespace")
                self.cocktailIngredients.create_text(10, (i*lineHeight), text=string, anchor='n', fill=colour, font=font, width=20)
                i = i+1
            ingredientString = ingredientString[:-1]
            ingredientText = self.cocktailIngredients.create_text(165, 0, text=ingredientString, anchor='n', fill=self.mainFGColour, font=font, width=290)
            bulletsText = self.cocktailIngredients.create_text(15, 0, text=bulletsString, anchor='n', fill=self.mainFGColour, font=font, width=20)
            self.cocktailIngredients.configure(height=max((self.cocktailIngredients.bbox(ingredientText)[3] - self.cocktailIngredients.bbox(ingredientText)[1]), self.bottomLeftPayne.winfo_height()))
            self.bottomLeftPayne.configure(scrollregion=(0, 0, 1000, max((self.cocktailIngredients.bbox(ingredientText)[3] - self.cocktailIngredients.bbox(ingredientText)[1])+15, 140)))
            
            if((self.cocktailIngredients.bbox(ingredientText)[3] - self.cocktailIngredients.bbox(ingredientText)[1]) > 140):
                 self.overFlowContainerSmall.create_image(0, 0, anchor='nw', image=self.overflowImageSmall)

            stepsString = ''
            for step in recipe['steps']:
                stepsString = stepsString + "\u2022 " + step['name'] + "\n" + step['text'] + "\n\n"
            stepsString = stepsString[:-1]

            stepsText = self.cocktailSteps.create_text(332, 0, text=stepsString, anchor='n', fill=self.mainFGColour, font=font, width=665)
            self.cocktailSteps.configure(height=max((self.cocktailSteps.bbox(stepsText)[3] - self.cocktailSteps.bbox(stepsText)[1]), self.bottomRightPayne.winfo_height()))
            self.bottomRightPayne.configure(scrollregion=(0, 0, 1000, max((self.cocktailSteps.bbox(stepsText)[3] - self.cocktailSteps.bbox(stepsText)[1]), 465)))

            if((self.cocktailSteps.bbox(stepsText)[3] - self.cocktailSteps.bbox(stepsText)[1]) > 465):
                 self.overFlowContainer.create_image(0, 0, anchor='nw', image=self.overflowImage)

            self.imgGlass = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/glasses/" + recipe['glassType'].split(' ')[0] + ".png")).resize((60, 75), Image.BICUBIC))
            self.underLeftPayne.create_image(5, 0, anchor='nw', image=self.imgGlass)
        
            self.imgCocktail = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/cocktails/" + recipe['ID'] + ".jpg")).resize((310, 255), Image.BICUBIC))
            self.underLeftPayne.create_image(5, 75, anchor='nw', image=self.imgCocktail)

            self.imgGarnishes = []
            x = 0
            for garnish in str(recipe['garnish']).replace(" or ", " , ").split(','):
                temp = str(garnish).strip(' ').lstrip(' ').lower()
                if len(temp) <= 1:
                    break
                if (temp[0] == 'a') & (temp[1] == ' '):
                    temp = temp[2:]
                self.imgGarnishes.append(ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images/garnishes/" + temp + ".png")).resize((60, 75), Image.BICUBIC)))
                self.underLeftPayne.create_image((255 - (x * 60)) , 0, anchor='nw', image=self.imgGarnishes[len(self.imgGarnishes)-1])
                x = x + 1

            

            #self.cocktailGarnish.config(text=recipe['garnish'])
            #self.cocktailGlass.config(text=recipe['glassType'])

    def openIngredientsManager(self):
        pygame.mixer.music.load(os.path.join(dirname, "openRecipe.mp3"))
        pygame.mixer.music.play()
        self.currentPageIndex = 2
        self.lastActive = datetime.now()
        for child in self.mainFrameCanvas.winfo_children():
            child.destroy()
        #self.closeKeyboard()
        #self.closePickerBox()
        self.pages[self.currentPageIndex]()

def HexToRGB(rgb):
    if (type(rgb) != str):
        return (0, 0, 0)
    if ((len(rgb) == 0) | (rgb[0] != '#')):
        return (0, 0, 0)
    rgb = str.lstrip(rgb, '#')
    return tuple(int(rgb[i:i+2], 16) for i in (0, 2, 4))

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
                # r2 = int(r/4)
                # g2 = int(g/4)
                # b2 = int(b/4)
            else:
                r = mask.get(x,y)[0]
                g = mask.get(x,y)[1]
                b = mask.get(x,y)[2]
                # r2 = mask.get(x,y)[0]
                # g2 = mask.get(x,y)[1]
                # b2 = mask.get(x,y)[2]

            newImage.put("#%02x%02x%02x" % (int(r), int(g), int(b)), (x, y))
            newImageDark.put("#%02x%02x%02x" % (int(r/4), int(g/4), int(b/4)), (x, y))

    return (newImage, newImageDark)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

root.bind("<Escape>", on_escape)
root.wm_geometry("1024x600")
root.resizable(width=False, height=False)
applicationInstance = Application(root)

if(platform.system() != 'Windows'):
    root.after(250, lambda: root.wm_attributes('-fullscreen', 'true'))
    root.after(250, lambda: root.wm_attributes('-topmost', 'true'))

root.after(1000, applicationInstance.update)
root.mainloop()