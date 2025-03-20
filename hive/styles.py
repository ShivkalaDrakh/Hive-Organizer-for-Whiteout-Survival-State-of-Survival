import os
import tkinter as tk 
from tkinter import ttk
from copy import deepcopy

#color dictionary
used_colors = { "assign":"#99ee99",
                "current" : "#e9e999",
                "text" : "#dab55d",
                "floor" : "#606b82",
                "city" : "#ff4e45",
                "flag" : "#7f7f7f",
                "rock" : "#454a7d",
                "hq" : "#135d96",
                "trap" : "#60c5f4",
                "castle" : "orange",
                "tower" : "orange",
                "erase1" : "purple",
                "erase2" : "red",
                "canvas_bg" : "#bac1dc" 
                   }

# make a copy of the default values, as "used_colors" changes
used_colors_default = deepcopy(used_colors)

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
    #add background color to dictionary
    bg_color = style.lookup('TButton.label','background')
    used_colors.update({'bg':bg_color})
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
    style.configure('Current.TEntry',fieldbackground=used_colors["current"])
    style.configure('Assign.TEntry',fieldbackground=used_colors["assign"])
    return style