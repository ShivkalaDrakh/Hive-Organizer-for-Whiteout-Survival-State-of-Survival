"""
Hive Organizer for Whiteout Survival and State of Survival
Copyright (C) 2024 Mark Hartrampf

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
import math
import os
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter import ttk
from PIL import Image, ImageTk
from hive.utils import callweb, listadd, listsub, center, VerticalScrolledFrame, find
from hive.styles import initStyle, used_colors

Version = "V0.2.1"

# script dir will be used as initial for load/save
script_dir=os.path.dirname(os.path.realpath(__file__))
init_dir =os.path.join(script_dir,'hive')
save_dir = os.path.join(init_dir,'save')

class Member():
    def __init__(self, number=0, name='', coords=' --- ',power=0,status='', 
                 city_id=None, widget = None, coord_widget = None, canvas = None):
        self.number=number
        self.name = name
        self.coords = coords
        self.power = power
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


class Block():
    multiplier = 5
    def __init__(self,size=0, area=0,coords=[0,0], color='red',tag = '', id=dict(), floor_color=used_colors["floor"], text_color =used_colors["floor"]):
        #create a block(building, floor, etc)
        # with:
        # size in grid coordinates
        # area size of its floor (for FLag and HQ)
        # color of the block on the canvas
        # multiplier: Pixel per grid point
        self.size = size
        self.area = area
        self.coords = coords
        self.color = color
        self.tag=tag
        self.id = dict()
        self.id.update(id)
        self.floor_color = floor_color
        self.text_color = text_color
    
    def paint(self,canvas,coords,grid=True):
        self.canvas = canvas
        if grid:
            self.coords = self.convGrid2Coord(coords)
        else:
            self.coords=coords

        building = canvas.create_rectangle(self.coords[0]-self.size*self.multiplier,self.coords[1]-self.size*self.multiplier,
                                self.coords[0]+self.size*self.multiplier, self.coords[1]+self.size*self.multiplier, 
                                fill=self.color,tags=('building',self.tag))
        self.id.update({'building' : building})
        canvas.buildings.append(self)
        #if building provides Area, add it here
        if self.area > 0:
            floor=canvas.create_rectangle(self.coords[0]-self.area*self.multiplier,self.coords[1]-self.area*self.multiplier,
                        self.coords[0]+self.area*self.multiplier, self.coords[1]+self.area*self.multiplier, 
                        stipple="gray12", fill=self.floor_color,outline ='',tags=('floor',self.tag))
            canvas.tag_lower(floor)
            self.id.update({'floor' : floor})
            return [building, floor]        
        return building
    
    def convGrid2Coord(self,grid_coords):
        #convert Grid coordinates into pixel coordinates on canvas
        #Attention: for CANVAS coordinates POSITIVE Y is DOWN
        #but for GRID coordinates POSITIVE Y is UP!
        coords = [self.canvas.origin[0]+grid_coords[0]*self.multiplier*2, self.canvas.origin[1] - grid_coords[1]*self.multiplier*2]
        return coords
    
    def box(self,center,grid = False,floor=False):
        #gives upper left and lower right coordinates from center in 
        # canvas coordinates (grid = False, default) or
        # grid coordinates (grid = True)
        # uses size for buildings and area for floor
        if floor:
            size=self.area
        else:
            size=self.size
        if grid:
            bbox =[center[0]-size/2, center[1]+size/2, 
                   center[0]+size/2, center[1]-size/2]
        else:
            bbox =[center[0]-size*self.multiplier, center[1]-size*self.multiplier, 
                   center[0]+size*self.multiplier, center[1]+size*self.multiplier]
        return bbox

class Flag(Block):
     def __init__(self,size=1, area=7,coords=[0,0],color=used_colors["flag"],tag = 'Flag',floor_id=0):
          super().__init__(size, area,coords,color,tag)
          self.floor_id = floor_id  

class City(Block):
     def __init__(self,size=2, area=0,coords=[0,0],color=used_colors["city"], tag='City'):
          super().__init__(size, area,coords,color,tag) 
          #self.assign = assign     

class HQ(Block):
     def __init__(self,size=3, area=15,coords=[0,0],color=used_colors["hq"], tag='HQ',floor_id=0):
          super().__init__(size, area,coords,color,tag)
          self.floor_id = floor_id   
        
class Trap(Block):
     def __init__(self,size=3, area=0,coords=[0,0],color=used_colors["trap"], tag='Trap'):
          super().__init__(size, area,coords,color,tag)       

class Rock(Block):
     def __init__(self,size=2, area=0,coords=[0,0],color=used_colors["rock"], tag='Rock'):
          super().__init__(size, area,coords,color,tag)  

class MembersList(tk.Toplevel):
    # Defines the window with the list of member names
    def __init__(self,lines,geometry='100x100+100+100'):
        super().__init__()
        self.style = self.master.style
        self.lines = lines
        self.members=[]
        #build member list and show in seperate Window
        self.title("Alliance Members List")
        self.geometry(geometry)
        #add border
        self.config(bd=3, bg=used_colors['bg'])

        upper_frame = ttk.Frame(self)
        #upper_frame.pack()
        upper_frame.pack(fill='x')
        update_c_button=ttk.Button(upper_frame, text="Update", style='TButton', 
                                   command=self.updateCoordinates)
        update_c_button.grid(row=0,column=0, padx=(7, 7), pady=(7, 7), sticky='w')
        close_button=ttk.Button(upper_frame, text="Close", style='TButton', command=self.remove)
        #close_button.pack()
        close_button.grid(row=0,column=1, padx=(7, 7), pady=(7, 7), sticky='e')

        upper_frame.columnconfigure(0, weight=0)
        upper_frame.columnconfigure(1, weight=1)

        # frame with actual list
        # the data is in the frame inside the scroll frame
        self.scroll_frame = VerticalScrolledFrame(self)
        self.scroll_frame.pack(fill='both', expand=True)
        self.new_frame = self.scroll_frame.interior
        self.new_frame.columnconfigure(1, weight=1)

        #add members, to be filled in addMember
        for line in lines:
            self.members.append(Member(name=line.strip()))
        self.setup()

    def setup(self):
        self.ml = []
        self.names = []
        #for i, member in enumerate(self.members):
        for member in self.members:
            self.addMember(member)
 
    def selectName(self,event, var):
        #select the klicked name
        member_name = var.get()
        #remove old current line
        old_cl = find(lambda my: "current line;" in my.status, self.members)
        if old_cl:
            old_cl.changeState("!current")
            old_cl.setColor()

        member = find(lambda my: my.name == member_name, self.members)
        #add new current line
        if not member:
            member=Member(name=member_name)
        member.changeState("new current")

    def remove(self):
        #check if there are any assignments
        #if yes, warn window
        #if not, destroy
        if find(lambda my: "assigned;" in my.status, self.members):
            response = self.master.warn_window('Closing Members List will remove current assignments!\nDo you want to proceed?', buttons = 2, b_text=['Yes','No'])
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

    def updateCoordinates(self):
        canvas = self.master.paint_canvas
        for member in self.members:
            if "assigned;" in member.status:
                canvas.showMemberCoords(member)

    def removeCityAssignment(self, city, member_name):
        #remove the city from the assignment list and delete the number
        canvas = self.master.paint_canvas
        #find city on canvas
        text_field = set(canvas.find_overlapping(*canvas.coords(city))).intersection(set(canvas.find_withtag('member')))
        #remove number
        canvas.delete(*text_field)
        #remove tag
        canvas.dtag(city, member_name)

        member = find(lambda my: my.name == member_name,self.members)
        if member:
            member.changeState("!assigned")
            member.city_id = None
            member.coords = [0, 0]
            member.coord_widget.config(text=' --- ')

        #remove from list of assigned cities
        #TODO: this doesn_t work with iterations
        #canvas.cities.pop(member_name)

    def merge(self,new_members):
        #merge new list of names with existing one

        for new_member in new_members:
            #remove whitespaces and CR at start and end of name
            new_member=new_member.strip()
            #Is member in list already?
            member = find(lambda my: my.name == new_member, self.members)
            if not member:
                self.members.append(Member(name=new_member))
                self.addMember(self.members[-1])

    def addMember(self, member):
        #add new member to MembersList
        self.names.append(tk.StringVar(master =self.new_frame, value=member.name))
        new_idx = len(self.names)
        member.number= new_idx
        ml_number = ttk.Label(self.new_frame,style='TLabel',text=str(new_idx))
        ml_number.grid(row=new_idx,column=0, sticky='news')
        ml_entry = ttk.Entry(self.new_frame,style='TEntry',textvar=self.names[new_idx-1], width=20)
        ml_entry.grid(row=new_idx,column=1, sticky='news')
        member.widget = ml_entry
        ml_coords = ttk.Label(self.new_frame,style='TLabel',text=member.coords)
        ml_coords.grid(row=new_idx,column=2, padx= 7, sticky='news')
        member.coord_widget = ml_coords
        
        ml_entry.bind('<ButtonRelease-1>', func=lambda event,var = self.names[new_idx-1]: self.selectName(event,var))
        self.ml.append((ml_number,ml_entry, ml_coords ))

        #change state of old 'current' member
        cur_member = find(lambda my: "current line;" in my.status, self.members)
        if cur_member:
            cur_member.changeState('!current')
        #and make the new member the current one
        member.changeState("new current")

class IsoCanvas(tk.Canvas):
    def __init__(self, master, width=0, height=0, bg='white', print_coords = True):
        super().__init__(master=master,width=width, height=height, bg=bg)

    def findAssignee(self,id):
        #find the name of the member assigned to the id of the canvas object
        ret_val = list(set(self.gettags(id)).intersection(set(self.cities.keys())))
        #if only one member (which should always be the case) return string, not list
        if len(ret_val) == 0:
            return None
        elif len(ret_val) == 1:
            ret_val = ret_val[0] 
        return ret_val
    
#TODO: make PaintCanvas sub-class of IsoCAnvas and transfer the relevent methods
class PaintCanvas(IsoCanvas):
    def __init__(self, master, width=0, height=0, bg='white', print_coords = True):
        super().__init__(master=master,width=width, height=height, bg=bg)
        self.master = master
        self.width = width
        self.height = height
        self.origin = [0,0]

        self.erase = False
        self.print_coords = print_coords
        self.block = None
        self.grid_on = False
        self.assign_mode = False
        self.zoom_on = False
        self.buildings=list()
        self.cities = dict()
        self.showMember = None

        #define mouse actions
        #Button 1
        self.bind('<Button-1>', selectBlock)
        self.bind('<B1-Motion>', moveBlock)
        self.bind('<ButtonRelease-1>', putBlock)
        
        #generel movement
        self.bind('<Motion>', self.showCoords)

        # for area select use button-3
        self.bind('<Button-3>', self.startSelect)
        self.bind('<B3-Motion>', self.showArea)
        self.bind('<ButtonRelease-3>', self.areaSelect)

        #self.makeGrid()

    def setup(self):
        # resize canvas if window resizes
        self.master.bind("<Configure>", self.on_resize)
        # set origin of grid and activate grid
        self.block = None
        self.buildings=list()
        self.cities = dict()
        self.showMember = None
        self.origin = [self.winfo_width()/2, self.winfo_height()/2]
        self.makeGrid()

    def zoom(self, zoom_factor = 2.0):
        self.zoom_on = not self.zoom_on
        origin = self.origin
        if not self.zoom_on:
            self.master.zoom_button.state(['!pressed'])
            zoom_factor = 1/zoom_factor
        else:
            self.master.zoom_button.state(['pressed'])
        #remove coordnates
        self.delete(self.find_withtag('c_coords'))
        self.delete(self.find_withtag('g_coords'))
        #up- or downscale everything
        self.scale('all',*origin,zoom_factor,zoom_factor)
        Block.multiplier *= zoom_factor
        #re-draw the grid
        self.makeGrid()

    def on_resize(self,event):
        # when the canvas resizes, Grid and Coordinates need to be updated
        # end all blocks have to move
        old_origin = self.origin
        origin = [self.winfo_width()/2,self.winfo_height()/2]
        
        dx = origin[0] - old_origin[0]
        dy = origin[1] - old_origin[1]

        #if sized changed: 
        if dx != 0 or dy != 0:
            # draw new grid
            self.makeGrid()
            #remove coordnates
            self.delete(self.find_withtag('c_coords'))
            self.delete(self.find_withtag('g_coords'))
            #move blocks: buildings, assigned numbers, floors, origin
            blocks_to_move = set(self.find_withtag('building'))
            blocks_to_move.update(self.find_withtag('member'),
                                  self.find_withtag('floor'),
                                  self.find_withtag('origin'))
            for block in blocks_to_move:
                self.move(block,dx,dy)

    def convCoord2Grid(self,coords,block=None,trap_coords=None):
        # size of block, if block is
        #convert normal coordinates into grid positions and lock into grid
        #Attention: for CANVAS coordinates POSITIVE Y is DOWN
        #but for GRID coordinates POSITIVE Y is UP!   

        #if a Block() is provided, use its size and multiplier
        if isinstance(block,Block):
            size=block.size 
            multiplier=block.multiplier
        #otherwise use default
        else:
            size=0
            multiplier=Block.multiplier
    
        grid_coords = [0,0]

        #objects of even size need to shift by 0.5 grid points as origin is at a half-point
        grid_shift = (size+1)%2*0.5
        #move to closest grid line, not only to the right...
        #Y coord is negative, see above
        dummy_c = [(coords[0]-self.origin[0])/(multiplier*2), (-coords[1]+self.origin[1])/(multiplier*2)]
        round_c = [round((coords[0]-self.origin[0])/(multiplier*2)), round((-coords[1]+self.origin[1])/(multiplier*2))]
        for i in range(2):
            if dummy_c[i] > round_c[i]:
                grid_coords[i] = round_c[i] + grid_shift
            else:
                grid_coords[i] = round_c[i] - grid_shift

        #Add Trap Coordinates
        if trap_coords is not None:
            #Debug
            grid_coords = listadd(grid_coords,trap_coords)
        return grid_coords

    def showCoords(self, event):
        #show canvas coordinates in lower right corner
        # and grid coordinates in lower left corner
        trap_coord = None
        self.master.trap_entry.state(['disabled'])
        if self.print_coords:
            # if Trap exists, activate Coordinate field
            if self.find_withtag('Trap'):
                self.master.trap_entry.state(['!disabled'])
                trap_coord = self.master.trap_c
            text='{}, {}'.format(str(event.x), str(event.y))
            # convert canvas coordinates to grid coordinates
            delta=Block.multiplier
            grid = [event.x-delta, event.y+delta]
            grid = self.convCoord2Grid(grid,trap_coords=trap_coord) 
 
            text_grid = 'Grid: {}, {}'.format(str(grid[0]), str(grid[1]))
            c_coords = self.find_withtag('c_coords')
            g_coords = self.find_withtag('g_coords')
            if c_coords:
                self.itemconfigure(c_coords, text=text)
            else:
                self.text_coord = self.create_text(self.winfo_width()-10, self.winfo_height()-10, 
                                                                anchor=tk.SE, text=text, tag=('c_coords','coords'))
                self.itemconfig(self.text_coord,font=('Helvetica', 15))
            
            if g_coords:
                self.itemconfigure(g_coords, text=text_grid)
            else:
                self.text_grid_coord = self.create_text(10, self.winfo_height()-10, anchor=tk.SW, text=text_grid,tag=('g_coords','coords'))
                self.itemconfig(self.text_grid_coord,font=('Helvetica', 15))
    
    def removeCoords(self):
            #if coords are shown, delete them
            try:
                self.delete(self.text_coord)
                self.delete(self.text_grid_coord)
            except AttributeError:
                pass
    
    def removeBuilding(self, building):
        #remove building from the canvas and the building list     
        block = self.getBuildingFromId(building) 
        #is there a building with this ID?  
        if block is not None:
            self.buildings.remove(block)
            self.delete(*block.id.values())
            return
        #if it's not in the building list, just delete it from the canvas
        self.delete(building)
    
    def moveBuilding(self, building, center, grid=False, rel=False):
        #move the selected building with all it:s appendices
        if isinstance(building,Block):
            #convert to canvas coords if grid=True
            if grid:
                center=building.convGrid2Coord(center)
            #if it's relative coordinates, use Canvas.move, otherwise use Canvas.coords
            
            for id in building.id.values():
                if rel:
                    self.move(id, *center)
                else: 
                    floor = 'floor' in self.gettags(id)
                    box = building.box(center,floor=floor)
                    # the assigment indicator (canvas text) has only 2 coordinates, not 4
                    if 'member' in self.gettags(id):
                        box =[box[0]+2,box[1]+2]
                    self.coords(id,*box)
            #put assignment indicators on top
            self.tag_raise('member','all')
        else:
            if rel:
                self.move(building, *center)
            else:
                self.coords(building,*Block().box(center))
                    
    def startSelect(self, event):
        #define upper left corner of area
        self.area = [event.x, event.y , 0, 0]
        #create rectangle w size 1
        self.area_box = self.create_rectangle(event.x, event.y ,event.x+1, event.y+1 )

    def showArea(self, event):
        #define lower right corner, 
        self.area[2:4] = [event.x, event.y]
        #then change size of the rectangle
        self.coords(self.area_box,*self.area)

    def areaSelect(self, event):
        #find all blocks inside the area
        all_stuff = set(self.find_enclosed(*self.area))
        selected = set(self.find_withtag('building'))
        selected.union(set(self.find_withtag('floor')))
        selected_stuff = all_stuff.intersection(selected)
        for select in selected_stuff:
            self.itemconfig(select,stipple='gray12')
            self.addtag('selected','withtag', select)
        #then release the selection frame
        self.delete(self.area_box)    

    def drawDefault(self):
        #draw HQ, Trap and Grid
        #clear canvas before drawing
        self.delete('all')
        self.master.resetTrapCoord()
        self.buildings = []
        #but add the grid
        self.makeGrid()
        #remove assignments from member list (if any)
        try:
            #remove active player tag
            for member in self.MembersList.members:
                member.changeState("!assigned")
            #self.master.MembersList.members_list.tag_remove('assigned','1.0','end')
        except AttributeError:
            pass
        #put HQ and Trap
        HeadQuarter = HQ(coords=[-11, 5]) 
        NewTrap = Trap(coords = [0,0])

        #Set Trap at origin
        NewTrap.paint(self,NewTrap.coords)
        #put origin marker
        self.originMarker()        
        #then HQ
        HeadQuarter.paint(self,HeadQuarter.coords)
        #floor is under buildings
        self.tag_lower('floor','building')    

    def originMarker(self):
        #draw the origin
        om = self.create_rectangle(self.winfo_width()/2-1,self.winfo_height()/2-1,self.winfo_width()/2+1,self.winfo_height()/2+1)
        self.addtag_withtag('origin',om)

    def makeGrid(self,grid_space = 6):
        #draw grid on canvas
        #first remove existing grid if any
        self.removeGrid()
        # grid_space: distance betwen grid lines in grid coordinates
        self.origin = [self.winfo_width()/2,self.winfo_height()/2]
        self.grid_on = True
        multiplier = Block().multiplier*2
        pix_space = grid_space*multiplier
        # the origin is considered a 'half' grid point, so ensure that the lines reflect that
        width = self.winfo_width()
        height = self.winfo_height()
        # initialize grid line:
        grid_pos = grid_space/2
        # if grid_space is an even number, add a half grid point to match full gridpoint roster1
        grid_pos += (grid_space+1)%2*0.5
        pix_pos = grid_pos*multiplier
        while pix_pos < max(width, height):
            #horizontal (plus and minus of origin)
            self.create_line(0,self.origin[1]+pix_pos,width,self.origin[1]+pix_pos,dash=(1,5),tag='grid')
            self.create_line(0,self.origin[1]-pix_pos,width,self.origin[1]-pix_pos,dash=(1,5),tag='grid')
            #vertical
            self.create_line(self.origin[0]+pix_pos,0,self.origin[0]+pix_pos,height,dash=(1,5),tag='grid')
            self.create_line(self.origin[0]-pix_pos,0,self.origin[0]-pix_pos,height,dash=(1,5),tag='grid')
            pix_pos += pix_space
        
        #create coordinate axes:
        self.create_line(0,self.origin[1],width,self.origin[1],dash=(7,1,1,1),tag='grid')
        self.create_line(self.origin[0],0,self.origin[0],height,dash=(1,1,1,1),tag='grid')
        
        #at the end put grid under buildings but above floor (only relevant for on/off)
        if self.find_withtag('building'):
            self.tag_lower('grid','building')

    def removeGrid(self):
        # delete grid
        grid = self.find_withtag('grid')
        self.delete(*grid)
        self.grid_on = False

    def getBuildingFromId(self,building_id):
        #get the building in the self.buildings list from the id

        for building in self.buildings:
            #if building id in id values
            if building.id['building'] == building_id:
                return building
        return None
    
    def assignMember(self,ML,city):
        #assign selected member to building
        member = find(lambda my: "current line;" in my.status, ML.members)
        #if there is a current line
        if not member:
            return
        member_num = member.number
        member_name = member.name
        
        self.addtag_withtag('assigned',city)
        #remove old assignement as one member can have only one city
        if member_name in self.cities.keys():
            old_city = self.cities[member_name]
            ML.removeCityAssignment(old_city,member_name)
            self.cities.pop(member_name)
        #and remove previous owner of city (if any)
        if city in self.cities.values():
            old_owner = [k for k,v in self.cities.items() if v == city][0]
            #remove old assignment
            ML.removeCityAssignment(city,old_owner)
            self.cities.pop(old_owner)

        self.cities.update({member_name : city})
        #also tag the city in question
        self.addtag_withtag(member_name, city)
        # and the other way around
        self.assigments = { id : city for city, id in self.cities.items()}
        member.city_id = city
        member.canvas = self

        # provide coorinates if trap coordinates are activated
        if self.master.trap_c is not None:
            self.showMemberCoords(member)

        #bind to the city (not the text!)
        self.tag_bind(member_name,'<Enter>',func=lambda event: showAssignment(event=event,canvas = self))
        self.tag_bind(member_name,'<Leave>',func=lambda event: showAssignment(event=event,canvas = self))

        #then show the number on the city
        x0, y0, *_ = self.coords(city)
        text_id=self.create_text(x0+2, y0+2, anchor=tk.NW, text=str(member_num), fill='black',activefill='white',tag=('member'))
        # get the building object
        block = self.getBuildingFromId(city)
        if block is not None:
            block.id.update({'text':text_id})
        #set textcolor according to block setting
        self.itemconfig(text_id,fill=used_colors["assign"])
        self.tag_lower('building','member')
        #also mark it in member list and remove the current selection;:
        member.changeState("new assigned,!current")

    def showMemberCoords(self, member):
        #Calculate the city coordinate in the trap grid and display it
        #check if trap coordinates are active
        if self.master.trap_c is not None:
            cc = self.coords(member.city_id)
            cc = [cc[0],cc[-1]]
            cc_grid = [int(dummy) for dummy in self.convCoord2Grid(cc, trap_coords=self.master.trap_c)]
            #change to new class
            member.coords = cc_grid
            member.coord_widget.config(text=str(member.coords))
        else:
            member.coord_widget.config(text=' --- ')

    def findAssignee(self,id):
        #find the name of the member assigned to the id of the canvas object
        ret_val = list(set(self.gettags(id)).intersection(set(self.cities.keys())))
        #if only one member (which should always be the case) return string, not list
        if len(ret_val) == 0:
            return None
        elif len(ret_val) == 1:
            ret_val = ret_val[0] 
        return ret_val

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Hive Organizer '+Version+'\t'+chr(169)+' 2024 by Shivkala')

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

        #add border
        self.config(bd=3, bg=used_colors['bg'])

        #Frame
        bt_frame=ttk.Frame(self, width = wwidth, height = 65)
        bt_frame.grid(row=0,column=0,sticky='news')
        bt_frame.columnconfigure(0,weight=1)
        
        #setup Canvas
        self.paint_canvas = PaintCanvas(self, width=wwidth, height = wheight, bg='white')

        #paint canvas
        self.paint_canvas.grid(row=1,column=0,sticky='news')
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        #first column:
        fc = 1
        self.bt_frame = bt_frame
        #load/save/etc
        self.save_button = ttk.Button(bt_frame, text='Save', command=self.saveLayout)
        self.save_button.grid(row = 0, column=fc+0, sticky='news',padx=fpadx, pady=fpady)

        self.load_button = ttk.Button(bt_frame, text='Load', command=self.loadLayout)
        self.load_button.grid(row = 0, column=fc+1, sticky='news',padx=fpadx, pady=fpady)

        #add a bit of space in between
        self.dummy= ttk.Label(bt_frame)
        self.dummy.grid(row = 0, column=fc+7, sticky='news',padx=30, pady=fpady)
        #self.columnconfigure(fc+7, weight=1)

        self.isoview_button = ttk.Button(bt_frame, text='Isometric', style='TButton', command=self.isometricView)
        self.isoview_button.grid(row = 0, column=fc+8, sticky='news',padx=fpadx, pady=fpady)
        
        self.default_button = ttk.Button(bt_frame, text='Default', style='TButton', command=self.default)
        self.default_button.grid(row = 0, column=fc+9, sticky='nes',padx=fpadx, pady=fpady)

        self.members_button = ttk.Button(bt_frame, text='Member List', command=self.loadMembersList)
        self.members_button.grid(row = 0, column=fc+10, sticky='news',padx=fpadx, pady=fpady)

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
        self.coord_button = ttk.Button(bt_frame, text='Coords',style='CG.TButton', command=self.printCoords)
        self.coord_button.state(['pressed'])
        self.coord_button.grid(row=1, column=fc+8, sticky='e',padx=fpadx, pady=fpady)

        self.grid_button = ttk.Button(bt_frame, text='Grid', style='CG.TButton', command=self.gridOnOff)
        self.grid_button.state(['pressed'])
        self.grid_button.grid(row=1, column=fc+9, sticky='ew',padx=fpadx, pady=fpady)

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

        #draw default after starting mainloop
        self.after(100,self.setup)

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
                
    def setup(self):
        #performed once mainloop is started
        self.paint_canvas.setup()
        self.active_button = None
        self.buildings = set(['HQ','City','Flag','Trap','Rock'])

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

    def warn_window(self, warning,  buttons=1, b_text=['OK'], width=300, height=100):
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
            response = self.warn_window('Default setting will delete current setup!\nDo you want to proceed?', buttons = 2, b_text=['Yes','No'])
        else:
            response = 'yes'
        if response == 'yes':
            self.setup()
            self.activateButton(self.default_button)
            self.paint_canvas.drawDefault()
            self.activateButton(self.default_button)

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
            self.warn_window('Only one HQ allowed!\nHQ already exisits')
        else:
            self.paint_canvas.block = HQ()
            self.activateButton(self.hq_button)
    
    def printTrap(self):
        if self.paint_canvas.find_withtag('Trap'):
            self.warn_window('Only one Trap allowe!\nTrap already exisits')
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

    def gridOnOff(self):
        # change from True to False or vice versa
        self.paint_canvas.grid_on = not self.paint_canvas.grid_on
        if self.paint_canvas.grid_on:
            self.grid_button.state(['pressed'])
            self.paint_canvas.makeGrid()
        else:
            self.grid_button.state(['!pressed'])
            self.paint_canvas.removeGrid()

     
    def eraseBuilding(self):
        #toggle erase mode
        self.activateButton(self.erase_button) 
        if not self.paint_canvas.erase:
            self.paint_canvas.erase = True
            self.erase_button.state(['pressed'])
            self.paint_canvas.config(cursor='tcross')
        else:
            self.resetErase()
    
    def resetErase(self):
        self.paint_canvas.erase = False
        self.erase_button.state(['!pressed'])
        self.paint_canvas.config(cursor='left_ptr')
    
    def assignMode(self):
        # check of the window with the member names exists
        try:
            self.MembersList.winfo_exists()
        #if not ask for load
        except AttributeError:
            response = self.warn_window('No Member List available!\nLoad Member List?', buttons = 2, b_text=['Yes','No'])
            if response == 'yes':
                self.loadMembersList()
            return

        self.activateButton(self.assign_button)
        self.paint_canvas.block = None
        # check if assign button is active
        #if self.assign_button.cget('relief') == 'sunken':
        if 'pressed' in self.assign_button.state():
            self.paint_canvas.assign_mode = True
            #self.assign_button.config(bg = used_colors['current'])
            self.paint_canvas.config(cursor='man')
        else:
            self.resetAssign()

    def resetAssign(self):
            self.paint_canvas.assign_mode = False
            self.assign_button.state(['!pressed'])
            self.paint_canvas.config(cursor='left_ptr')

    def resetButtons(self):
        self.resetAssign()
        self.resetErase()
        #find Building Buttons and put them on !pressed status
        buttons = [b for b in self.bt_frame.children.values() if 'Build.TButton' in b.cget('style') and b.instate(['pressed'])]
        for button in buttons:
            button.state('!pressed')

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
        return obj_info_str.encode('ascii', errors='xmlcharrefreplace')

    def saveLayout(self):
        #save buildings and assignments to file
        save_file = asksaveasfilename(title='Save Hive as:', defaultextension='.hb', initialdir=save_dir,filetypes=[('Hive Organizer file','*.hb')])
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
            member_list = self.MembersList.lines
            #remove leading numbers and coordinates

            #strip whitespaces
            member_list = [member.strip() for member in member_list]
        except AttributeError:
            #if no list exists, ignore it
            member_list = None
        
        #Write one line for each building
        with open(save_file,'wb') as file:
            #Start with Trap Coordinates if any
            if self.trap_c is not None:
                #ensure integer
                save_tc = listsub(self.trap_c,[Trap().size/2,Trap().size/2])
                save_tc =[int(c) for c in save_tc]
                line = 'TrapCoords: '+str(save_tc)+'\n'
                file.write(line.encode('ascii', errors='xmlcharrefreplace'))
            #Then Buildings
            for enc_line in building_info:
                file.write(enc_line)

            #if member list exists, save it
            if member_list is not None:
                line = 'MemberList: '+'\n'.join(member_list)
                file.write(line.encode('ascii', errors='xmlcharrefreplace'))
        #set zoom_status back to original setting
        if zoom_status:
            self.paint_canvas.zoom()

    def loadLayout(self):
        #load previously saved layout
        lines=''
        ml_data = str()
        load_file = askopenfilename(title='Load Hive file:',initialdir=save_dir,defaultextension='.hb',filetypes=[('Hive Organizer file','*.hb'), ('All files','*.*')])   
        if load_file:
            with open(load_file,'r') as file:
                lines=file.readlines()
        # only if data was read
        if lines:
            #clear canvas before loading:
            self.paint_canvas.delete('all')
            self.paint_canvas.buildings= []
            #set the relevant values and add the grid
            self.setup()
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
                        self.MembersList = MembersList(ml_data,geometry=("{}x{}+{}+{}".format(250, self.winfo_height(),self.winfo_x()+self.winfo_width(),self.winfo_y())))
                        for member in self.MembersList.members:
                            member.changeState('!current')           
                # there is no list
                except AttributeError:
                    self.MembersList = MembersList(ml_data,geometry=("{}x{}+{}+{}".format(250, self.winfo_height(),self.winfo_x()+self.winfo_width(),self.winfo_y())))
                    #remove active player tag
                    for member in self.MembersList.members:
                        member.changeState("!current")

            # reset Trap Coordinates, then add the buildings
            self.resetTrapCoord()
            for line in lines:
                self.buildHive(line)
            #put origin marker
            self.paint_canvas.originMarker()   

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
            regex_assign = r'\[(-?\d+\.\d+),\s*(-?\d+\.\d+)\].{,3}\&#8364;\&#8364;([^\&]+)\&#8364;\&#8364;'
            regex = r'\[(-?\d+\.\d+),\s*(-?\d+\.\d+)\]'
            coords_str = re.findall(regex,line)
            #result is list of tuples of strings, e.g. [('1.0', '2.5'), ('5.00', '7.25'), ('77.1', '88.8')]
            #for cities, check if they have assigned members
            if block == 'City':
                assignments = re.findall(regex_assign,line)
            #result is list of tuples of strings, e.g. [('1.0', '2.5','Member1'), ('5.00', '7.25','Member2'), ('77.1', '88.8','Member3')]
            #convert into list of coordinates
            for ct in coords_str:
                coords=(listadd(list(map(float,ct)),self.paint_canvas.origin))
                #then paint them:
                build_new = eval(command)
                build_new.paint(canvas, coords,grid=False)
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
                            member = find(lambda f: f.name == member_name, ML.members)
                            if member:
                                member.changeState("new current")
                            #if member is not found, add them to the list
                            else:
                                self.MembersList.addMember(Member(name=member_name))
                            self.paint_canvas.assignMember(self.MembersList,city=city)

    def loadMembersList(self):
        load_file = askopenfilename(title='Load Member List:',initialdir=save_dir, defaultextension='.txt', filetypes=[('Member List text file','*.txt'), ('All files','*.*')]) 
        if load_file:
            with open(load_file,'r') as file:
                lines=file.readlines()
        #is there already a members list?
        try:
            if self.MembersList.winfo_exists():
                self.updateMembersList(lines)
                return
        #either there never was a members list or the window was closed:
        except AttributeError:
            pass
        self.MembersList = MembersList(lines,geometry=("{}x{}+{}+{}".format(250, self.winfo_height(),self.winfo_x()+self.winfo_width(),self.winfo_y())))

    def updateMembersList(self,ml_data):
        #what to do if new List is loaded when list already exists
        response = self.warn_window('Member List already active!\nOverwrite existing Member List,\n try to merge both lists or ignore list in File?', 
                                    buttons = 3, b_text=['Overwrite','Merge','Ignore'])
        if response == 'overwrite':
            #remove existing list
            self.MembersList.destroy()
            #and generate new one
            self.MembersList = MembersList(ml_data,geometry=("{}x{}+{}+{}".format(250, self.winfo_height(),self.winfo_x()+self.winfo_width(),self.winfo_y())))
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
        top.title("Isometric View")
        top.geometry("{}x{}+{}+{}".format(self.winfo_width(), self.winfo_height()+40,self.winfo_x()+20,self.winfo_y()+20))
        tk.Button(top, text="Close", command=top.destroy).pack()
        top_canvas = IsoCanvas(top, width=self.winfo_width(), height=self.winfo_height(),bg='white')
        top_canvas.pack()
        top_canvas.showMember = None
        top_canvas.cities = canvas.cities
        cos_val = math.cos(math.radians(angle))
        sin_val = math.sin(math.radians(angle))
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
                #if i%2 == 0:
                # x_rot = x*cos(angle) - y*sin(angle) + x_center
                x_rot = c[0] * cos_val - c[1] * sin_val + canvas.origin[0]
                # y_rot = x*sin(angle) + y*cos(angle) + y_center
                y_rot = c[0] * sin_val + c[1] * cos_val + canvas.origin[1]
                rot_coords[i] = [x_rot, y_rot]

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
              
def getPoly(coords):
    # provides polygon coordinates from rectangle coordinates
    poly_coords = list()
    # first top left, same as rectangle
    poly_coords.append([coords[0],coords[1]])
    # lower left
    poly_coords.append([coords[0],coords[3]])
    # lower right
    poly_coords.append([coords[2],coords[3]])
    # upper right
    poly_coords.append([coords[2],coords[1]])
    return poly_coords

def showAssignment(event, canvas):
    #show name of assigned member in a box
    #get active object

    current = canvas.find_withtag(tk.CURRENT)[0]
    #get member from tag of event
    member = canvas.findAssignee(current)
    #list(set(canvas.gettags(current)).intersection(set(canvas.cities.keys())))[0] 

    if event.type == tk.EventType['Enter']:
        coords = canvas.coords(current)
        #cur_cent = center(coords)
        #city_size = City().size*City().multiplier*2
        #coordinates for box relativ to city
        # get minimal y-value, whether it's a rectangle or a polygon
        coords[1] = min(list(map(lambda x:coords[x], range(1,len(coords),2))))
        # the width of '0' is only a placeholder.
        # it is made to fit the text below
        coords_rec = [coords[0], coords[1]-20, coords[0], coords[1]]

        # Create box for hover text
        canvas.showMember = [canvas.create_rectangle(*coords_rec,fill='#FCE69a')]
        #coordinates of text relative to box upper left corner
        coords_text = listadd(coords_rec, [3, 1 ,0 ,0])
        canvas.showMember.append(canvas.create_text(coords_text[0], coords_text[1], anchor=tk.NW, text=member))
        #resize box to fit text
        coords_text = canvas.bbox(canvas.showMember[-1])
        coords_rec = listadd(coords_text,[-3, 0, 3, 0])
        canvas.coords(canvas.showMember[0],*coords_rec)
    
    elif event.type == tk.EventType['Leave']:
        #remove hover field
        try:
            canvas.delete(*canvas.showMember)
        #or do nothing if it is not iterable, i.e. is not set yet
        except TypeError:
            pass


def selectBlock(event):
    #move current block with mouse
    canvas = event.widget
    selected = set(canvas.find_overlapping(event.x-1, event.y-1, event.x+1, event.y+1))

    #checks on selected area
    # already selected by area?
    area_select = set(canvas.find_withtag('selected'))
    # click outside of selected area releases the select
    if not selected.intersection(area_select):
        canvas.dtag('all', 'selected')
        for select in area_select:
            if 'building' in canvas.gettags(select):
                canvas.itemconfig(select, stipple='')
    #else, clicked inside
    else:
        for ab in area_select:
            #get correct floor for buildings in area select
            if 'building' in canvas.gettags(ab):
                building = canvas.getBuildingFromId(ab)
                for id in building.id.values():
                    canvas.addtag_withtag('selected', id)
        #delete if erease mode on
        if canvas.erase:
            canvas.addtag_withtag('erase','selected')
        else:
            #move selected block
            canvas.addtag_withtag('move','selected')
            canvas.dtag('all', 'selected')

    #if erase is on, erase block instead of painting or moving
    erase = canvas.erase
    
    #only paint new building if mouse not over existing building and building button is active
    paint_mode = canvas.master.active_button and not erase and not canvas.assign_mode
    if not selected.intersection(set(canvas.find_withtag('building'))) and paint_mode:
        #list makes it easier than working with int
        selected = list()
        #extend list if more than one object selected, else append value
        nb = canvas.block.paint(canvas,[event.x,event.y],grid=False)
        try:
            #has to switch order, as building needs to be last
            selected.extend(nb)
        except TypeError:
            selected.append(nb)
        #only move buildings!
    if selected: 
        block = None
        for select in selected:
            if 'building' in canvas.gettags(select):
                #canvas.new_block = list()
                #canvas.new_block.append(select)
                canvas.new_block = select
                # remember building
                new_building = canvas.getBuildingFromId(select)
                #if erase is on, erase block instead of painting or moving
                if erase:
                    canvas.addtag('erase', 'withtag', select)
                #if the selected building is a city and the assign mode is on, assign city to member
                elif canvas.assign_mode and 'City' in canvas.gettags(select):    
                    canvas.assignMember(ML=canvas.master.MembersList,city=select)
                    # No selection in assign mode!
                    canvas.dtag('all', 'selected')
                else:
                    if new_building is not None:
                        for id in new_building.id.values():
                            canvas.addtag_withtag('move', id)
                            canvas.itemconfig(id,fill='blue')
                    else:
                        canvas.addtag_withtag('move', select)
                        canvas.itemconfig(select,fill='blue')
                canvas.startxy = (event.x, event.y)
                #find type of building
                #get first building type (should be only building type)
                block = list(set(canvas.gettags(canvas.new_block)) & canvas.master.buildings)[0]
                # Only take highest building, leave loop if found
                break
        
        if erase:
            eraseBlock(canvas)
            return
        if block is not None:
            # define new block type
            canvas.block = eval(f"{block}()")
            canvas.block.canvas= canvas

def eraseBlock(canvas):
    # simply delete all blocks tagged 'erase'
    blocks_to_erase = canvas.find_withtag('erase')
    for block in blocks_to_erase:
        canvas.removeBuilding(block)
    #No block selected
    canvas.new_block = None

def moveBlock(event):
    #move current block with mouse
    canvas = event.widget
    #if there is already a selected block, move it, else ignore it
    move_blocks = canvas.find_withtag('move')
    if len(move_blocks) != 0:
        canvas.config(cursor='fleur')
        try:
            for new_block in move_blocks:
                dx, dy = event.x-canvas.startxy[0], event.y-canvas.startxy[1]
                canvas.move(new_block,dx,dy)   
            canvas.startxy = (event.x, event.y)
        except TypeError:
            dx, dy = event.x-canvas.startxy[0], event.y-canvas.startxy[1]
            canvas.move(move_blocks,dx,dy)   
            canvas.startxy = (event.x, event.y)
        #also show coordinates when moving
        canvas.showCoords(event)

def putBlock(event):
    #paint the block
    canvas = event.widget
    # if canvas.new_block is not defined, set it to 'None'
    try:
        type(canvas.new_block)
    except AttributeError:
        canvas.new_block = None

    # Do not put or delete block if in assign mode
    if canvas.new_block is not None and not canvas.assign_mode:
        #get the building from the building list
        new_building = canvas.getBuildingFromId(canvas.new_block)
        if isinstance(new_building,Block):
            new_block = new_building.id['building']
            #correct colors
            for part in new_building.id.values():
                if 'floor' in canvas.gettags(part):
                    canvas.itemconfig(part,fill=new_building.floor_color)
                elif 'member' in canvas.gettags(part):
                    canvas.itemconfig(part,fill=used_colors["assign"])
                else:
                    canvas.itemconfig(part,fill=new_building.color,stipple='')
                #remove 'move'status from new_block
                canvas.dtag(part,'move')
        else:
            new_block = new_building
            canvas.dtag(new_block,'move')
        #take coordinates of center of building, NOT event coordinates!
        ccoords = center(canvas.coords(new_block))

        #check collision in canvas coords BEFORE applying grid!
        delta_x, delta_y = checkCollision(canvas, new_block)
        #change grid_coordinates if neccessary
        
        #calculate new coordinates
        grid_coords = canvas.convCoord2Grid([ccoords[0]+delta_x, ccoords[1]+delta_y],block=canvas.block)
        
        #move building and check for collision on new location
        #canvas.delete(*canvas.new_block)
        canvas.moveBuilding(new_building, grid_coords, grid=True, rel=False)
        #if it has a floor, take only the building
        delta_x, delta_y = checkCollision(canvas, new_block)

        # collect all positions the block was tried to put
        grid_coords_hist = list()
        while delta_x != 0 or delta_y != 0:
            # check for further collisions
            grid_coords_hist.append(grid_coords)
            grid_coords = canvas.convCoord2Grid([ccoords[0]+delta_x, ccoords[1]+delta_y],block=canvas.block)
            canvas.moveBuilding(new_building, grid_coords, grid=True, rel=False)
            delta_x, delta_y = checkCollision(canvas, new_block)
            # if position was already tried, break (otherwise inifinty loop!)
            if grid_coords in grid_coords_hist:
                # if the block is part of a bigger selected area, don't blink
                if canvas.find_withtag('move'):
                    break
                else:
                    canvas.itemconfig(new_block,fill='red')
                    canvas.update()
                    canvas.after(300)
                    canvas.itemconfig(new_block,fill='blue')
                #return
                break
        #get total delta of movement
        delta_coord = listsub(center(canvas.coords(new_block)),ccoords)

        # now move all selected blocks by the accumulated delta
        for select in canvas.find_withtag('move'):
            canvas.move(select,*delta_coord)
            #remove stipple if it is not a floor
            if 'floor' not in canvas.gettags(select):
                canvas.itemconfig(select,stipple='')
            canvas.dtag(select,'move')
        # reset cursor
        canvas.config(cursor='left_ptr')
        # reset building type if active_button
        if canvas.master.active_button:
            if type(canvas.block) is type(canvas.active_block):
                # There can be only one HQ and one Trap
                if isinstance(canvas.block, HQ) or isinstance(canvas.block, Trap):
                    canvas.master.activateButton(canvas.master.active_button)
            else:
                canvas.block = canvas.active_block
        #remove 'moved' but should never be reached
        for mb in canvas.find_withtag('move'):
            canvas.delete(mb)
            
        canvas.new_block = None
    #at the end, put assignment indicators on top
    canvas.tag_raise('member','all')

def checkCollision(canvas, block):
    # check if new block collides with existing building
    # tk rectangles give lower right corner OUTSIDE the rectangle, 
    # so overlap area needs to be reduced to actual size
    canv_box = listadd(canvas.coords(block),[1,1,-1,-1])
    #canv_box.extend(block.convGrid2Coord(grid_box[2:4]))
    #find list of all other blocks covering this area (except the new block itself)
    selected = list(canvas.find_overlapping(*canv_box))
    #block itself is always in the list, so remove it
    selected.remove(block)
    #grid coordinates block has to move
    delta_coord = [0, 0]
    for sb in selected:
        if 'building' in canvas.gettags(sb): 
            #get grid coordinates of sb rectangle, again reduce size of rectangle
            #sb_box = listadd(canvas.coords(sb),[0,0,-1,-1])      
            sb_box = canvas.coords(sb)      
            delta_coord = pushBuilding(sb_box,canv_box)

    return delta_coord[0], delta_coord[1]

def pushBuilding(old_bb,new_bb):
            #get deltas to move new_building outside ol_building with minimal distance
            #old_bb: box of existing building in grid coordinates
            #new_bb: box of new building in grid coordinates
            #: make proper building class and methods

            delta_coord = [0 , 0]
            
            #all buildings are squares!
            #delta_size = abs(old_bb[2]-old_bb[0]) - abs(new_bb[2]-new_bb[0])
            new_size = abs(new_bb[2]-new_bb[0])
            old_size = abs(old_bb[2]-old_bb[0])
            #x-axis:
            #change if overlap in x-axis
            if new_bb[0] < old_bb[2] and new_bb[2] > old_bb[0]:
                delta_cx = center(new_bb)[0] - center(old_bb)[0] 

                if delta_cx == 0:
                    delta_coord[0] = abs(new_bb[2]-new_bb[0])
                else:
                    #delta_x = delta_x/abs(delta_x)*delta_size/2 -delta_x
                    delta_coord[0] = (new_size+old_size)/2 - abs(delta_cx)
                    #consider direction, apply sign
                    delta_coord[0] *= delta_cx/abs(delta_cx)
            #y-axis:
            #change if overlap in y-axis
            if new_bb[1] < old_bb[3] and new_bb[3] > old_bb[1]:
                delta_cy = center(new_bb)[1] - center(old_bb)[1]
                if delta_cy == 0:
                    delta_coord[1] = abs(new_bb[3]-new_bb[1])
                else:
                    delta_coord[1] = (new_size+old_size)/2 - abs(delta_cy)
                    #consider direction, apply sign
                    delta_coord[1] *= delta_cy/abs(delta_cy)
            #only one axis should be necessary unless it is completely covered/covering?
            #use smaller absolute delta (only if both axos have a delta)
            #is there a 0 velue in delta_coordss, then leave it
            if 0 not in delta_coord:
                delta_coord[delta_coord.index(max(delta_coord,key=abs))] = 0

            return delta_coord

MW = MainWindow()
MW.mainloop()
