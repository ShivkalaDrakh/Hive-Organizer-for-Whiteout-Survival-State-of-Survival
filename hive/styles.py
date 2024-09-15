import os
import tkinter as tk 
from tkinter import ttk

#color dictionary
used_colors = { "assign":"#99ee99",
                "current" : "#e9e999",
                "text" : 'orange',
                "floor" : "#dd6666",
                "city" : "grey",
                "flag" : "cyan",
                "rock" : "black",
                "hq" : "green",
                "trap" : "yellow",
                "erase1" : "purple",
                "erase2" : "red" 
                   }

def initStyle(win, theme='black'):
    #define the style of ttk 
    # win: tk.Tk or tk.Tk.Toplevel
    
    # directory with the styles
    init_dir=os.path.dirname(os.path.realpath(__file__))
    #ttk styles
    style = ttk.Style()
    #theme='black'
    win.tk.call("source",os.path.join(init_dir,theme,theme+".tcl"))

    style.theme_use(theme)
    style.configure('TButton', padding= [4,2,4,2], anchor=tk.CENTER)
    style.map('TButton',
        relief=[('pressed', 'sunken'),
                ('!pressed', 'raised')])   

    style.configure('Assign.TButton')
    style.map('Assign.TButton',
        foreground=[('pressed','black'),('active', 'blue')],
        background=[('disabled', 'grey'),
                    ('pressed', used_colors["assign"]),
                    ('active', used_colors["current"])],       
        highlightcolor=[('focus', 'green'),
                        ('!focus', 'red')])
            
    style.configure('Build.TButton')
    style.map('Build.TButton',
        foreground=[('active','blue'),
                    ('!active','black')],
        background=[('active', used_colors["flag"]),
                    ('!active','white')],
        relief=[('pressed', 'sunken'),
                ('!pressed', 'raised')])
    
    style.configure('City.Build.TButton')
    style.map('City.Build.TButton', 
                    background=[('active', used_colors["city"]),
                    ('!active','pressed', used_colors["city"]), 
                    ('!active','white')]) 

    style.configure('Flag.Build.TButton')
    style.map('Flag.Build.TButton', 
                    background=[('active', used_colors["flag"]),
                    ('!active','pressed', used_colors["flag"]), 
                    ('!active','white')]) 

    style.configure('Rock.Build.TButton')
    style.map('Rock.Build.TButton', 
                    foreground=[('active','blue'),  
                                ('!active','pressed', 'white'),
                                ('!active','black')],
                    background=[('active', used_colors["rock"]),
                    ('!active','pressed', used_colors["rock"]), 
                    ('!active','white')]) 

    style.configure('HQ.Build.TButton')
    style.map('HQ.Build.TButton', 
                    background=[('active', used_colors["hq"]),
                    ('!active','pressed', used_colors["hq"]), 
                    ('!active','white')]) 

    style.configure('Trap.Build.TButton')
    style.map('Trap.Build.TButton', 
                    background=[('active', used_colors["trap"]),
                    ('!active','pressed', used_colors["trap"]), 
                    ('!active','white')]) 
    
    style.configure('CG.TButton')                     
    style.map('CG.TButton',
        highlightcolor=[('focus', 'green'),
                        ('!focus', 'red')])
    
    style.configure('Erase.TButton',
        padding= [20,2]) 
    style.map('Erase.TButton',       
                    background=[('pressed', used_colors["erase2"]),
                                ('!pressed',used_colors["erase1"])])                 
    style.map('Erase.TButton',
        highlightcolor=[('focus', 'green'),
                        ('!focus', 'red')],
        relief=[('pressed', 'sunken'),
                ('!pressed', 'raised')])
    return style