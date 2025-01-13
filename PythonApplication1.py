import ast
from genericpath import isfile
import json
from tkinter import *
from tkinter import ttk 
import os
import tkinter
from tkinter.messagebox import showerror
from tkinter.font import Font
dirname = os.path.dirname(__file__)
from functools import partial
from datetime import datetime
from difflib import SequenceMatcher
from PIL import Image
from PIL import ImageTk
from pathlib import Path

root = Tk()

transparentColour = '#FF00E8'
mainBGColour = '#111111'
secondaryBGColour = '#595959'
mainFGColour = '#CCCCCC'

font = Font(family="Courier new", size=13)
smallFont = Font(family="Courier new", size=8)
titleFont = Font(family="Courier new", size=40, weight="bold")
subTitleFont = Font(family="Courier new", size=15, weight="bold")

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
            path = os.path.join(dirname, "images\\garnishes\\" + temp + ".png")
            if Path(path).is_file() == False:
                showerror("", "missing file: " + path)
                return False
    return True

def checkGlassImagesExist(recipes):
    for recipe in recipes['recipies']:
        path = os.path.join(dirname, "images\\glasses\\" + recipe['glassType'].split(' ')[0] + ".png")
        if Path(path).is_file() == False:
                showerror("", "missing file: " + path)
                return False
    return True

class Application(Frame):

    scrollPos = 0;
    categories = set([])
    names = set([])
    ingredients = set([])
    glassTypes = set([])
    
    def getIfIngredientIsSpirit(self, ing):
        for word in str(ing).split(' '):
            for spirit in spiritList:
                if spirit.__contains__(str(word).lower()):
                    return spirit
        return ""

    def getSearchables(self, recipes):
        categories2 = set([])
        names2 = set([])
        ingredients2 = set([])
        spirits = set([])
        glassTypes2 = set([])
        for recipe in recipes['recipies']:
            temp = recipe['season']
            if len(temp) > 1:
                categories2.add(temp)

            temp = recipe['name']
            if len(temp) > 1:
                names2.add(temp)

            temp = recipe['glassType']
            if len(temp) > 1:
                glassTypes2.add(temp)

            if len(recipe['ingredients']) > 1:
                for ingredient in recipe['ingredients']:
                    ingredients2.add(ingredient['name'])
                    
                    temp = self.getIfIngredientIsSpirit(ingredient['name'])
                    if temp != "":
                        spirits.add(temp)
            
            self.categories = sorted(categories2)
            self.names = sorted(names2)
            self.ingredients = sorted(ingredients2)
            self.spirits = sorted(spirits)
            self.glassTypes = sorted(glassTypes2)
    
    def __init__(self, root):
        super().__init__(root, bg=mainBGColour)

        self.f = open("recipes.JSON", "r")
        self.recipes = json.load(self.f)

        checkGarnishImagesExist(self.recipes)
        checkGlassImagesExist(self.recipes)

        #self.garnishes = findGarnishes(self.recipes)
        self.getSearchables(self.recipes)

        self.currentPageIndex = 0
        self.pages = [self.Page0, self.Page1, self.Page2]

        self.mainFrame = self
        self.mainFrame.configure(bg=mainBGColour)
        self.mainFrame.pack(fill=BOTH, expand=True)
        self.mainFrame.columnconfigure(0, weight=1)
        self.mainFrame.rowconfigure(0, weight=1)
        
        self.pages[self.currentPageIndex]()

    def getRecipesByCategory(self, season):
        recipeList = []
        for recipe in self.recipes['recipies']:
            if (recipe['season'] == season) | (season == 'None') | (season == 'Any'):
                recipeList.append(recipe)
        self.addRecipeButtons(recipeList)

 #if (SequenceMatcher(a=ing['name'],b=spirit).ratio() > 0.75) | (spirit == 'Any'):
    def getRecipesBySpirit(self, spirit):
        recipeList = []
        for recipe in self.recipes['recipies']:
            for ing in recipe['ingredients']:
                if str(ing['name']).lower().__contains__(spirit) | (spirit == 'Any'):
                    recipeList.append(recipe)
                    break
        self.addRecipeButtons(recipeList)


    def getRecipesByGlassType(self, glassType):
        recipeList = []
        for recipe in self.recipes['recipies']:
            if (recipe['glassType'] == glassType) | (glassType == 'Any'):
                recipeList.append(recipe)
        self.addRecipeButtons(recipeList)

    def addRecipeButtons(self, recipes):
        for child in self.midPayne.winfo_children():
            child.destroy()
        self.totalButtons = 501
        self.w = 190
        self.h = 100
        self.rows = 1
        self.top = 5
        self.left = 5
        self.buttonImages = {};
        x = 0
        for recipe in recipes:
            if (x % 4 == 0) & (x > 0):
                self.left=5
                self.top = self.top + self.h + 10
                self.rows = self.rows + 1

            action_with_arg = partial(self.openRecipe, recipe)
            self.buttonImages[recipe['ID']] = PhotoImage(file = os.path.join(dirname, "images\\cocktails\\buttons\\"+recipe['ID']+".jpg"))
            self.btn = Button(self.midPayne, width=self.w, height=self.h, highlightthickness=0, fg='#ffffff', font=font, wraplength=180, borderwidth=0, padx=0, pady=0, image=self.buttonImages[recipe['ID']], compound="center", text=recipe['name'], command=action_with_arg)
            self.btn.bind("<MouseWheel>", self.scrollMainPageRecipes)
            self.item = self.midPayne.create_window((self.left, self.top), anchor=NW, window=self.btn)
            self.left = self.left+self.w+10;
            x = x + 1
        self.midPayne.configure(scrollregion=(0, 0, ((self.w * 4) + 25), max((((self.h * self.rows) + (10 * (self.rows + 1)))-5), self.midPayneContainer.winfo_height())))

    def setTimeString(self, timeString):
        if self.currentPageIndex == 0:
            self.dateTimeLabel.configure(text=timeString)
            self.dateTimeLabel.update()
    

    def Page0(self):

        self.topPayne = Canvas(self.mainFrame, highlightthickness=0, bg=mainBGColour, width=1024, height=70);
        self.titleFrame = Frame(self.topPayne, bg=mainBGColour)
        self.titleLabel = Label(self.titleFrame, font=titleFont, text="Cocktails 'n shit", bg=mainBGColour, fg=mainFGColour)
        self.titleLabel.pack(side=BOTTOM)
        self.titleFrame.pack(side=LEFT, fill='y', padx=10, pady=0)
        self.dateTimeFrame = Frame(self.topPayne, bg=mainBGColour)
        self.dateTimeLabel = Label(self.dateTimeFrame, font=subTitleFont, anchor='n', bg=mainBGColour, fg=mainFGColour, text="00/00/0000 00:00:00")
        self.dateTimeLabel.pack(side=TOP)
        self.dateTimeFrame.pack(side=RIGHT, fill='y', padx=10, pady=10)
        self.topPayne.pack(fill='x')
        self.topPayne.pack_propagate(0)

        self.midPayneContainerContainer = Frame(self.mainFrame, bg=mainBGColour)
        self.midPayneContainer = Frame(self.midPayneContainerContainer)
        self.midPayne = Canvas(self.midPayneContainer, highlightthickness=0, bg=mainBGColour, scrollregion="0 0 2000 1000", width=805, height=450)
        self.midPayne.bind("<MouseWheel>", self.scrollMainPageRecipes)
        #self.vbar=Scrollbar(self.midPayneContainer, orient=VERTICAL)
        #self.vbar.pack(side=RIGHT, fill=Y)
        #self.vbar.config(command=self.midPayne.yview)
        #self.midPayne.config(yscrollcommand=self.vbar.set)
        self.getRecipesByCategory('Any')
        self.midPayne.pack()

        self.upDownBtnFrame = Frame(self.midPayneContainerContainer, bg=mainBGColour)
        action_with_arg2 = partial(self.recipesMove, -1)
        self.buttonUpImage = PhotoImage(file = os.path.join(dirname, "images\\buttons\\btn1.png"))
        self.upBtn = Button(self.upDownBtnFrame, width=75, height=75, highlightthickness=0, borderwidth=0, fg='#ffffff', padx=0, pady=0, image=self.buttonUpImage, compound="center", text='up', command=action_with_arg2)
        self.upBtn.pack(side=TOP, pady=10)
        action_with_arg3 = partial(self.recipesMove, 1)
        self.buttonDownImage = PhotoImage(file = os.path.join(dirname, "images\\buttons\\btn1.png"))
        self.downBtn = Button(self.upDownBtnFrame, width=75, height=75, highlightthickness=0, borderwidth=0, fg='#ffffff', padx=0, pady=0, image=self.buttonDownImage, compound="center", text='down', command=action_with_arg3)
        self.downBtn.pack(side=BOTTOM, pady=10)
        self.upDownBtnFrame.pack(side=RIGHT, fill='y', padx=10)

        self.midPayneContainer.pack(side=LEFT)
        self.midPayneContainerContainer.pack(pady=5)

        self.bottomPayne = Canvas(self.mainFrame, highlightthickness=0, bg=mainBGColour, width=1024, height=75);

        self.categoryFrame = Frame(self.bottomPayne, bg=mainBGColour)
        self.categoryLabel = Label(self.categoryFrame, bg=mainBGColour, fg=mainFGColour, font=smallFont, text='Season:')
        self.categoryLabel.pack(side=TOP)
        if self.categories.__contains__('Any') == False:
            self.categories.insert(0, 'Any')
        self.categoryString = StringVar(self.categoryFrame) 
        self.categoryBox = ttk.OptionMenu(self.categoryFrame, self.categoryString, list(self.categories)[0], *self.categories, command=self.pickCategory, direction='above')
        self.categoryBox.configure(width=25)
        self.categoryBox.pack(ipadx=20, ipady=10, side=BOTTOM)
        self.categoryFrame.pack(side=LEFT, padx = 25, pady=5)

        self.ingredientsFrame = Frame(self.bottomPayne, bg=mainBGColour)
        self.ingredientsLabel = Label(self.ingredientsFrame, bg=mainBGColour, fg=mainFGColour, font=smallFont, text='Spirit:')
        self.ingredientsLabel.pack(side=TOP)
        if self.spirits.__contains__('Any') == False:
            self.spirits.insert(0, 'Any')
        self.ingredientsString = StringVar(self.ingredientsFrame) 
        self.ingredientsBox = ttk.OptionMenu(self.ingredientsFrame, self.ingredientsString, list(self.spirits)[0], *self.spirits, command=self.pickSpirit, direction='above')
        self.ingredientsBox.configure(width=25)
        self.ingredientsBox.pack(ipadx=20, ipady=10, side=BOTTOM)
        self.ingredientsFrame.pack(side=LEFT, padx = 25, pady=5)

        self.glassFrame = Frame(self.bottomPayne, bg=mainBGColour)
        self.glassLabel = Label(self.glassFrame, bg=mainBGColour, fg=mainFGColour, font=smallFont, text='Glass Type:')
        self.glassLabel.pack(side=TOP)
        if self.glassTypes.__contains__('Any') == False:
            self.glassTypes.insert(0, 'Any')
        self.glassTypeString = StringVar(self.glassFrame) 
        self.glassTypeBox = ttk.OptionMenu(self.glassFrame, self.glassTypeString, list(self.glassTypes)[0], *self.glassTypes, command=self.pickGlassType, direction='above')
        self.glassTypeBox.configure(width=25)
        self.glassTypeBox.pack(ipadx=20, ipady=10, side=BOTTOM)
        self.glassFrame.pack(side=LEFT, padx = 25, pady=5)

        self.bottomPayne.pack()

    def Page1(self):

        self.topPayne = Canvas(self.mainFrame, highlightthickness=0, bg=mainBGColour, width=1024, height=100);

        self.topPayne.pack(side=TOP)
        self.topPayne.pack_propagate(0)

        self.btn = Button(self.topPayne, text="Return", font=subTitleFont, command=self.homepage)
        self.btn.pack(side=RIGHT, padx=25, pady=25)

        self.middleContainer = Frame(self.mainFrame, bg=mainBGColour)

        self.leftPaynesContainer = Frame(self.middleContainer)
        self.bottomLeftPayneContainer = Frame(self.leftPaynesContainer, bg=mainBGColour)
        self.bottomLeftPayne = Canvas(self.bottomLeftPayneContainer, highlightthickness=0, bg=mainBGColour, scrollregion="0 0 2000 500", height=150, width=315)
        self.bottomLeftPayne.bind("<MouseWheel>", self.scrollRecipeIngredients)
        #self.vbar2=Scrollbar(self.bottomLeftPayneContainer, orient=VERTICAL)
        #self.vbar2.pack(side=LEFT, fill=Y)
        #self.vbar2.config(command=self.bottomLeftPayne.yview)
        #self.bottomLeftPayne.config(yscrollcommand=self.vbar2.set)
        self.cocktailIngredients = Text(self.bottomLeftPayne, font=font, width=31, bg=mainBGColour, fg=mainFGColour, borderwidth=0, wrap=WORD)
        self.cocktailIngredients.bind("<MouseWheel>", self.scrollRecipeIngredients)
        self.bottomLeftPayne.create_window((5, 5), anchor=NW, window=self.cocktailIngredients)
        self.bottomLeftPayne.pack(pady=5)
        self.bottomLeftPayneContainer.pack(side=TOP, padx=0, pady=0)

        self.underLeftPayneContainer = Frame(self.leftPaynesContainer, bg=mainBGColour)
        self.underLeftPayne = Canvas(self.underLeftPayneContainer, highlightthickness=0, bg=mainBGColour, height=285, width=315)

        self.underLeftPayne.pack(pady=10)
        self.underLeftPayne.pack_propagate(0)
        self.underLeftPayneContainer.pack(side=BOTTOM, padx=0, pady=0)

        self.leftPaynesContainer.pack(side=LEFT, padx=5, pady=5)

        self.bottomRightPayneContainer = Frame(self.middleContainer, bg=mainBGColour)
        self.bottomRightPayne = Canvas(self.bottomRightPayneContainer, highlightthickness=0, bg=mainBGColour, scrollregion="0 0 2000 1000", width=700, height=435)
        self.bottomRightPayne.bind("<MouseWheel>", self.scrollRecipeSteps)
        #self.vbar3=Scrollbar(self.bottomRightPayneContainer, orient=VERTICAL)
        #self.vbar3.pack(side=RIGHT, fill=Y)
        #self.vbar3.config(command=self.bottomRightPayne.yview)
        #self.bottomRightPayne.config(yscrollcommand=self.vbar3.set)
        self.cocktailSteps = Text(self.bottomRightPayne, font=font, width=66, bg=mainBGColour, fg=mainFGColour, borderwidth=0, wrap=WORD)
        self.cocktailSteps.bind("<MouseWheel>", self.scrollRecipeSteps)
        self.bottomRightPayne.create_window((5, 5), anchor=NW, window=self.cocktailSteps)
        self.bottomRightPayne.pack(padx=8, side=TOP)

        self.overFlowContainer = Canvas(self.bottomRightPayneContainer, bg=mainBGColour, width=700, height=30, highlightthickness=0)
        self.overFlowContainer.pack(padx=8, side=BOTTOM)

        self.bottomRightPayneContainer.pack(side=RIGHT, padx=5, pady=0)

        self.middleContainer.pack(side=TOP)

        #self.cocktailGarnish = Label(self.mainFrame, text="garnish")
        #self.cocktailGarnish.pack()

        #self.cocktailGlass = Label(self.mainFrame, text="glass")
        #self.cocktailGlass.pack()

        self.bottomPayneContainer = Frame(self.mainFrame, bg='#0000cc', width=1024, height=15)
        self.bottomPayne = Canvas(self.bottomPayneContainer, highlightthickness=0, bg='#cc0000', width=1024, height=20);
        self.bottomPayne.pack()
        self.bottomPayneContainer.pack(side=BOTTOM)



    def Page2(self):
        pass

    def homepage(self):
        self.currentPageIndex = 0
        for child in self.mainFrame.winfo_children():
            child.destroy()
        self.pages[self.currentPageIndex]()
        self.midPayne.yview_moveto(self.scrollPos)

    def recipesMove(self, direction):
        self.midPayne.yview_scroll(int(direction*7), "units")
        

    def scrollMainPageRecipes(self, event):
        self.midPayne.yview_scroll(int(-1*(event.delta/120)), "units")

    def scrollRecipeIngredients(self, event):
        self.bottomLeftPayne.yview_scroll(int(-1*(event.delta/120)), "units")

    def scrollRecipeSteps(self, event):
        self.bottomRightPayne.yview_scroll(int(-1*(event.delta/120)), "units")

    def pickCategory(self, event):
        self.ingredientsString.set("Any")
        self.glassTypeString.set("Any")
        self.getRecipesByCategory(self.categoryString.get())

    def pickSpirit(self, event):
        self.categoryString.set("Any")
        self.glassTypeString.set("Any")
        self.getRecipesBySpirit(self.ingredientsString.get())

    def pickGlassType(self, event):
        self.categoryString.set("Any")
        self.ingredientsString.set("Any")
        self.getRecipesByGlassType(self.glassTypeString.get())

    def openRecipe(self, recipe):
        #self.scrollPos = self.vbar.get()[0]
        self.currentPageIndex = 1
        for child in self.mainFrame.winfo_children():
            child.destroy()
        self.pages[self.currentPageIndex]()

        width = self.winfo_width()
        height = self.winfo_height()
        (r1,g1,b1) = self.winfo_rgb(recipe['colour'])
        (r2,g2,b2) = self.winfo_rgb('#000000')
        r_ratio = float(r2-r1) / width
        g_ratio = float(g2-g1) / width
        b_ratio = float(b2-b1) / width
        for i in range(width):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = "#%4.4x%4.4x%4.4x" % (nr,ng,nb)
            self.topPayne.create_line(i, 0, i, 100, tags=("gradient",), fill=color)
            self.bottomPayne.create_line(i, 0, i, 20, tags=("gradient",), fill=color)
        self.topPayne.lower("gradient")
        self.bottomPayne.lower("gradient")
        self.topPayne.create_rectangle(0,97,width, 100, fill='#cccccc', outline='#cccccc')
        self.bottomPayne.create_rectangle(0,0,width, 2, fill='#cccccc', outline='#cccccc')

        #self.cocktailName.config(text=recipe['name'])
        self.topPayne.create_text(30,20, text=recipe['name'], font=titleFont, anchor='nw')
        
        self.cocktailIngredients.delete(1.0, END)

        for ingredient in recipe['ingredients']:
            dots = ""
            for x in range(28 - (len(ingredient['name'][:18]) + len(ingredient['quantity']) + len(ingredient['unit']))):
                dots = dots + "."
            self.cocktailIngredients.insert(END, "\u2022 " + ingredient['name'][:18] + dots + ingredient['quantity'] + ingredient['unit'] + "\n")
        self.cocktailIngredients.delete('end-2c', END)
        root.update()
        root.update_idletasks()
        line_height = font.metrics("linespace")
        num_lines = self.cocktailIngredients.count('1.0', END, 'displaylines')[0]
        total_height = line_height * num_lines + 10
        self.cocktailIngredients.config(height=(num_lines))
        self.bottomLeftPayne.configure(scrollregion=(0, 0, 1000, max(total_height, self.bottomLeftPayne.winfo_height())))
                    
        self.cocktailSteps.delete(1.0, END)
        for step in recipe['steps']:
            self.cocktailSteps.insert(END, "\u2022 " + step['name'] + "\n" + step['text'] + "\n\n")
        self.cocktailSteps.delete('end-2c', END)
        root.update()
        root.update_idletasks()
        line_height = font.metrics("linespace")
        num_lines = self.cocktailSteps.count('1.0', END, 'displaylines')[0]
        total_height = line_height * num_lines + 10
        self.cocktailSteps.config(height=(num_lines))
        self.bottomRightPayne.configure(scrollregion=(0, 0, 1000, max(total_height, self.bottomRightPayne.winfo_height())))

        if num_lines > 21:
            self.overflowImage = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images\\overflow.png")), Image.BICUBIC)
            self.overFlowContainer.create_image(0, 0, anchor='nw', image=self.overflowImage)

        self.imgGlass = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images\\glasses\\" + recipe['glassType'].split(' ')[0] + ".png")).resize((75, 75), Image.BICUBIC))
        self.underLeftPayne.create_image(10, 0, anchor='nw', image=self.imgGlass)
        
        self.imgCocktail = ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images\\cocktails\\" + recipe['ID'] + ".jpg")).resize((225, 225), Image.BICUBIC))
        self.underLeftPayne.create_image(85, 0, anchor='nw', image=self.imgCocktail)

        self.imgGarnishes = []
        x = 0
        for garnish in str(recipe['garnish']).replace(" or ", " , ").split(','):
            temp = str(garnish).strip(' ').lstrip(' ').lower()
            if len(temp) <= 1:
                break
            if (temp[0] == 'a') & (temp[1] == ' '):
                temp = temp[2:]
            self.imgGarnishes.append(ImageTk.PhotoImage(Image.open(os.path.join(dirname, "images\\garnishes\\" + temp + ".png")).resize((75, 75), Image.BICUBIC)))
            self.underLeftPayne.create_image((235 - (x * 75)) , 225, anchor='nw', image=self.imgGarnishes[len(self.imgGarnishes)-1])
            x = x + 1

        #self.cocktailGarnish.config(text=recipe['garnish'])
        #self.cocktailGlass.config(text=recipe['glassType'])

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
#root.attributes("-fullscreen", True)
#root.wm_attributes("-topmost", True)
root.bind("<Escape>", on_escape)
root.wm_geometry("1024x600")
root.resizable(width=False, height=False)
applicationInstance = Application(root)

def update():
    now = datetime.now()
    dtString = now.strftime("%d/%m/%Y %H:%M:%S")
    applicationInstance.setTimeString(dtString)
    root.after(1000, update)

root.after(1000, update)
root.mainloop()