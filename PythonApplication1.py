from ast import Str
import json
from tkinter import *
import os
import tkinter
from tkinter.messagebox import showerror
from tkinter.font import Font
dirname = os.path.dirname(__file__)
from functools import partial

def on_escape(event=None):
    root.destroy()

class Application(Frame):

    scrollPos = 0;

    def __init__(self, root):
        super().__init__(root, bg='#111111')

        self.f = open("recipes.JSON", "r")
        self.recipes = json.load(self.f)
        
        self.currentPageIndex = 0
        self.pages = [self.Page0, self.Page1, self.Page2]

        self.font = Font(family="Courier new", size=13, weight="bold")

        self.mainFrame = self
        self.mainFrame.pack(fill=BOTH, expand=True)
        self.mainFrame.columnconfigure(0, weight=1)
        self.mainFrame.rowconfigure(0, weight=1)
        
        self.pages[self.currentPageIndex]()


    def Page0(self):

        self.topPayne = Canvas(self.mainFrame, highlightthickness=0, bg='red', width=1024, height=50);
        self.topPayne.pack()

        self.midPayneContainer = Frame(self.mainFrame)
        self.midPayne = Canvas(self.midPayneContainer, highlightthickness=0, bg='green', scrollregion="0 0 2000 1000", width=805, height=450)
        self.midPayne.bind("<MouseWheel>", self.scrollMainPageRecipes)
        self.vbar=Scrollbar(self.midPayneContainer, orient=VERTICAL)
        self.vbar.pack(side=RIGHT, fill=Y)
        self.vbar.config(command=self.midPayne.yview)
        self.midPayne.config(yscrollcommand=self.vbar.set)
        
        self.totalButtons = 501
        self.w = 190
        self.h = 100
        self.rows = 1
        self.top = 5
        self.left = 5
        self.buttonImage = PhotoImage(file = os.path.join(dirname, "images\\buttons\\btn1.png"))
        x = 0
        for recipe in self.recipes['recipies']:
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

        self.midPayne.pack()
        self.midPayne.configure(scrollregion=(0, 0, ((self.w * 4) + 25), (((self.h * self.rows) + (10 * (self.rows + 1)))-5)))
        self.midPayneContainer.pack(pady=25)
        

        self.bottomPayne = Canvas(self.mainFrame, highlightthickness=0, bg='blue', width=1024, height=50);
        self.bottomPayne.pack()



    def Page1(self):

        self.topPayne = Canvas(self.mainFrame, highlightthickness=0, bg='gray30', width=1024, height=100);
        self.topPayne.pack(side=TOP)
        self.topPayne.pack_propagate(0)

        self.btn = Button(self.topPayne, text="Return", font=('Arial', 36), command=self.homepage)
        self.btn.pack(side=LEFT, padx=25, pady=25)

        self.cocktailName = Label(self.topPayne, bg='gray30', text="name", font=('Arial', 36))
        self.cocktailName.pack(side=LEFT, padx=25, pady=25)


        self.leftPaynesContainer = Frame(self.mainFrame)

        self.bottomLeftPayneContainer = Frame(self.leftPaynesContainer)
        self.bottomLeftPayne = Canvas(self.bottomLeftPayneContainer, highlightthickness=0, bg='gray30', scrollregion="0 0 2000 1000", width=324, height=230)
        self.bottomLeftPayne.bind("<MouseWheel>", self.scrollRecipeIngredients)
        self.vbar2=Scrollbar(self.bottomLeftPayneContainer, orient=VERTICAL)
        self.vbar2.pack(side=RIGHT, fill=Y)
        self.vbar2.config(command=self.bottomLeftPayne.yview)
        self.bottomLeftPayne.config(yscrollcommand=self.vbar2.set)
        self.cocktailIngredients = Text(self.bottomLeftPayne, font=self.font, width=31, bg='gray50', borderwidth=0, wrap=WORD)
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
        self.cocktailSteps = Text(self.bottomRightPayne, font=self.font, width=63, bg='gray50', borderwidth=0, wrap=WORD)
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


    def scrollMainPageRecipes(self, event):
        self.midPayne.yview_scroll(int(-1*(event.delta/120)), "units")

    def scrollRecipeIngredients(self, event):
        self.bottomLeftPayne.yview_scroll(int(-1*(event.delta/120)), "units")

    def scrollRecipeSteps(self, event):
        self.bottomRightPayne.yview_scroll(int(-1*(event.delta/120)), "units")

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
        line_height = self.font.metrics("linespace")
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
        line_height = self.font.metrics("linespace")
        num_lines = self.cocktailSteps.count('1.0', END, 'displaylines')[0]
        total_height = line_height * num_lines + 10
        self.cocktailSteps.config(height=(num_lines))
        self.bottomRightPayne.configure(scrollregion=(0, 0, 1000, max(total_height, self.bottomRightPayne.winfo_height())))

        
        

        self.cocktailGarnish.config(text=recipe['garnish'])
        self.cocktailGlass.config(text=recipe['glassType'])


root = Tk()

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
#root.attributes("-fullscreen", True)
#root.wm_attributes("-topmost", True)
root.bind("<Escape>", on_escape)
root.wm_geometry("1024x600")
root.resizable(width=False, height=False)

applicationInstance = Application(root)















root.mainloop()
