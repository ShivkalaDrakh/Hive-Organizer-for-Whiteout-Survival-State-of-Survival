"""
Hive Organizer for Whiteout Survival and State of Survival
Copyright (C) 2024/2025 Mark Hartrampf

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import tkinter as tk
import re
#import math
import os
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter import ttk
from tkinter.colorchooser import askcolor
from PIL import Image, ImageTk, ImageGrab
from copy import deepcopy
import json
from hive.utils import VerticalScrolledFrame, ScrolledFrame, callweb, listadd, listsub, center, find, getPoly, rot, findMenuIndex
from hive.styles import initStyle, used_colors, used_colors_default
from hive.canvas import *

Version = "V0.3"
#TODO for V0.3:
# - Menus and Keyboard Short Cuts -> partially done
# - color selection for all buildings -> Done
# - Remove erased cities from Assignement List and also delete name pop-up -> Done
# - Add columns to MembersList (e.g. Furnace Level, Power, Rank) -> Done
# - Allow configuration of those additional columns via menubar -> Done
# - add button to enter more embers in member list
#NICE TO HAVE for 0.3:
# - 
# script dir will be used as initial for load/save
script_dir=os.path.dirname(os.path.realpath(__file__))
init_dir =os.path.join(script_dir,'hive')
save_dir = os.path.join(init_dir,'save')

class Member():
    def __init__(self, number=0, name='', coords='[ ---, --- ] ',power="100.0M",level='FC1',rank='R1',status='', 
                 city_id=None, widget = None, coord_widget = None, canvas = None):
        self.number=number
        self.name = tk.StringVar(value=name)
        self.coords = coords
        self.power = tk.StringVar(value=power)
        self.level = tk.StringVar(value=level)
        self.rank = tk.StringVar(value=rank)
        self.status = status
        self.city_id = city_id
        self.widget = widget
        self.coord_widget = coord_widget
        self.canvas = canvas

    def setColor(self):
        if "current line;" in self.status:
            self.widget.config(style='Current.TEntry')
        elif "assigned;" in self.status:
            self.widget.config(style='Assign.TEntry')
        else:
            self.widget.config(style='TEntry')

    def changeState(self, state=""):
        change = False
        if "!current" in state:
            self.status =self.status.replace("current line;","")
            change = True
            self.setCityHighlight(highlight=False)
        if "!assigned" in state:
            self.status =self.status.replace("assigned;","")
            change = True
            self.setCityHighlight(highlight=False)
        if "new current" in state:    
            self.status += "current line;"
            change = True
            #highlight assigned city
            if "assigned;" in self.status:
                self.setCityHighlight(highlight=True)
        if "new assigned" in state:    
            self.status += "assigned;"
            change = True
        self.setColor()
        return change    

    def setCityHighlight(self, highlight=True):
        #set or reset the city highlight
        if highlight:
            bg = used_colors['current']
            fg = 'black'
        else:
            bg = used_colors['city']
            fg = used_colors['assign']
        if self.city_id is not None:
            try:
                self.canvas.itemconfig(self.city_id, fill=bg)
                block = self.canvas.getBuildingFromId(self.city_id)
                if block is not None:
                    text_id = block.id['text']
                    #set textcolor according to block setting
                    self.canvas.itemconfig(text_id,fill=fg)
            except AttributeError:
                pass

class MembersList(tk.Toplevel):
    # Defines the window with the list of member names
    def __init__(self,lines,geometry='100x100+100+100'):
        super().__init__()
        self.style = self.master.style
        self.lines = lines
        self.members=[]
        self.column_mode = [tk.IntVar(value=1), tk.IntVar(value=1), tk.IntVar(value=1)]

        #build member list and show in seperate Window
        self.title("Alliance Members List")
        self.geometry(geometry)
        #add border
        self.config(bd=3, bg=used_colors['bg'])

        #canvas for List header
        self.head_canvas = tk.Canvas(self,bg=used_colors['bg'],bd = 0, height=20, highlightthickness=0)
        self.head_canvas.pack(fill='x')

        # frame with actual list
        # the data is in the frame inside the scroll frame
        self.scroll_frame = VerticalScrolledFrame(self)
        self.scroll_frame.pack(fill='both', expand=True)
        self.new_frame = self.scroll_frame.interior
        #self.new_frame.columnconfigure(1, weight=1)

        #self.head_canvas.columnconfigure(1, weight=1)
        #add members, to be filled in addMember
        for line in lines:
            mem_attr = line.split(';')
            #if power, level, and rank are there, use them, otherwise default them
            if len(mem_attr) == 1:
                self.members.append(Member(name=mem_attr[0].strip()))
            elif len(mem_attr) == 2:
                self.members.append(Member(name=mem_attr[0].strip(),power=mem_attr[1].strip()))
            elif len(mem_attr) == 3:
                self.members.append(Member(name=mem_attr[0].strip(),power=mem_attr[1].strip(),level=mem_attr[2].strip()))
            elif len(mem_attr) == 4:
                self.members.append(Member(name=mem_attr[0].strip(),power=mem_attr[1].strip(),
                                    level=mem_attr[2].strip(),rank=mem_attr[3]))       
            else:
                if mem_attr[2].strip().isdecimal():
                    mem_attr[2] = "FC"+mem_attr[2].strip()

                self.members.append(Member(name=mem_attr[0].strip(),power=mem_attr[1].strip(),
                                    level=mem_attr[2].strip(),rank=mem_attr[3]))
        self.setup()
        self.update()

        # add (empty) menubar
        self.mB = tk.Menu(self)
        self['menu'] = self.mB
        self.configMenu = tk.Menu(self.mB, tearoff=0)
        #self.configMenu.add_command(label='Close',command=self.remove)
        #set all columns to on by default:
        self.power_mode = tk.IntVar(value=1)
        self.lvl_mode = tk.IntVar(value=1)
        self.rank_mode = tk.IntVar(value=1)
        self.configMenu.add_checkbutton(label='Show Power',  
                                      variable=self.column_mode[0], command=self.columnMode)
        self.configMenu.add_checkbutton(label='Show Level',  
                                      variable=self.column_mode[1], command=self.columnMode)
        self.configMenu.add_checkbutton(label='Show Rank',  
                                      variable=self.column_mode[2], command=self.columnMode)
        self.configMenu.add_separator()
        #move from update button to menu action to update Coordinates
        self.configMenu.add_command(label='Update Coordinates',accelerator='Ctrl+U',command=self.updateCoordinates)
        self.bind("<Control-u>", self.updateCoordinates)
        self.configMenu.add_separator()
        
        #also remove the close butten and make it a command
        self.configMenu.add_command(label='Close Members List',accelerator='Alt+F4',command=self.closeML)
        # Alt-F4 is already defined, no need to bind it again
        self.mB.add_cascade(label='Config', menu=self.configMenu)
        
        #adjust header
        self.generateHeader()
        
        self.update()

    def setup(self):
        self.ml = []
        self.names = []
        self.power = []
        self.level = []
        #for i, member in enumerate(self.members):
        for member in self.members:
            self.addMember(member)

    def generateHeader(self):
        #remove old header widgets if any
        self.head_canvas.delete(*self.head_canvas.find_all())
            
        header_names = ['ID','Member Name','Coords']
        additional_columns = ['Power','Lvl', 'Rank']
        for i, add_col in enumerate(additional_columns):
            #if column is activated add header name
            if self.column_mode[i].get():
                header_names.append(add_col) 
        for i, head in enumerate(header_names):
            bbox = self.new_frame.grid_bbox(i, 0)
            #add the padding in x and center in y
            #self.head_canvas.create_text(bbox[0]+0,bbox[1]+10,text=head,anchor=tk.W,fill = 'white')
            self.head_canvas.create_text(bbox[0]+bbox[2]/2,bbox[1]+int(self.head_canvas.cget('height'))/2,text=head,anchor=tk.CENTER,fill = 'white')
            self.head_canvas.addtag_withtag(head,i)
        #correct width of window
        need = bbox[0]+bbox[2]
        #DEBUG
        self.new_frame.config(width=need)
        self.scroll_frame.config(width=need)
        #only change width with colum number
        #height is at least as high as main window
        #16 px is the width of the scrollbar (needs to be added to make it look better)
        self.minsize(need+16, self.master.winfo_height())
        self.maxsize(need+16, 2048)
        #ttk.Label(self, width=need).pack()

    def columnMode(self):
        #change columns and build list anew
        #destroy old list and build it anew
        self.scroll_frame.destroy()
        #and remove 'current' status from current member
        cur_member = find(lambda my: "current line;" in my.status, self.members)
        if cur_member:
            cur_member.status =cur_member.status.replace("current line;","")
        # the data is in the frame inside the scroll frame
        self.scroll_frame = VerticalScrolledFrame(self)
        self.scroll_frame.pack(fill='both', expand=True)
        self.new_frame = self.scroll_frame.interior
        #self.new_frame.columnconfigure(1, weight=1)

        self.setup()
        self.update()
        #add and remove columns that are selected
        self.generateHeader()

    def selectName(self,event, var):
        #select the klicked name
        member_name = var.get()
        #remove old current line
        old_cl = find(lambda my: "current line;" in my.status, self.members)
        if old_cl:
            old_cl.changeState("!current")
            old_cl.setColor()

        member = find(lambda my: my.name.get() == member_name, self.members)
        #add new current line
        if not member:
            member=Member(name=member_name)
        member.changeState("new current")

    def remove(self):
        #check if there are any assignments
        #if yes, warn window
        #if not, destroy
        if find(lambda my: "assigned;" in my.status, self.members):
            response = self.master.warnWindow('Closing Members List will remove current assignments!\nDo you want to proceed?', buttons = 2, b_text=['Yes','No'])
        else:
            self.destroy() 
            return
        if response == 'yes':  
            cities=self.master.paint_canvas.cities
            for member, city in cities.items():
                self.removeCityAssignment(city, member)
            #clear cities as removeCityAssignment doesn't do this at the moment
            cities.clear()
            self.destroy()  

    def updateCoordinates(self, event= None):
        canvas = self.master.paint_canvas
        for member in self.members:
            if "assigned;" in member.status:
                canvas.showMemberCoords(member)
        #self.updateHeader()

    def updateHeader(self): 
        #just an alias for self.head_canvas.update()
        """self.update()
        for id in self.head_canvas.find_all():
            new_x = self.new_frame.grid_bbox(id-1, 0)[0]
            own_x = self.head_canvas.bbox(id)[0]
            self.head_canvas.move(id,new_x-own_x,0)"""
        self.head_canvas.update()

    def removeCityAssignment(self, city, member_name):
        #remove the city from the assignment list and delete the number
        canvas = self.master.paint_canvas
        #find city on canvas
        text_field = set(canvas.find_overlapping(*canvas.coords(city))).intersection(set(canvas.find_withtag('member')))
        #remove number
        canvas.delete(*text_field)
        #remove tag
        canvas.dtag(city, member_name)

        member = find(lambda my: my.name.get() == member_name,self.members)
        if member:
            member.changeState("!assigned")
            member.city_id = None
            member.coords = [0, 0]
            member.coord_widget.config(text='[ ---, --- ]')

        #remove from list of assigned cities
        #TODO: this doesn_t work with iterations
        #canvas.cities.pop(member_name)

    def merge(self,new_members):
        #merge new list of names with existing one

        for new_member in new_members:
            #remove whitespaces and CR at start and end of name
            new_member=new_member.strip()
            #Is member in list already?
            member = find(lambda my: my.name.get() == new_member, self.members)
            if not member:
                self.members.append(Member(name=new_member))
                self.addMember(self.members[-1])

    def checkWidget(self,member, *argv):
        #a change in the name has also to be traced to assigned cities, if any!
        canvas = self.master.paint_canvas
        new_name = member.name.get()
        try:
            city = canvas.cities[member.save_name]
            canvas.cities.pop(member.save_name)
            canvas.cities.update({new_name: city})
            #also update the tag of the city in question
            canvas.addtag_withtag(new_name, city)
            #and remove old tag
            canvas.dtag(city, member.save_name)
            canvas.assignments[city] = new_name
            #and bind the keys
            #bind to the city (not the text!)
            canvas.tag_bind(new_name,'<Enter>',func=lambda event: showAssignment(event=event,canvas = canvas))
            canvas.tag_bind(new_name,'<Leave>',func=lambda event: showAssignment(event=event,canvas = canvas))
        #exception if Member was not yet assigned
        except KeyError:
            pass
        
        #DEBUG
        print(canvas.assignments[city],member.save_name,member.name.get())
        #END DEBUG
        #update old name
        member.save_name = member.name.get()
        return True

    def addMember(self, member):
        #add new member to MembersList
        self.names.append(member.name)        
        new_idx = len(self.names)
        member.save_name = member.name.get()
        member.name.trace_add('write', lambda *pargs: self.checkWidget(member, *pargs)) #DEBUG
        member.number= new_idx
        ml_number = ttk.Label(self.new_frame,style='TLabel',text=str(new_idx))
        ml_number.grid(row=new_idx,column=0, sticky='news')
        #Name entry: How to allow selection for assignment after name change?
        #checkCommand= (self.register(self.checkWidget), '%s','%P','%W')
        
        ml_entry = ttk.Entry(self.new_frame,style='TEntry',textvar=member.name, width=20)
                             #validate='key', validatecommand=checkCommand)

        ml_entry.grid(row=new_idx,column=1, sticky='news')
        member.widget = ml_entry
        ml_coords = ttk.Label(self.new_frame,style='TLabel',text=str(member.coords))
        ml_coords.grid(row=new_idx,column=2, padx= 2, sticky='news')
        member.coord_widget = ml_coords
        # Add new columns here if neccessary
        new_columns = [member.power, member.level,member.rank]
        col_width = [6,4,3]
        ml_extra= ['' for a in range(len(new_columns))]
        #also specify number of columns that are fixed
        num_fixed_col = 3
        #if column is set, make Entry, otherwise skip
        i=0
        for c, col_conf in enumerate(self.column_mode):
            if col_conf.get() == 1:
                ml_extra[i]=ttk.Entry(self.new_frame,style='TEntry',textvar=new_columns[c],
                           width=col_width[c])
                ml_extra[i].grid(row=new_idx,column=num_fixed_col+i, padx= 2, sticky='news')
                i+=1
        ml_entry.bind('<Button-1>', func=lambda event,var = member.name: self.selectName(event,var))
        #ml_entry.bind('<ButtonRelease-1>', func=lambda event,var = self.names[new_idx-1]: self.selectName(event,var))
        self.ml.append((ml_number,ml_entry, ml_coords, *ml_extra))

        #change state of old 'current' member
        cur_member = find(lambda my: "current line;" in my.status, self.members)
        if cur_member:
            cur_member.changeState('!current')
        #and make the new member the current one
        member.changeState("new current")

    def removeCurrent(self):
        #remove all 'current' tags
        for memb in self.members:
            memb.changeState("!current")

    def getLines(self):
        member_lines = []
        for member in self.members:
            member_lines.append(';'.join([member.name.get(),member.power.get(),member.level.get(),member.rank.get()]))
        return member_lines

    def closeML(self):
        #warning: closing ML will remove all assignments
        response = self.master.warnWindow('Closing MembersList will delete current \nassignments!\nDo you want to proceed?', buttons = 2, b_text=['Yes','No'])
        if response == 'yes':
            self.clearAssignments()
            self.destroy()

    def clearAssignments(self):
        #remove all assignments from current hive
        canvas = self.master.paint_canvas
        for member_name in canvas.cities.keys():
            old_city = canvas.cities[member_name]
            self.removeCityAssignment(old_city,member_name)
        #and set the list to 'empty'
        canvas.cities.clear()
        canvas.assignments.clear()
        #also remove the member state
        try:
            #remove active player tag
            for member in self.members:
                member.changeState("!assigned")
        except AttributeError:
            pass

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Hive Organizer '+Version+'\t'+chr(169)+' 2025 by Shivkala')
        self.file_name = ''
        #define buttons and button actions
        # size depending on screen size
        geo_fac = 0.5
        wwidth = self.winfo_screenwidth()*geo_fac
        wheight = self.winfo_screenheight()*geo_fac
        
        fpady = 3
        fpadx = 5
        self.trap_c = None
        #get style
        self.style = initStyle(self)

        #add list of buildings
        #self.buildings = set(['HQ','City','Flag','Trap','Rock','Castle','Tower'])
        self.buildings = ['City','Flag','HQ','Rock','Trap','Castle','Tower']

        #add border
        self.config(bd=3, bg=used_colors['bg'])

        #Frame for Buttons
        bt_frame=ttk.Frame(self, width = wwidth, height = 65)
        bt_frame.grid(row=0,column=0,sticky='news')
        bt_frame.columnconfigure(0,weight=1)
        
        #Frame for Canvas
        self.cs_frame= ScrolledFrame(self, width = wwidth, height = wheight)
        self.int_frame = self.cs_frame.interior
        self.int_frame.columnconfigure(0, weight=1)
        self.int_frame.rowconfigure(0, weight=1)
        self.upper_canvas = self.int_frame.master
        self.paint_canvas = PaintCanvas(self.int_frame, width=wwidth*2, height = wheight*2, bg=used_colors["canvas_bg"])
        
        #paint canvas
        self.cs_frame.grid(row=1,column=0,sticky='news')
        self.paint_canvas.pack(side=tk.LEFT,fill='both', expand=True)
        
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.upper_canvas.configure(width = wwidth, height = wheight)
        #calculate scrollregion
        self.update()
        size = (int(self.paint_canvas.cget('width')), int(self.paint_canvas.cget('height')))
        self.cs_frame.scrollArea(size)

        #first column:
        fc = 1
        self.bt_frame = bt_frame
        
        #add a bit of space in between
        self.dummy= ttk.Label(bt_frame)
        self.dummy.grid(row = 0, column=fc+7, sticky='news',padx=30, pady=fpady)
        #self.columnconfigure(fc+7, weight=1)

        self.isoview_button = ttk.Button(bt_frame, text='Isometric', style='TButton', command=self.isometricView)
        self.isoview_button.grid(row = 0, column=fc+9, sticky='news',padx=fpadx, pady=fpady)
        
        self.default_button = ttk.Button(bt_frame, text='Default', style='TButton', command=self.default)
        self.default_button.grid(row = 0, column=fc+10, sticky='nes',padx=fpadx, pady=fpady)

        #self.members_button = ttk.Button(bt_frame, text='Member List', command=self.fileMembersList)
        #self.members_button.grid(row = 0, column=fc+10, sticky='news',padx=fpadx, pady=fpady)

        self.assign_button = ttk.Button(bt_frame, text='Assign',style='Assign.TButton', command=self.assignMode)
        self.assign_button.grid(row = 0, column=fc+11, sticky='news',padx=fpadx, pady=fpady)

        #buildings
        #self.city_button = tk.Button(bt_frame, text='City', activebackground=City().color, command=self.printCity)
        self.city_button = ttk.Button(bt_frame, text='City',style='City.Build.TButton', command=self.printCity)
        self.city_button.grid(row = 1, column=fc+0, sticky='news',padx=fpadx, pady=fpady)

        self.flag_button = ttk.Button(bt_frame, text='Flag',style='Flag.Build.TButton', command=self.printFlag)
        self.flag_button.grid(row=1, column=fc+1, sticky='news',padx=fpadx, pady=fpady)

        self.rock_button = ttk.Button(bt_frame, text='Rock',style='Rock.Build.TButton', command=self.printRock)
        self.rock_button.grid(row=1, column=fc+2, sticky='news',padx=fpadx, pady=fpady)

        self.hq_button = ttk.Button(bt_frame, text=' HQ ',style='HQ.Build.TButton', command=self.printHQ)
        self.hq_button.grid(row=1, column=fc+3, sticky='news',padx=fpadx, pady=fpady)

        self.trap_button = ttk.Button(bt_frame, text='Trap',style='Trap.Build.TButton', command=self.printTrap)
        self.trap_button.grid(row=1, column=fc+4, sticky='news',padx=fpadx, pady=fpady)

        #Add refernece Trap Coordinates (Trap coordinates shown in the game are always SW corner!)
        self.trap_coord = tk.StringVar(master=bt_frame, value='X: 0, Y: 0')
        
        valCommand= (self.register(self.validateCoord), '%P')
        self.trap_clabel =ttk.Label(bt_frame,text='Trap Coords:',style='TLabel')
        self.trap_clabel.grid(row=0, column=fc+5, sticky='ews',padx=fpadx, pady=0)
        
        self.trap_entry = ttk.Entry(bt_frame,style='TEntry',textvar=self.trap_coord, width=15, 
                                    validate='key', validatecommand=valCommand)
        self.trap_entry.grid(row=1, column=fc+5, sticky='news',padx=fpadx, pady=fpady)
        self.trap_entry.state(['disabled'])

        # toggle buttons
        self.floor_button = ttk.Button(bt_frame, text='Show Floor',style='CG.TButton', command=self.raiseFloor)
        self.floor_button.grid(row=1, column=fc+7, sticky='e',padx=fpadx, pady=fpady)

        self.coord_button = ttk.Button(bt_frame, text='Coords',style='CG.TButton', command=self.printCoords)
        self.coord_button.state(['pressed'])
        self.coord_button.grid(row=1, column=fc+8, sticky='e',padx=fpadx, pady=fpady)

        self.grid_button = ttk.Button(bt_frame, text='Grid', style='CG.TButton', command=self.gridOnOff)
        self.grid_button.state(['pressed'])
        self.grid_button.grid(row=1, column=fc+9, sticky='ew',padx=fpadx, pady=fpady)
        self.grid_button.bind('<Button-3>', self.changeGridSize)

        self.zoom_button = ttk.Button(bt_frame, text='Zoom', style='CG.TButton',command=self.paint_canvas.zoom)
        self.zoom_button.grid(row=1, column=fc+10, sticky='ew',padx=fpadx, pady=fpady)

        self.erase_button = ttk.Button(bt_frame, text='Erase', style='Erase.TButton',command=self.eraseBuilding)
        self.erase_button.grid(row=1, column=fc+11, sticky='e',padx=fpadx, pady=fpady)

        #donate button
        db_im = Image.open(os.path.join(init_dir,'donate-button4.png'))
        db_im = db_im.resize((50,50))
        self.db_im = ImageTk.PhotoImage(db_im)
        
        self.donate_button = ttk.Button(bt_frame, image=self.db_im, command=self.donate, cursor='heart')
        #self.donate_button.grid(row = 0, column=12, sticky='ew',padx=fpadx, pady=fpady)
        self.donate_button.grid(row = 0, rowspan=2, column=fc+13, sticky='ew',padx=fpadx, pady=fpady)
        
        #last column
        lc = fc+14 
        bt_frame.columnconfigure(lc,weight=1)
        bt_frame.grid_propagate(False)

        self.iconbitmap(default = os.path.join(init_dir,'icon.ico'))
        
        #add menues
        self.menues()

        #draw default after starting mainloop
        self.after(100,self.setup())
        

    #function for Trap Coordinate Entry field
    def validateCoord(self, new_text):
            #TODO: Show limit of state on canvas
            max_coord = 1199
            min_coord = 0
            regex = r'X:\s*(\d*),\s*Y:\s*(\d*)'
            val_res = re.search(regex, new_text)

            #correct format?
            if val_res is None:
                return False
            else:
                try:
                    self.trap_c = [float(val_res.groups()[0]),float(val_res.groups()[1])]
                    #check correct boundaries
                    if max(self.trap_c) > max_coord or min(self.trap_c) < min_coord:
                        print(f'Trap Coordinates have to be between {min_coord} and {max_coord}')
                        return False
                    # In the game, trap coordinates are given for lower left corner, not center
                    # therefore half trap size has to be added in both x and y
                    if self.trap_c == [0, 0]:
                        self.resetTrapCoord()
                    else:
                        self.trap_c = listadd(self.trap_c,[Trap().size/2,Trap().size/2])
                    return True
                except ValueError:
                    return True

    def menues(self):
        top = self.winfo_toplevel()
        self.menuBar = tk.Menu(top)
        top['menu'] = self.menuBar
        # Menu for File Options
        # Hive Options
        
        self.fileMenu = tk.Menu(self.menuBar, tearoff=0)
        self.fileMenu.add_command(label='Load Hive',accelerator='Ctrl+L',command=self.loadLayout)
        self.bind("<Control-l>", self.loadLayout)
        self.fileMenu.add_command(label='Save Hive',accelerator='Ctrl+S',command=self.saveLayout)
        self.bind("<Control-s>", self.saveLayout)
        self.fileMenu.add_command(label='Save Hive As...',accelerator='Ctrl+Shift+S',command=lambda nf=True: self.saveLayout(new_file=nf))
        self.bind("<Control-S>", lambda e,nf=True: self.saveLayout(event=e,new_file=nf))
        
        self.fileMenu.add_separator()
        #MembersList Options
        self.fileMenu.add_command(label='Load MembersList',accelerator='Ctrl+O', command=self.loadMembersList)
        self.bind("<Control-o>", self.loadMembersList)
        self.fileMenu.add_command(label='Save MembersList',accelerator='Ctrl+M', command=self.saveMembersList)
        self.bind("<Control-m>", self.saveMembersList)
        
        self.fileMenu.add_separator()
        #Color Theme options
        self.fileMenu.add_command(label='Load Color Theme',accelerator='Ctrl+Shift+T', command=self.loadColors)
        self.bind("<Control-T>", self.loadColors)
        self.fileMenu.add_command(label='Save Color Theme',accelerator='Ctrl+T', command=self.saveColors)
        self.bind("<Control-t>", self.saveColors)
        
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label='Exit',accelerator='Ctrl+Q', command=self.quitDialog)
        self.bind("<Control-q>", self.quitDialog)
        #Menu for Mode Options
        self.modeMenu = tk.Menu(self.menuBar, tearoff=0)
        self.modeMenu.add_checkbutton(label='Assign Mode', accelerator='Ctrl+A',  
                                      variable=self.paint_canvas.assign_mode, command=self.assignMode)
        self.bind("<Control-a>", self.assignMode)
        self.modeMenu.add_checkbutton(label='Erase Mode', accelerator='Ctrl+E', 
                                      variable=self.paint_canvas.erase, command=self.eraseBuilding)
        self.bind("<Control-e>", self.eraseBuilding)

        #Menu for Colors
        self.colorMenu = tk.Menu(self.menuBar, tearoff=0)
        self.BuildingColors = tk.Menu(self.colorMenu, tearoff=0)
        for building in self.buildings:
            #how to prevent that building at command call is always last in list ('Tower')        
            self.BuildingColors.add_command(label=building, activebackground = used_colors[building.lower()], 
                                        command = lambda b=building: self.getcolor(b))
        #and one for the floor
        self.BuildingColors.add_command(label='Floor', activebackground = used_colors['floor'], 
                                        command = lambda: self.getcolor('floor'))
        self.colorMenu.add_cascade(label='Buildings', menu=self.BuildingColors)
        self.colorMenu.add_separator()
        self.colorMenu.add_command(label='Background', activebackground = used_colors['canvas_bg'],
                                   command = lambda: self.getcolor('canvas_bg'))
        self.colorMenu.add_separator()
        self.colorMenu.add_command(label='Default', command = lambda: self.getcolor('default'))
        self.menuBar.add_cascade(label='File', menu=self.fileMenu)
        self.menuBar.add_cascade(label='Modes', menu=self.modeMenu)
        self.menuBar.add_cascade(label='Colors', menu=self.colorMenu)

        self.update()

    def setup(self):
        #performed once mainloop is started
        self.paint_canvas.setup()
        self.active_button = None
        self.ML_width = 321

    def quitDialog(self,event=None,):
        #Ask for save hive or quit without saving
        #but only if anything exists on the canvas
        buildings_exist = max([len(self.paint_canvas.find_withtag(b)) for b in self.buildings ]) > 0
        if not buildings_exist:
            #without buildings, just quit
            self.quit()
            return
        # if there is at least one building, ask for save
        response = self.warnWindow('Save Hive before quitting??', buttons = 3, b_text=["Save Hive","Don't Save","Abort"])
        if response =="abort":
            return
        elif response=="save hive":
            self.saveLayout()
        self.quit()

    def getcolor(self, building):
        #change colors of buildings and floor
        global used_colors

        def ChangeBuildingColor(building):
            #find all buildings of the type
            # and change to new color
            new_paint=set(self.paint_canvas.find_withtag(building))
            #only change the color of the building, not its floor
            if building != 'floor':
                exclude_floor = set(self.paint_canvas.find_withtag('floor'))
                new_paint = new_paint.difference(exclude_floor)
            for id in new_paint:
                self.paint_canvas.itemconfig(id,fill=used_colors[building.lower()])
            
            #change button background
            button = building.capitalize()
            #HQ is special
            if button == "Hq":
                button = "HQ"
            if button in ['City','Flag','Rock', 'HQ','Trap']:
                self.style.map(button+'.Build.TButton', 
                    background=[('active', used_colors[button.lower()]),
                    ('!active','pressed', used_colors[button.lower()]), 
                    ('!active','white')]) 
        bblocks = deepcopy(self.buildings)
        #TODO: Not nice, can we use used_colors.keys() instead?
        bblocks.append('floor')
        bblocks.append('canvas_bg')
        #find position of canvas_bg in menu
        bg_pos = findMenuIndex(menu = self.colorMenu, label = "Background")
        if building.lower() in ['default', 'all']:
            if building.lower() == 'default':
                #reset all colors to default values
                for key in used_colors_default.keys():
                    used_colors[key] = used_colors_default[key]
            # repaint everything
            for block in bblocks:
                if block == 'canvas_bg':
                    self.paint_canvas.config(bg = used_colors[block])
                    #keep the separator in mind!
                    self.colorMenu.entryconfig(bg_pos, activebackground = used_colors[block.lower()])
                else:
                    ChangeBuildingColor(block)
                    self.BuildingColors.entryconfig(bblocks.index(block), activebackground = used_colors[block.lower()])
            return
        #get the new color and put it in the color directory
        new_color = askcolor(title='New Color')
        used_colors[building.lower()] = new_color[1]

        #if it's the background, don't change any buildings ;)
        if building.lower() == 'canvas_bg':
            self.paint_canvas.config(bg = new_color[1])
            #keep the separator in mind!
            self.colorMenu.entryconfig(bg_pos, activebackground = used_colors[building.lower()])
            return
        #change buildings of the changed type to the new color
        self.BuildingColors.entryconfig(bblocks.index(building), activebackground = used_colors[building.lower()])
        ChangeBuildingColor(building)
        
    def resetTrapCoord(self):
        #TODO: make inactive even if trap is there
        self.trap_c = None 
        self.trap_coord.set('X: 0, Y: 0')
        self.trap_entry.state(['disabled'])

    def donate(self, width=300, height=350):
        top=tk.Toplevel(self)
        top.details_expanded = False

        #position, width, and hight based on main window geometry
        top_x = int(self.winfo_x()+self.winfo_width()/2-150)
        top_y = self.winfo_y()+100

        top.title("Help Shivkala!")
        top.geometry("{}x{}+{}+{}".format(width, height, top_x, top_y))
        top.resizable(False, False)
        top_frame = ttk.Frame(top,width=width, height=height)
        top_frame.grid_propagate(0)
        top_frame.pack()

        text_label = ttk.Label(top_frame,wraplength=width-20,
                               text="If you use and like Hive Organizer, I would appreciate a small donation!\n\nThis allows me to further improve and update the tool.\n\nThink about it as buying a Pack in the Game!\n\nThere are \nCommon Donation Packs, \nEpic Donation Packs, \nand \nMythic Donation Packs ;)\n",
                               style='TLabel', justify='center', padding=[10,10,10,10])
        text_label.grid(row=0, column=0, columnspan=3)
        
        db_im2 = ImageTk.PhotoImage(Image.open(os.path.join(init_dir,'donate-button4.png')).resize((100,100)))
        dbtn = ttk.Button(top_frame,image=db_im2, style='TButton', command=lambda: callweb('https://www.paypal.com/donate/?hosted_button_id=J3NY5KH92LC7L'))
        dbtn.grid(row=1, column = 0)
        
        qr_im = ImageTk.PhotoImage(Image.open(os.path.join(init_dir,'Donate QR Code.png')).resize((100,100)))
        dlabel = ttk.Label(top_frame,image=qr_im,style='TLabel')
        dlabel.grid(row=1, column = 2)

        top.mainloop()

    def warnWindow(self, warning,  buttons=1, b_text=['OK'], width=300, height=100):
        # pop-up wwarning window
        # buttons: number of buttons in window
        # b_text: list of texts on button 
        #           also defines the response: response=b_text[button].lower()
        top = tk.Toplevel(self)
        top.details_expanded = False
        top.style = self.style
        #position, width, and hight based on main window geometry
        top_x = int(self.winfo_x()+self.winfo_width()/2-150)
        top_y = self.winfo_y()+100
        top.title("Warning")
        top.geometry("{}x{}+{}+{}".format(width, height, top_x, top_y))
        top.resizable(False, False)
        top_frame = ttk.Frame(top,width=width, height=height)
        top_frame.grid_propagate(0)
        top_frame.pack()

        top_frame.rowconfigure(0, weight=0)
        top_frame.rowconfigure(1, weight=1)
        #get weight on all columns
        for i in range(1,max(buttons+1,2)):
            top_frame.columnconfigure(i, weight=1)
        #...except the first
        top_frame.columnconfigure(0, weight=0)
        response = tk.StringVar()

        #top.style = self.style
        #put warning symbol and warning text
        ttk.Label(top_frame, image="::tk::icons::warning").grid(row=0, column=0, pady=(7, 0), padx=(7, 7), sticky="e")
        ttk.Label(top_frame, text=warning).grid(row=0, column=1, columnspan=buttons, pady=(7, 7), sticky="news")
        
        #add_buttons        
        warn_buttons = []
        for button in range(buttons):
            #define button action
            def responder(number=button):
                response.set(b_text[number].lower())
            warn_buttons.append(ttk.Button(top_frame, text=b_text[button], command=responder))
            warn_buttons[button].grid(row=1, column=button+1, padx=(7, 7), pady=(7, 7), sticky='news')

        # wait for a button to be clicked
        warn_buttons[0].wait_variable(response)
        top.destroy()
        return response.get()

    def default(self):
        #check if there are any buildings already on the canvas
        #if so warn about deletion
        if self.paint_canvas.find_withtag('building'):
            response = self.warnWindow('Default setting will delete current setup!\nDo you want to proceed?', buttons = 2, b_text=['Yes','No'])
        else:
            response = 'yes'
        if response == 'yes':
            self.setup()
            #if there are any assignments, clear assignment
            self.MembersList.clearAssignments()
            self.activateButton(self.default_button)
            self.paint_canvas.drawDefault()
            self.activateButton(self.default_button)
            #reset file name
            self.file_name = ''
            
    def isometricView(self):
        #rotate the Canvas contents by 45° to give isometric view like in the game
        self.rotateCanvas(-45)

    def printCity(self):
        self.paint_canvas.block = City()
        self.activateButton(self.city_button)

    def printFlag(self):
        self.paint_canvas.block = Flag()
        self.activateButton(self.flag_button)

    def printRock(self):
        self.paint_canvas.block = Rock()
        self.activateButton(self.rock_button)     

    def printHQ(self):
        if self.paint_canvas.find_withtag('HQ'):
            self.warnWindow('Only one HQ allowed!\nHQ already exists')
        else:
            self.paint_canvas.block = HQ()
            self.activateButton(self.hq_button)
    
    def printTrap(self):
        if len(self.paint_canvas.find_withtag('Trap')) >= 2:
            self.warnWindow('Only two Traps allowed!\nTraps already exist!')
        else:
            self.paint_canvas.block = Trap()
            self.activateButton(self.trap_button)
 
    def printCoords(self):
        # change from True to False or vice versa
        self.paint_canvas.print_coords = not self.paint_canvas.print_coords
        if self.paint_canvas.print_coords:
            self.coord_button.state(['pressed'])
        else:
            self.coord_button.state(['!pressed'])
            self.paint_canvas.removeCoords()

    def raiseFloor(self):
        self.paint_canvas.top_floor = not self.paint_canvas.top_floor
        if self.paint_canvas.top_floor:
            self.paint_canvas.tag_raise('floor','all')
            self.floor_button.state(['pressed'])
        else:
            self.paint_canvas.tag_lower('floor','all')
            self.floor_button.state(['!pressed'])

    def gridOnOff(self):
        # change from True to False or vice versa
        self.paint_canvas.grid_on = not self.paint_canvas.grid_on
        if self.paint_canvas.grid_on:
            self.grid_button.state(['pressed'])
            self.paint_canvas.makeGrid(self.paint_canvas.grid_size)
        else:
            self.grid_button.state(['!pressed'])
            self.paint_canvas.removeGrid()

    def changeGridSize(self,event):
        #refer to canvas method
        self.paint_canvas.changeGridSize(new_grid_size=self.paint_canvas.grid_size)       
     
    def eraseBuilding(self):
        #toggle erase mode
        self.activateButton(self.erase_button) 
        if not self.paint_canvas.erase.get():
            self.paint_canvas.erase.set(True)
            self.erase_button.state(['pressed'])
            self.paint_canvas.config(cursor='tcross')
            #can't have assign and erase at the same time
            self.assign_button.state(['!pressed'])
        else:
            self.resetErase()
    
    def resetErase(self):
        self.paint_canvas.erase.set(False)
        self.erase_button.state(['!pressed'])
        self.paint_canvas.config(cursor='left_ptr')
    
    def assignMode(self,event=False):
        # check of the window with the member names exists
        try:
            self.MembersList.winfo_exists()
        #if not ask for load
        except AttributeError:
            response = self.warnWindow('No Member List available!\nLoad Member List?', buttons = 2, b_text=['Yes','No'])
            if response == 'yes':
                self.loadMembersList()
            return

        self.activateButton(self.assign_button)
        self.paint_canvas.block = None
        # check if assign button is active
        #if self.assign_button.cget('relief') == 'sunken':
        if 'pressed' in self.assign_button.state():
            self.paint_canvas.assign_mode.set(True)
            #self.assign_button.config(bg = used_colors['current'])
            self.paint_canvas.config(cursor='man')
            #can't have assign and erase at the same time
            self.erase_button.state(['!pressed'])
        else:
            self.resetAssign()

    def resetAssign(self):
            self.paint_canvas.assign_mode.set(False)
            self.assign_button.state(['!pressed'])
            self.paint_canvas.config(cursor='left_ptr')

    def resetButtons(self):
        self.resetAssign()
        self.resetErase()
        #find Building Buttons and put them on !pressed status
        buttons = [b for b in self.bt_frame.children.values() if 'Build.TButton' in b.cget('style') and b.instate(['pressed'])]
        for button in buttons:
            button.state(['!pressed'])

    def activateButton(self, clicked_button):
        #self.set_status()
        #release active button if it is clicked
        if self.active_button is not None:
            #try:
            #    self.active_button.config(relief='raised')
            #except tk.TclError:
            self.active_button.state(['!pressed','!focus'])
            #if it is the active button, deactivate button and return
            if self.active_button == clicked_button:
                self.active_button = None
                self.paint_canvas.block = None
                return
       
        #reset all select buttons to inactive
        self.resetButtons()
        #and the clicked button to active
        clicked_button.state(['pressed'])

        #activate button
        self.active_button = clicked_button
        self.paint_canvas.new_block = None
        self.paint_canvas.active_block = self.paint_canvas.block 

    def buildingInfoEncoder(self, tag, unique=True):
        #get coordinates of all canvas objects with tag == 'tag'
        #if unique is set, duplicates are removed
        #get objects from canvas
        obj_list = self.paint_canvas.find_withtag(tag)
        #are there multiple instances (i.e. 'City')
        if isinstance(obj_list, list) or isinstance(obj_list, tuple):
            obj_info = list()
            for obj in obj_list:
                # substract origin to get relative coordinates
                obj_center = listsub(center(self.paint_canvas.coords(obj)),self.paint_canvas.origin)
                #if unique is set, don't add multiples
                if unique:
                    if obj_center in obj_info:
                        continue
                obj_info.append(obj_center)
                if tag == 'City':
                    try:
                        #is the object an assigned city? 
                        obj_info.append('€€'+self.assigments[obj]+'€€')
                    except (TypeError, KeyError):
                        #if not an assigned city, just continue
                        pass
        #else: could be one or zero
        else:
            try:
                #TODO: what if there is only one city and that is assigned to a name?
                # substract origin to get relative coordinates
                obj_info = listsub(center(self.paint_canvas.coords(obj)),self.paint_canvas.origin)
            except TypeError:
                print(f'No {tag} found!')
                obj_info = []

        obj_info_str = tag+': '+str(obj_info)+'\n'
        return obj_info_str.encode('utf8', errors='xmlcharrefreplace')

    def saveLayout(self,event=False,new_file=False):
        #save buildings and assignments to file
        #file already exists:
        if self.file_name == '':
            new_file = True
        #if new file, ask for file name
        if new_file:
            self.file_name = asksaveasfilename(title='Save Hive as:', defaultextension='.hb', initialdir=save_dir,filetypes=[('Hive Organizer file','*.hb')])

        self.assigments = { id : city for city, id in self.paint_canvas.cities.items()}
        building_info = list()
        #remove zoom status for saving
        zoom_status = self.paint_canvas.zoom_on
        if zoom_status:
            self.paint_canvas.zoom()
        #get list of lists for all building coordinates
        for building in self.buildings:
            building_info.append(self.buildingInfoEncoder(building))
        try:
            self.MembersList.winfo_exists()
            member_list = self.MembersList.getLines()
            #strip whitespaces
            member_list = [member.strip() for member in member_list]
        except AttributeError:
            #if no list exists, ignore it
            member_list = None
        
        #Write one line for each building
        with open(self.file_name,'wb') as file:
            #Start with Trap Coordinates if any
            if self.trap_c is not None:
                #ensure integer
                save_tc = listsub(self.trap_c,[Trap().size/2,Trap().size/2])
                save_tc =[int(c) for c in save_tc]
                line = 'TrapCoords: '+str(save_tc)+'\n'
                file.write(line.encode('utf8', errors='xmlcharrefreplace'))
            #Then Buildings
            for enc_line in building_info:
                file.write(enc_line)

            #if member list exists, save it
            if member_list is not None:
                line = 'MemberList: '+'\n'.join(member_list)
                file.write(line.encode('utf8', errors='xmlcharrefreplace'))
            #save used colors if they differ from default
            #Perhaps save even if default?
            # TODO: Might also save everything as json
            # But needs a legacy load function then
            if used_colors is not used_colors_default:
                col_file = self.file_name.split('.')[-2]+'.col'
                with open(col_file, 'w') as fp:
                    json.dump(used_colors, fp)

        #set zoom_status back to original setting
        if zoom_status:
            self.paint_canvas.zoom()

    def loadLayout(self,event=False):
        #load previously saved layout
        lines=''
        ml_data = str()
        self.file_name = askopenfilename(title='Load Hive file:',initialdir=save_dir,defaultextension='.hb',filetypes=[('Hive Organizer file','*.hb'), ('All files','*.*')])   
        #if a color file exists, load it before the rest
        try:
            col_file = self.file_name.split('.')[-2]+'.col'
            self.loadColors(col_file=col_file)          
        except FileNotFoundError:
            #no associated color file, use current colors
            pass
        if self.file_name:
            with open(self.file_name,'r',encoding='utf8') as file:
                lines=file.readlines()
        # only if data was read
        if lines:
            #clear canvas before loading:
            self.paint_canvas.delete('all')
            self.paint_canvas.buildings= []
            #set the relevant values and add the grid
            self.setup()
            #remove zoom
            if self.paint_canvas.zoom_on:
                self.paint_canvas.zoom()

            #check if member list exists
            for ln,line in enumerate(lines):
                if line.startswith('MemberList:'):
                    #all lines from here to end of file should be member names
                    ml_data = lines[ln:]
                    #remove 'MemberList:' from first line
                    ml_data[0]=ml_data[0].replace('MemberList:','')
                    break
            if ml_data:
                #is there already an MembersList?
                try:
                    if self.MembersList.winfo_exists():
                        self.updateMembersList(ml_data)
                    else:
                        self.MembersList = MembersList(ml_data,geometry=("{}x{}+{}+{}".format(self.ML_width, self.winfo_height(),self.winfo_x()+self.winfo_width(),self.winfo_y())))
                        for member in self.MembersList.members:
                            member.changeState('!current')           
                # there is no list
                except AttributeError:
                    self.MembersList = MembersList(ml_data,geometry=("{}x{}+{}+{}".format(self.ML_width, self.winfo_height(),self.winfo_x()+self.winfo_width(),self.winfo_y())))
                    #remove active player tag
                    self.MembersList.removeCurrent()

            # reset Trap Coordinates, then add the buildings
            self.resetTrapCoord()
            for line in lines:
                self.buildHive(line)
            #update header of Memberslist if it is included in the save file
            if ml_data:
                self.MembersList.updateHeader()
            #put origin marker
            self.paint_canvas.originMarker()   

    def saveColors(self,event=None,col_file=None):
        #if it is called by hot_key, event is present and has to be adressed
        #if no file name is provided, ask for one
        if col_file is None:
            col_file = asksaveasfilename(title='Save Color Theme:',initialdir=save_dir, defaultextension='.col', filetypes=[('Color Theme','*.col'), ('All files','*.*')]) 
        try:
            with open(col_file, 'w') as fp:
                json.dump(used_colors, fp)
        except FileNotFoundError:
            self.warnWindow('Colors could not be saved!\nProvide correct Filename!')
    
    def loadColors(self, event=None, col_file=None):
        #if it is called by hot_key, event is present and has to be adressed
        #if no file name is provided, ask for one
        if col_file is None:
            col_file = askopenfilename(title='Load Color Theme:',initialdir=save_dir, defaultextension='.col', filetypes=[('Color Theme','*.col'), ('All files','*.*')]) 
        with open(col_file, 'r') as fp:
            used_colors_load = json.load(fp)
        for key in used_colors_load.keys():
            used_colors[key] = used_colors_load[key]
        self.getcolor('all')

    def buildHive(self,line):
        #paint the Hive from the saved file
        canvas = self.paint_canvas
        block = None
        #check Trap coordinates:
        if line.startswith('TrapCoords'):
            regex = r'\[(\d+),\s*(\d+)\]'
            f = re.search(regex, line)
            if f is not None:
                self.trap_c =[int(f.group(1)), int(f.group(2))]
                self.trap_coord.set(f'X: {self.trap_c[0]}, Y: {self.trap_c[1]}')
                #add half size, as origin is now on lower left corner of trap, not at the center
                self.trap_c = listadd(self.trap_c,[Trap().size/2,Trap().size/2])
        #check building type
        for building in self.buildings:
            if line.startswith(building):
                block = building
        #if it is a building line, do stuff:    
        if block is not None:
            #generate building
            #build_now=''
            command=f'{block}()'
            #build_now = eval(command)
            #find all coordinates of the block
            #there might be negative numbers!
            #legacy mode:
            regex_assign_old = r'\[(-?\d+\.\d+),\s*(-?\d+\.\d+)\].{,3}\&#8364;\&#8364;([^\&]+)\&#8364;\&#8364;'
            regex_assign = r'\[(-?\d+\.\d+),\s*(-?\d+\.\d+)\].{,3}€€([^(€€)]+)€€'
            regex = r'\[(-?\d+\.\d+),\s*(-?\d+\.\d+)\]'
            coords_str = re.findall(regex,line)
            #result is list of tuples of strings, e.g. [('1.0', '2.5'), ('5.00', '7.25'), ('77.1', '88.8')]
            #for cities, check if they have assigned members
            if block == 'City':
                assignments = re.findall(regex_assign,line)
                #legacy mode
                if len(assignments) < 1:
                    assignments = re.findall(regex_assign_old,line)

            #result is list of tuples of strings, e.g. [('1.0', '2.5','Member1'), ('5.00', '7.25','Member2'), ('77.1', '88.8','Member3')]
            #convert into list of coordinates
            for ct in coords_str:
                coords=(listadd(list(map(float,ct)),self.paint_canvas.origin))
                #then paint them:
                build_new = eval(command)
                build_new.paint(canvas, coords,grid=False,color=used_colors[block.lower()])
                #for cities, add they have assigned members
                if block == 'City':
                    for member in assignments:
                        ML = self.MembersList

                        member_coords = member[0:2]
                        member_name = member[2:][0].strip()
                        
                        #assigned city!
                        if member_coords == ct:
                            city=build_new.id['building']

                            #check if member exists in list
                            member = find(lambda f: f.name.get() == member_name, ML.members)
                            if member:
                                #remove active player tag
                                self.MembersList.removeCurrent()
                                member.changeState("new current")
                            #if member is not found, add them to the list
                            else:
                                self.MembersList.addMember(Member(name=member_name))
                            self.paint_canvas.assignMember(self.MembersList,city=city)
        #remove any remaining "new current" status if MembersList exists
        try:
            self.MembersList.removeCurrent()
        except AttributeError:
            pass

    def loadMembersList(self,event=False):
        load_file = askopenfilename(title='Load Member List:',initialdir=save_dir, defaultextension='.txt', filetypes=[('Member List text file','*.txt'), ('All files','*.*')]) 
        if load_file:
            with open(load_file,'r',encoding='utf8') as file:
                lines=file.readlines()
        #is there already a members list?
        try:
            if self.MembersList.winfo_exists():
                self.updateMembersList(lines)
                return
        #either there never was a members list or the window was closed:
        except AttributeError:
            pass
        self.MembersList = MembersList(lines,geometry=("{}x{}+{}+{}".format(self.ML_width, self.winfo_height(),self.winfo_x()+self.winfo_width(),self.winfo_y())))

    def saveMembersList(self,event=False):
        #save MemberslList to Textfile
        try:
            ml_ok = self.MembersList.winfo_exists()
        except AttributeError or UnboundLocalError:
            return
        if ml_ok:  
            # get list of member names
            member_list = self.MembersList.getLines()
            #strip whitespaces
            member_list = [member.strip() for member in member_list]          
            save_file = asksaveasfilename(title='Save Member List:',initialdir=save_dir, defaultextension='.txt', filetypes=[('Member List text file','*.txt'), ('All files','*.*')]) 
            if save_file:
                with open(save_file,'wb') as file:
                    if member_list is not None:
                        line = '\n'.join(member_list)
                        file.write(line.encode('utf8', errors='xmlcharrefreplace'))

    def updateMembersList(self,ml_data):
        #what to do if new List is loaded when list already exists
        response = self.warnWindow('Member List already active!\nOverwrite existing Member List,\n try to merge both lists or ignore list in File?', 
                                    buttons = 3, b_text=['Overwrite','Merge','Ignore'])
        if response == 'overwrite':
            #remove all old assignments
            self.MembersList.clearAssignments()

            #remove existing list
            self.MembersList.destroy()
            #and generate new one
            self.MembersList = MembersList(ml_data,geometry=("{}x{}+{}+{}".format(self.ML_width, self.winfo_height(),self.winfo_x()+self.winfo_width(),self.winfo_y())))
            #remove active player tag
            for member in self.MembersList.members:
                member.changeState('!current')
            
        elif response == 'merge':
            #merge both lists
            self.MembersList.merge(ml_data)
        else:
            #ignore: Do nothing
            pass

    def rotateCanvas(self, angle):
        #rotate the whole canvas by angle degrees
        canvas = self.paint_canvas
        #create new canvas on top of old canvas
        top = tk.Toplevel(self)
        top.details_expanded = False
        top.title('Hive Organizer '+Version+'\t'+chr(169)+' 2024/25 by Shivkala'+"\tIsometric View")
        top.style = self.style
        top.config(bd=3, bg=used_colors['bg'])

        upper_frame = ttk.Frame(top)
        #upper_frame.pack()
        upper_frame.pack(fill='x')
        top.geometry("{}x{}+{}+{}".format(self.winfo_width(), self.winfo_height()+40,self.winfo_x()+20,self.winfo_y()+20))
        
        #Frame for Canvas
        cs_frame= ScrolledFrame(top, width = top.winfo_width(), height = top.winfo_height())
        int_frame = cs_frame.interior
        int_frame.columnconfigure(0, weight=1)
        int_frame.rowconfigure(0, weight=1)
        upper_canvas = int_frame.master
        
        #isometric canvas
        top_canvas = IsoCanvas(int_frame, width=self.paint_canvas.winfo_width(), 
                               height=self.paint_canvas.winfo_height(),bg=used_colors["canvas_bg"])
        
        #cs_frame.grid(row=1,column=0,sticky='news')
        cs_frame.pack(side=tk.LEFT,fill='both', expand=True)
        top_canvas.pack(side=tk.LEFT,fill='both', expand=True)
        
        top.rowconfigure(1, weight=1)
        top.columnconfigure(0, weight=1)
        upper_canvas.configure(width = top.winfo_width(), height = top.winfo_height())
        #calculate scrollregion
        self.update()
        size = (int(top_canvas.cget('width')), int(top_canvas.cget('height')))
        cs_frame.scrollArea(size,2)       
        #TODO: focus on the same area as PaintCanvas

        tmpng = ttk.Button(upper_frame, text="Make PNG", style='TButton', command=lambda: make_png(top_canvas,top))
        tmpng.grid(row=0,column=0, padx=(7, 7), pady=(7, 7), sticky='w')
        tcb = ttk.Button(upper_frame, text="Close", style='TButton', command=top.destroy)
        tcb.grid(row=0,column=1, padx=(7, 7), pady=(7, 7), sticky='e')
        top_canvas.pack()
        top_canvas.showMember = None
        top_canvas.cities = canvas.cities

        all_stuff = canvas.find_all()

        # go through every element and rotate it around the center
        for element in all_stuff:
            #get the tags of the element
            tags = canvas.gettags(element)
            el_coords = canvas.coords(element)
            # give coords relative to center
            for i in range(len(el_coords)):
                x_or_y = i%2
                el_coords[i] -= canvas.origin[x_or_y]
            
            # convert coordinates (there need to be 4:x0,y0,x1,y1)
            if len(el_coords) == 4:
                # grid lines need to stay grid lines
                if 'grid' in tags:
                    poly_coords = [[el_coords[0],el_coords[1]],[el_coords[2],el_coords[3]]]
                else:            
                    #for a polygon we need each point, not box
                    poly_coords = getPoly(el_coords)
            #text of assigned cities
            elif 'member' in tags:
                poly_coords = [[el_coords[0],el_coords[1]]]
            else:
                #if number of coordinates is wrong, just don't paint anything
                poly_coords = []
            # now rotate coordinates
            rot_coords = poly_coords

            for i, c in enumerate(poly_coords):
                # for each x/y set
                #rotate the coordinates and add the center    
                rot_coords[i] = listadd(rot(c, angle), canvas.origin)
                #[x_rot, y_rot]

            # now put the rotated element on the new canvas
            if 'grid' in tags:
                top_canvas.create_line(*rot_coords,dash=canvas.itemcget(element,'dash'))
            elif 'building' in tags: 
                nb=top_canvas.create_polygon(rot_coords, fill=canvas.itemcget(element,'fill'),
                                        stipple=canvas.itemcget(element,'stipple'),
                                        outline='black')
                #for get the tags so that it can be used for hover text
                if 'City' in tags:
                    member_name = canvas.findAssignee(element)
                    #check for an assigned member
                    if member_name is not None:
                        top_canvas.addtag_withtag(member_name,nb)
                        top_canvas.tag_bind(member_name,'<Enter>',func=lambda event: showAssignment(event=event,canvas = top_canvas))
                        top_canvas.tag_bind(member_name,'<Leave>',func=lambda event: showAssignment(event=event,canvas = top_canvas))

                #get the tags so that it can be used for hover text
            #floor gets no border
            elif 'floor' in tags:
                top_canvas.create_polygon(rot_coords, fill=canvas.itemcget(element,'fill'),stipple=canvas.itemcget(element,'stipple'),outline='')
            elif 'member' in tags:
               text_config = self.paint_canvas.itemconfig(element)
               text_config = { key:value[-1] for key, value in text_config.items()}
               #move it a bit for better readability
               rot_coords = listadd(rot_coords[0],[5, -7])
               top_canvas.create_text(rot_coords, text_config) 
        #at the end center the view at the same point as in the PaintCanvas
        upper_canvas.xview_moveto(self.upper_canvas.xview()[0])
        upper_canvas.yview_moveto(self.upper_canvas.yview()[0])

def make_png(widget, toplevel):
    save_file = asksaveasfilename(title='Save Hive as PNG:', defaultextension='.png', initialdir=save_dir)
    #put the window on top so that the screen grab is not obstructed by other windows
    toplevel.attributes('-topmost',True)
    x=toplevel.winfo_rootx()+widget.winfo_x()
    y=toplevel.winfo_rooty()+widget.winfo_y()
    x1=x+widget.winfo_width()
    y1=y+widget.winfo_height()
    ImageGrab.grab((x,y,x1,y1)).save(save_file)
    #release the window
    toplevel.attributes('-topmost',False)

MW = MainWindow()
MW.mainloop()
MW.destroy()