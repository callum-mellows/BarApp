import ast
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

root = Tk()

mainBGColour = '#111111'
secondaryBGColour = '#444444'
mainFGColour = '#CCCCCC'

font = Font(family="Courier new", size=13)
smallFont = Font(family="Courier new", size=8)
titleFont = Font(family="Courier new", size=40, weight="bold")
subTitleFont = Font(family="Courier new", size=15, weight="bold")

def on_escape(event=None):
    root.destroy()

def findGarnishes(recipes):
    garnishes = set([])
    for recipe in recipes['recipies']:
        for garnish in ast.Constant(recipe['garnish']).replace(" or ", " , ").split(','):
            temp = ast.Constant(garnish).strip(' ').lower() + "\n"
            if len(temp) <= 1:
                break
            if (temp[0] == 'a') & (temp[1] == ' '):
                temp = temp[2:]
            garnishes.add(temp)

    f2 = open("garnishes.txt", "w")
    for garnish in garnishes:
        f2.write(garnish)
    f2.close()

class Application(Frame):

    scrollPos = 0;
    categories = set([])
    names = set([])
    ingredients = set([])
    glassTypes = set([])
    
    def getSearchables(self, recipes):
        categories2 = set([])
        names2 = set([])
        ingredients2 = set([])
        glassTypes2 = set([])
        for recipe in recipes['recipies']:
            temp = recipe['colour']
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
       
            self.categories = sorted(categories2)
            self.names = sorted(names2)
            self.ingredients = sorted(ingredients2)
            self.glassTypes = sorted(glassTypes2)
    
    def __init__(self, root):
        super().__init__(root, bg=mainBGColour)

        self.f = open("recipes.JSON", "r")
        self.recipes = json.load(self.f)

        #findGarnishes(self.recipes)
        self.getSearchables(self.recipes)

        self.currentPageIndex = 0
        self.pages = [self.Page0, self.Page1, self.Page2]

        self.mainFrame = self
        self.mainFrame.pack(fill=BOTH, expand=True)
        self.mainFrame.columnconfigure(0, weight=1)
        self.mainFrame.rowconfigure(0, weight=1)
        
        self.pages[self.currentPageIndex]()

    def getRecipesByCategory(self, colour):
        recipeList = []
        for recipe in self.recipes['recipies']:
            if (recipe['colour'] == colour) | (colour == 'None') | (colour == 'Any'):
                recipeList.append(recipe)
        self.addRecipeButtons(recipeList)

    def getRecipesByIngredient(self, ingredient):
        recipeList = []
        for recipe in self.recipes['recipies']:
            for ing in recipe['ingredients']:
                if SequenceMatcher(a=ing['name'],b=ingredient).ratio() > 0.75:
                    recipeList.append(recipe)
                    break
        self.addRecipeButtons(recipeList)


    def getRecipesByGlassType(self, glassType):
        recipeList = []
        for recipe in self.recipes['recipies']:
            if (recipe['glassType'] == glassType):
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
        self.buttonImage = PhotoImage(file = os.path.join(dirname, "images\\buttons\\btn1.png"))
        x = 0
        for recipe in recipes:
            if (x % 4 == 0) & (x > 0):
                self.left=5
                self.top = self.top + self.h + 10
                self.rows = self.rows + 1

            action_with_arg = partial(self.openRecipe, recipe)
            self.btn = Button(self.midPayne, width=self.w, height=self.h, highlightthickness=0, borderwidth=0, padx=0, pady=0, image=self.buttonImage, compound="center", text=recipe['name'], command=action_with_arg)
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

        self.midPayneContainerContainer = Frame(self.mainFrame, bg=secondaryBGColour)
        self.midPayneContainer = Frame(self.midPayneContainerContainer)
        self.midPayne = Canvas(self.midPayneContainer, highlightthickness=0, bg=secondaryBGColour, scrollregion="0 0 2000 1000", width=805, height=450)
        self.midPayne.bind("<MouseWheel>", self.scrollMainPageRecipes)
        self.vbar=Scrollbar(self.midPayneContainer, orient=VERTICAL)
        self.vbar.pack(side=RIGHT, fill=Y)
        self.vbar.config(command=self.midPayne.yview)
        self.midPayne.config(yscrollcommand=self.vbar.set)
        self.getRecipesByCategory('Any')
        self.midPayne.pack()

        self.upDownBtnFrame = Frame(self.midPayneContainerContainer, bg=secondaryBGColour)
        action_with_arg2 = partial(self.recipesMove, -1)
        self.upBtn = Button(self.upDownBtnFrame, width=75, height=75, highlightthickness=0, borderwidth=0, padx=0, pady=0, image=self.buttonImage, compound="center", text='up', command=action_with_arg2)
        self.upBtn.pack(side=TOP, pady=10)
        action_with_arg3 = partial(self.recipesMove, 1)
        self.downBtn = Button(self.upDownBtnFrame, width=75, height=75, highlightthickness=0, borderwidth=0, padx=0, pady=0, image=self.buttonImage, compound="center", text='down', command=action_with_arg3)
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
        self.categoryBox = ttk.OptionMenu(self.categoryFrame, self.categoryString, list(self.categories)[0], *self.categories, command=self.pickCategory)
        self.categoryBox.configure(width=25)
        self.categoryBox.pack(ipadx=20, ipady=10, side=BOTTOM)
        self.categoryFrame.pack(side=LEFT, padx = 25, pady=5)

        self.ingredientsFrame = Frame(self.bottomPayne, bg=mainBGColour)
        self.ingredientsLabel = Label(self.ingredientsFrame, bg=mainBGColour, fg=mainFGColour, font=smallFont, text='Ingredient:')
        self.ingredientsLabel.pack(side=TOP)
        if self.ingredients.__contains__('Any') == False:
            self.ingredients.insert(0, 'Any')
        self.ingredientsString = StringVar(self.ingredientsFrame) 
        self.ingredientsBox = ttk.OptionMenu(self.ingredientsFrame, self.ingredientsString, list(self.ingredients)[0], *self.ingredients, command=self.pickIngredient)
        self.ingredientsBox.configure(width=25)
        self.ingredientsBox.pack(ipadx=20, ipady=10, side=BOTTOM)
        self.ingredientsFrame.pack(side=LEFT, padx = 25, pady=5)

        self.glassFrame = Frame(self.bottomPayne, bg=mainBGColour)
        self.glassLabel = Label(self.glassFrame, bg=mainBGColour, fg=mainFGColour, font=smallFont, text='Glass Type:')
        self.glassLabel.pack(side=TOP)
        if self.glassTypes.__contains__('Any') == False:
            self.glassTypes.insert(0, 'Any')
        self.glassTypeString = StringVar(self.glassFrame) 
        self.glassTypeBox = ttk.OptionMenu(self.glassFrame, self.glassTypeString, list(self.glassTypes)[0], *self.glassTypes, command=self.pickGlassType)
        self.glassTypeBox.configure(width=25)
        self.glassTypeBox.pack(ipadx=20, ipady=10, side=BOTTOM)
        self.glassFrame.pack(side=LEFT, padx = 25, pady=5)

        self.bottomPayne.pack()

    def Page1(self):

        self.topPayne = Canvas(self.mainFrame, highlightthickness=0, bg='gray30', width=1024, height=100);
        self.topPayne.pack(side=TOP)
        self.topPayne.pack_propagate(0)

        self.btn = Button(self.topPayne, text="Return", font=subTitleFont, command=self.homepage)
        self.btn.pack(side=LEFT, padx=25, pady=25)

        self.cocktailName = Label(self.topPayne, bg='gray30', text="name", font=titleFont)
        self.cocktailName.pack(side=LEFT, padx=25, pady=25)


        self.leftPaynesContainer = Frame(self.mainFrame)

        self.bottomLeftPayneContainer = Frame(self.leftPaynesContainer)
        self.bottomLeftPayne = Canvas(self.bottomLeftPayneContainer, highlightthickness=0, bg='gray30', scrollregion="0 0 2000 1000", width=324, height=230)
        self.bottomLeftPayne.bind("<MouseWheel>", self.scrollRecipeIngredients)
        self.vbar2=Scrollbar(self.bottomLeftPayneContainer, orient=VERTICAL)
        self.vbar2.pack(side=RIGHT, fill=Y)
        self.vbar2.config(command=self.bottomLeftPayne.yview)
        self.bottomLeftPayne.config(yscrollcommand=self.vbar2.set)
        self.cocktailIngredients = Text(self.bottomLeftPayne, font=font, width=31, bg='gray50', borderwidth=0, wrap=WORD)
        self.cocktailIngredients.bind("<MouseWheel>", self.scrollRecipeIngredients)
        self.bottomLeftPayne.create_window((5, 5), anchor=NW, window=self.cocktailIngredients)
        self.bottomLeftPayne.pack()
        self.bottomLeftPayneContainer.pack(side=TOP, padx=0, pady=0)


        self.underLeftPayneContainer = Frame(self.leftPaynesContainer)
        self.underLeftPayne = Canvas(self.underLeftPayneContainer, highlightthickness=0, bg='gray30', scrollregion="0 0 2000 1000", width=342, height=260)

        self.image = PhotoImage(file=os.path.join(dirname, "images\\glasses\\None.png"))
        self.glassImage = Label(self.underLeftPayne, image=self.image, width=32, height=32)
        self.glassImage.pack(side=RIGHT, anchor="n")



        self.underLeftPayne.pack()
        self.underLeftPayne.pack_propagate(0)
        self.underLeftPayneContainer.pack(side=BOTTOM, padx=0, pady=0)

        self.leftPaynesContainer.pack(side=LEFT, padx=5, pady=5)

        self.bottomRightPayneContainer = Frame(self.mainFrame)
        self.bottomRightPayne = Canvas(self.bottomRightPayneContainer, highlightthickness=0, bg='gray30', scrollregion="0 0 2000 1000", width=700, height=500)
        self.bottomRightPayne.bind("<MouseWheel>", self.scrollRecipeSteps)
        self.vbar3=Scrollbar(self.bottomRightPayneContainer, orient=VERTICAL)
        self.vbar3.pack(side=RIGHT, fill=Y)
        self.vbar3.config(command=self.bottomRightPayne.yview)
        self.bottomRightPayne.config(yscrollcommand=self.vbar3.set)
        self.cocktailSteps = Text(self.bottomRightPayne, font=font, width=63, bg='gray50', borderwidth=0, wrap=WORD)
        self.cocktailSteps.bind("<MouseWheel>", self.scrollRecipeSteps)
        self.bottomRightPayne.create_window((5, 5), anchor=NW, window=self.cocktailSteps)
        self.bottomRightPayne.pack()
        self.bottomRightPayneContainer.pack(side=RIGHT, padx=5, pady=5)




        self.cocktailGarnish = Label(self.mainFrame, text="garnish")
        self.cocktailGarnish.pack()

        self.cocktailGlass = Label(self.mainFrame, text="glass")
        self.cocktailGlass.pack()


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
        self.getRecipesByCategory(self.categoryString.get())

    def pickIngredient(self, event):
        self.getRecipesByIngredient(self.ingredientsString.get())

    def pickGlassType(self, event):
        self.getRecipesByGlassType(self.glassTypeString.get())

    def openRecipe(self, recipe):
        self.scrollPos = self.vbar.get()[0]
        self.currentPageIndex = 1
        for child in self.mainFrame.winfo_children():
            child.destroy()
        self.pages[self.currentPageIndex]()

        self.cocktailName.config(text=recipe['name'])
        
        self.cocktailIngredients.delete(1.0, END)

        for ingredient in recipe['ingredients']:
            dots = ""
            for x in range(28 - (len(ingredient['name']) + len(ingredient['quantity']) + len(ingredient['unit']))):
                dots = dots + "."
            self.cocktailIngredients.insert(END, "\u2022 " + ingredient['name'] + dots + ingredient['quantity'] + ingredient['unit'] + "\n\n")
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

        
        

        self.cocktailGarnish.config(text=recipe['garnish'])
        self.cocktailGlass.config(text=recipe['glassType'])

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