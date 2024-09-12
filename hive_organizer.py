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
import webbrowser
from PIL import Image, ImageTk


def callback(url):
    webbrowser.open_new(url)

# script dir will be used as initial for load/save
script_dir=os.path.dirname(os.path.realpath(__file__))
init_dir =os.path.join(script_dir,'hive')
save_dir = os.path.join(init_dir,'save')

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

class Block():
    def __init__(self,size=0, area=0,coords=[0,0], color='red',tag = '',multiplier=5, id=dict(), floor_color=used_colors["floor"], text_color =used_colors["floor"]):
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
        self.multiplier = multiplier
        self.tag=tag
        self.id = dict()
        self.id.update(id)
        self.floor_color = floor_color
        self.text_color = text_color
    
    def paint(self,canvas,coords,grid=True):
        self.canvas = canvas
        #x1,self.coords[1] = (self.coords[0]-self.size)*self.multiplier*2,(self.coords[1]-self.size)*self.multiplier*2
        
        #self.coords= [canvas.origin[0]+coords[0]*self.multiplier*2,canvas.origin[1]+coords[1]*self.multiplier*2]
        if grid:
            self.coords = self.convGrid2Coord(coords)
        else:
            self.coords=coords

        building = canvas.create_rectangle(self.coords[0]-self.size*self.multiplier,self.coords[1]-self.size*self.multiplier,
                                self.coords[0]+self.size*self.multiplier, self.coords[1]+self.size*self.multiplier, 
                                fill=self.color,tags=('building',self.tag))
        #Only add 'real' buildings
        if not isinstance(self,DummyBlock):
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
    
    """def convCoord2Grid(self,coords):
        #convert normal coordinates into grid positions and lock into grid
        #Attention: for CANVAS coordinates POSITIVE Y is DOWN
        #but for GRID coordinates POSITIVE Y is UP!   
    
        grid_coords = [0,0]
        #objects of even size need to shift by 0.5 grid points as origin is at a half-point
        grid_shift = (self.size+1)%2*0.5
        #move to closest grid line, not only to the right...
        #Y coord is negative, see above
        dummy_c = [(coords[0]-self.canvas.origin[0])/(self.multiplier*2), (-coords[1]+self.canvas.origin[1])/(self.multiplier*2)]
        round_c = [round((coords[0]-self.canvas.origin[0])/(self.multiplier*2)), round((-coords[1]+self.canvas.origin[1])/(self.multiplier*2))]
        for i in range(2):
            if dummy_c[i] > round_c[i]:
                grid_coords[i] = round_c[i] + grid_shift
            else:
                grid_coords[i] = round_c[i] - grid_shift

        return grid_coords"""
    
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
    
class DummyBlock(Block):
    def __init__(self,size=1, area=0,coords=[0,0],color='',tag = ''):
          super().__init__(size, area,coords,color,tag)

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

def listadd(a,b):
    #subtrahiert list b von liste a
    if len(a) is not len(b):
        return []
    result_list = list(map(lambda x,y: x+y,a,b))
    return result_list

def listsub(a,b):
    #subtrahiert list b von liste a
    if len(a) is not len(b):
        return []
    result_list = list(map(lambda x,y: x-y,a,b))
    return result_list

def center(box):
    #center point of the rectangle
    return [(box[0]+box[2])/2 , (box[1]+box[3])/2]

class MembersList(tk.Toplevel):
    # Defines the window with the list of member names
    #TODO: Scroll function
    def __init__(self,lines,geometry='100x100+100+100'):
        super().__init__()
        self.lines = lines
        #buld member list and show in seperate Window
        self.title("Alliance Members List")
        self.geometry(geometry)
        
        tk.Button(self, text="Close", command=self.destroy).pack()
        self.members_list = tk.Text(self)
        self.members_list.pack(fill='y', expand=True)
        self.members_list.tag_configure("current_line", background=used_colors["current"])
        self.members_list.tag_configure("assigned", background=used_colors["assign"])
        self.members_list.tag_raise("current_line", "assigned")
        self.members_list.tag_raise("sel", "current_line")
        self.members_list.insert('1.0','\n')
        #Fill list
        for n,line in enumerate(self.lines):
            self.members_list.insert('2.0 + ' + str(n)  +' lines',str(n+1)+'. ')
            self.members_list.insert('2.end + ' + str(n)  +' lines',line.lstrip())
        self.members_list.tag_add("current_line", "2.0", "2.end")
        #select name by mouse klick
        self.bind('<Button-1>', self.selectName)

    def selectName(self,event):
        #select the klicked name
        #get current line
        index_line = self.members_list.index(tk.CURRENT).split('.')[0]
        # set current line and remove old seting
        self.members_list.tag_remove("current_line",'1.0',"end")
        self.members_list.tag_add("current_line",index_line+'.0',index_line+'.end')
    
    def merge(self,new_members):
        #merge new list of names with existing one
        old_list = self.members_list.get('1.0','end')
        for new_member in new_members:
            #remove whitespaces and CR at start and end of name
            new_member=new_member.strip()
            #Is member in list already?
            if old_list.find(new_member) == -1:
                self.addMember(new_member)

    def addMember(self,member_name):
        #add new member to MembersList
        ml=self.members_list
        
        line_num=ml.index('end').split('.')[0]
        #last line is empty line? Find last line with text
        while ml.compare(line_num+'.end', '==', line_num+'.0'):
            line_num=str(int(line_num)-1)
        new_idx=ml.get(line_num+'.0',line_num+'.end')
        try:
            new_idx=new_idx.split('.')[0]
            #is it a number?
            new_idx = self.getNewNumber()
        except ValueError:
            new_idx=100+int(line_num)
        #Cont here
        ml.tag_remove("current_line",'1.0','end')
        ml.insert(str(int(line_num)+1)+'.0','\n'+str(new_idx)+'. '+member_name,"current_line") 

    def getNewNumber(self):
        #get all numbers currently used in the MembersList
        usedNums=set()
        #max_lines = int(self.members_list.index("end").split('.')[0])-1
        lines = self.members_list.get('1.0','end').split('\n')
        for line in lines:
            #if there is a number at the beginning of the line, take it, otherwise ignore
            try:
                usedNums.add(int(line.split('.')[0]))
            except ValueError:
                pass
        if usedNums:
            #return highest used number+1
            return max(usedNums)+1
        else:
            return 1

class PaintCanvas(tk.Canvas):
    def __init__(self, master, width=0, height=0, bg='white', print_coords = True):
        super().__init__(master=master,width=width, height=height, bg=bg)
        self.origin = [0,0]

        self.erase = False
        self.print_coords = print_coords
        self.block = None
        self.grid_on = False
        self.assign_mode = False
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

        self.makeGrid()

    def setup(self):
        # set origin of grid and activate grid
        self.block = None
        self.buildings=list()
        self.cities = dict()
        self.showMember = None
        self.origin = [self.winfo_width()/2, self.winfo_height()/2]
        self.makeGrid()

    def convCoord2Grid(self,coords,block=None):
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
            multiplier=Block().multiplier
    
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

        return grid_coords

    def showCoords(self, event):
        #show canvas coordinates in lower right corner
        # and grid coordinates in lower left corner
        if self.print_coords:
            text='{}, {}'.format(str(event.x), str(event.y))
            #TODO: need a real conversion to grid
            #db = DummyBlock()
            #dummy = db.paint(self, coords=[0, 0])
            grid = self.convCoord2Grid([event.x, event.y])
            #self.delete(dummy)
            #self.removeBuilding(dummy)
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

    """def getBuilding(self ,building):
        #get building Block
        #use only first, if list is given
        if isinstance(building,list):
            building=building[0]
        for block in self.buildings:
            if building in block.id.values():
                return block
        #if for some reason building is not in list just return the input
        return building"""
    
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
        self.buildings = []
        #but add the grid
        self.makeGrid()
        #remove assignments from member list (if any)
        try:
            self.master.MembersList.members_list.tag_remove('assigned','1.0','end')
        except AttributeError:
            pass
        #put HQ and Trap
        HeadQuarter = HQ(coords=[-11, 5]) 
        NewTrap = Trap(coords = [0,0])

        #self.origin = [self.winfo_width()/2,self.winfo_height()/2]

        #Set Trap at origin
        NewTrap.paint(self,NewTrap.coords)
        #put origin marker
        self.create_rectangle(self.winfo_width()/2-1,self.winfo_height()/2-1,self.winfo_width()/2+1,self.winfo_height()/2+1)
        
        #then HQ
        HeadQuarter.paint(self,HeadQuarter.coords)
        #floor is under buildings
        self.tag_lower('floor','building')    

    def makeGrid(self,grid_space = 6):
        #draw grid on canvas
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
    
    def assignMember(self,ml,city):
        #assign selected member to building
        #ml: MembersList
        cl_index = ml.tag_ranges("current_line")
        #check if there actually is a current line
        #otherwise ignore it
        if not cl_index:
            return
        current_line = ml.get(*cl_index).split('.')
        try:
            member_num = int(current_line[0])
        except ValueError:
            #no number in line, so add it
            member_num = ml.master.getNewNumber()
            ml.insert(cl_index[0],str(member_num)+'. ',"current_line")
            #update tag
            cl_index = ml.tag_ranges("current_line")
            current_line = ml.get(*cl_index).split('.')
            #self.master.warn_window('Member has no number!\nPlease add new number: <XX. MemberName>')
            #return
        member_name = current_line[1].strip()
        self.addtag_withtag('assigned',city)
        #remove old assignement as one member can have only one city
        if member_name in self.cities.keys():
            #TODO make function or method of City()
            old_city = self.cities[member_name]
            text_field = set(self.find_overlapping(*self.coords(old_city))).intersection(set(self.find_withtag('member')))
            self.delete(*text_field)
            self.dtag(old_city, member_name)
            self.cities.pop(member_name)
        #and remove previous owner of city (if any)
        if city in self.cities.values():
            old_owner = [k for k,v in self.cities.items() if v == city][0]
            # remove from owner list
            self.cities.pop(old_owner)
            #remove owner tag from city
            self.dtag(city, old_owner)
            #and remove text field w number from city
            text_field = set(self.find_overlapping(*self.coords(city))).intersection(set(self.find_withtag('member')))
            #text_field is a set, so adress as pointer
            self.delete(*text_field)
            #also: owner should no longer be 'assigned'
            line=ml.search(old_owner,'1.0').split('.')[0]
            ml.tag_remove("assigned",line+'.0',line+'.end')

        self.cities.update({member_name : city})
        #also tag the city in question
        self.addtag_withtag(member_name, city)
        # and the other way around
        self.assigments = { id : city for city, id in self.cities.items()}
        #also mark it in member list:
        ml.tag_add("assigned",*cl_index)
        #and remove the current selection
        ml.tag_remove("current_line",*cl_index)

        #bind to the city (not the text!)
        self.tag_bind(member_name,'<Enter>',func=lambda event: self.showAssignment(event=event,member=member_name))
        self.tag_bind(member_name,'<Leave>',func=lambda event: self.showAssignment(event=event,member=member_name))

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

    def showAssignment(self, event, member):
        #show name of assigned member in a box
        #get active object
        current = self.find_withtag(tk.CURRENT)[0]
        
        if event.type == tk.EventType['Enter']:
            coords = self.coords(current)
            #cur_cent = center(coords)
            city_size = City().size*City().multiplier*2
            #coordinates for box relativ to city
            # the width of '1' is only a placeholder.
            # it is made to fit the text below
            coords_rec = listadd(coords, [0, -city_size, 1,-city_size])
            # Create box for hover text
            self.showMember = [self.create_rectangle(*coords_rec,fill='#FCE69a')]
            #coordinates of text relative to box upper left corner
            coords_text = listadd(coords_rec, [3, 1 ,0 ,0])
            self.showMember.append(self.create_text(coords_text[0], coords_text[1], anchor=tk.NW, text=member))
            #resize box to fit text
            coords_text = self.bbox(self.showMember[-1])
            coords_rec = listadd(coords_text,[-3, 0, 3, 0])
            self.coords(self.showMember[0],*coords_rec)
        
        elif event.type == tk.EventType['Leave']:
            #remove hover field
            try:
                self.delete(*self.showMember)
            #or do nothing if it is not iterable, i.e. is not set yet
            except TypeError:
                pass

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Hive Organizer \t'+chr(169)+' 2024 by Shivkala')

        #define buttons and button actions
        # size depending on screen size
        geo_fac = 0.7
        wwidth = self.winfo_screenwidth()*geo_fac
        wheight = self.winfo_screenheight()*geo_fac
        
        fpady = 3
        fpadx = 5

        #ttk styles
        self.style = ttk.Style()
        theme='black'
        self.tk.call("source",os.path.join(init_dir,theme,theme+".tcl"))

        self.style.theme_use(theme)
        self.style.configure('TButton', padding= [4, 4,4,4])
        self.style.map('TButton.border',
            relief=[('pressed', 'sunken'),
                    ('!pressed', 'raised')])   

        self.style.configure('Assign.TButton')
        self.style.map('Assign.TButton',
            foreground=[('pressed','black'),('active', 'blue')],
            background=[('disabled', 'grey'),
                        ('pressed', used_colors["assign"]),
                        ('active', used_colors["current"])],       
            highlightcolor=[('focus', 'green'),
                            ('!focus', 'red')])
            #relief=[('pressed', 'sunken'),
            #        ('!pressed', 'raised')])
        
        self.style.configure('TButton', padding= [4, 2,4,2])
        self.style.map('TButton',
            relief=[('pressed', 'sunken'),
                    ('!pressed', 'raised')])        
        self.style.configure('Build.TButton',
            padding= [4, 2,4,2])
        self.style.map('Build.TButton',
            foreground=[('active','blue'),
                        ('!active','black')],
            background=[('active', used_colors["flag"]),
                        ('!active','white')])              
        self.style.map('Build.TButton',
            highlightcolor=[('focus', 'green'),
                            ('!focus', 'red')],
            relief=[('pressed', 'sunken'),
                    ('!pressed', 'raised')])
        
        self.style.configure('City.Build.TButton')
        self.style.map('City.Build.TButton', 
                       background=[('active', used_colors["city"]),
                        ('!active','pressed', used_colors["hq"]), 
                        ('!active','white')]) 
        
        self.style.configure('CG.TButton')                     
        self.style.map('CG.TButton',
            highlightcolor=[('focus', 'green'),
                            ('!focus', 'red')])
            #relief=[('pressed', 'sunken'),
            #        ('!pressed', 'raised')])
        
        self.style.configure('Erase.TButton') 
        self.style.map('Erase.TButton',       
                        background=[('pressed', used_colors["erase2"]),
                                    ('!pressed',used_colors["erase1"])])                 
        self.style.map('Erase.TButton',
            highlightcolor=[('focus', 'green'),
                            ('!focus', 'red')],
            relief=[('pressed', 'sunken'),
                    ('!pressed', 'raised')])

        #Frame
        bt_frame=ttk.Frame(self, width = wwidth, height = 65)
        bt_frame.grid(row=0,column=0)
        self.bt_frame = bt_frame
        #load/save/etc
        self.save_button = ttk.Button(bt_frame, text='Save', command=self.saveLayout)
        self.save_button.grid(row = 0, column=0, sticky='news',padx=fpadx, pady=fpady)

        self.load_button = ttk.Button(bt_frame, text='Load', command=self.loadLayout)
        self.load_button.grid(row = 0, column=1, sticky='news',padx=fpadx, pady=fpady)

        self.isoview_button = ttk.Button(bt_frame, text='Isometric', command=self.isometricView)
        self.isoview_button.grid(row = 0, column=7, sticky='news',padx=fpadx, pady=fpady)
        
        self.default_button = ttk.Button(bt_frame, text='Default', style='TButton', command=self.default)
        self.default_button.grid(row = 0, column=8, sticky='nes',padx=fpadx, pady=fpady)

        self.members_button = ttk.Button(bt_frame, text='Member List', command=self.loadMembersList)
        self.members_button.grid(row = 0, column=9, sticky='news',padx=fpadx, pady=fpady)

        self.assign_button = ttk.Button(bt_frame, text='Assign',style='Assign.TButton', command=self.assignMode)
        self.assign_button.grid(row = 0, column=10, sticky='news',padx=fpadx, pady=fpady)


        #buildings
        #self.city_button = tk.Button(bt_frame, text='City', activebackground=City().color, command=self.printCity)
        self.city_button = ttk.Button(bt_frame, text='City',style='City.Build.TButton', command=self.printCity)
        self.city_button.grid(row = 1, column=1, sticky='news',padx=fpadx, pady=fpady)

        self.flag_button = ttk.Button(bt_frame, text='Flag',style='Build.TButton', command=self.printFlag)
        self.flag_button.grid(row=1, column=2, sticky='news',padx=fpadx, pady=fpady)

        self.rock_button = ttk.Button(bt_frame, text='Rock',style='Build.TButton', command=self.printRock)
        self.rock_button.grid(row=1, column=3, sticky='news',padx=fpadx, pady=fpady)

        self.hq_button = ttk.Button(bt_frame, text=' HQ ',style='Build.TButton', command=self.printHQ)
        self.hq_button.grid(row=1, column=4, sticky='news',padx=fpadx, pady=fpady)

        self.trap_button = ttk.Button(bt_frame, text='Trap',style='Build.TButton', command=self.printTrap)
        self.trap_button.grid(row=1, column=5, sticky='news',padx=fpadx, pady=fpady)

        self.coord_button = ttk.Button(bt_frame, text='Coords',style='CG.TButton', command=self.printCoords)
        self.coord_button.state(['pressed'])
        self.coord_button.grid(row=1, column=8, sticky='e',padx=30, pady=fpady)

        self.grid_button = ttk.Button(bt_frame, text='Grid', style='CG.TButton', command=self.gridOnOff)
        self.grid_button.state(['pressed'])
        self.grid_button.grid(row=1, column=9, sticky='ew',padx=fpadx, pady=fpady)

        self.erase_button = ttk.Button(bt_frame, text='Erase', style='Erase.TButton',command=self.eraseBuilding)
        self.erase_button.grid(row=1, column=10, sticky='e',padx=30, pady=fpady)

        #donate button
        db_im = Image.open(os.path.join(init_dir,'donate-button4.png'))
        db_im = db_im.resize((50,50))
        self.db_im = ImageTk.PhotoImage(db_im)
        
        self.donate_button = ttk.Button(bt_frame, image=self.db_im, command=self.donate, cursor='heart')
        #self.donate_button.grid(row = 0, column=12, sticky='ew',padx=fpadx, pady=fpady)
        self.donate_button.grid(row = 0, rowspan=2, column=12, sticky='ew',padx=fpadx, pady=fpady)

        bt_frame.grid_propagate(False)

        self.iconbitmap(default = os.path.join(init_dir,'icon.ico'))

        #setup Canvas
        self.paint_canvas = PaintCanvas(self, width=wwidth, height = wheight, bg='white')

        #paint canvas
        self.paint_canvas.grid(row=1,column=0)
        self.paint_canvas.erase = False
        self.paint_canvas.print_coords = True

        #draw default after starting mainloop
        self.after(100,self.setup)

    def setup(self):
        #performed once mainloop is started
        self.paint_canvas.setup()
        self.active_button = None
        self.buildings = set(['HQ','City','Flag','Trap','Rock'])

    def donate(self, width=300, height=300):
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

        db_im2 = ImageTk.PhotoImage(Image.open(os.path.join(init_dir,'donate-button4.png')).resize((100,100)))
        dbtn = ttk.Button(top_frame,image=db_im2,padx=10, pady=10, command=lambda: callback('https://www.paypal.com/donate/?hosted_button_id=J3NY5KH92LC7L'))
        dbtn.grid(row=1, column = 0)
        qr_im = ImageTk.PhotoImage(Image.open(os.path.join(init_dir,'Donate QR Code.png')).resize((100,100)))
        dlabel = ttk.Label(top_frame,image=qr_im,padx=10, pady=10)
        dbtn.grid(row=1, column = 2)
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
        #test rotation
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
        #Debug
        obj_info_str = tag+': '+str(obj_info)+'\n'

        return obj_info_str.encode('ascii', errors='xmlcharrefreplace')
        #EndDebug
        #return obj_info

    def saveLayout(self):
        #save buildings and assignments to file
        save_file = asksaveasfilename(title='Save Hive as:', defaultextension='.hb', initialdir=save_dir,filetypes=[('Hive Organizer file','*.hb')])
        self.assigments = { id : city for city, id in self.paint_canvas.cities.items()}
        building_info = list()
        #get list of lists for all building coordinates
        for building in self.buildings:
            building_info.append(self.buildingInfoEncoder(building))

        try:
            self.MembersList.winfo_exists()
            member_list = self.MembersList.members_list.get('1.0','end')
            #remove leading numbers
            regex=r'\d+\. (.*)'
            member_list = re.findall(regex,member_list)
        except AttributeError:
            #if no list exists, ignore it
            member_list = None
        #Write one line for each building
        with open(save_file,'wb') as file:
            for enc_line in building_info:
                file.write(enc_line)
        #End Debug
            #if member list exists, save it
            if member_list is not None:
                line = 'MemberList: '+'\n'.join(member_list)
                file.write(line.encode('ascii', errors='xmlcharrefreplace'))

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
                # there is no list
                except AttributeError:
                    pass
                    self.MembersList = MembersList(ml_data,geometry=("{}x{}+{}+{}".format(250, self.winfo_height(),self.winfo_x()+self.winfo_width(),self.winfo_y())))
                    #remove active player tag
                    self.MembersList.members_list.tag_remove("current_line",'1.0','end')
            #then add the buildings
            for line in lines:
                self.buildHive(line)

    def buildHive(self,line):
        #paint the Hive from the saved file
        canvas = self.paint_canvas
        block = None
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
            regex_assign = r'\[(-?\d+\.\d+),\s*(-?\d+\.\d+)\].{,3}\&#8364;\&#8364;([\w\s]+)\&#8364;\&#8364;'
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
                #TODO: This is painting the same building multiple times, which does not work with canvas.buildings
                build_new = eval(command)
                build_new.paint(canvas, coords,grid=False)
                #for cities, add they have assigned members
                if block == 'City':
                    for member in assignments:
                        ml = self.MembersList.members_list
                        member_coords = member[0:2]
                        member_name = member[2:][0]
                        #TODO: make method!
                        #assigned city!
                        if member_coords == ct:
                            city=build_new.id['building']
                            line_num=ml.search(member_name,'1.0').split('.')[0]
                            #check if member exists in list
                            if line_num:
                                ml.tag_add("current_line",line_num+'.0',line_num+'.end')
                            #if member is not found, add them to the list
                            else:
                                self.MembersList.addMember(member_name)
                            self.paint_canvas.assignMember(self.MembersList.members_list,city=city)

        #paint origin
        canvas.create_rectangle(canvas.origin[0]-1,canvas.origin[1]-1,canvas.origin[0]+1,canvas.origin[1]+1)    

    def loadMembersList(self):
        load_file = askopenfilename(title='Load Member List:',initialdir=save_dir, defaultextension='.txt', filetypes=[('Member List text file','*.txt'), ('All files','*.*')]) 
        if load_file:
            with open(load_file,'r') as file:
                lines=file.readlines()
        #is there already a members list?
        try:
            if self.MembersList.winfo_exists():
                self.updateMembersList(lines)
        except AttributeError:
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
            self.MembersList.members_list.tag_remove("current_line",'1.0','end')
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
        top_canvas = tk.Canvas(top, width=self.winfo_width(), height=self.winfo_height(),bg='white')
        top_canvas.pack()
        
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
                top_canvas.create_polygon(rot_coords, fill=canvas.itemcget(element,'fill'),stipple=canvas.itemcget(element,'stipple'),outline='black')
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
                    canvas.assignMember(ml=canvas.master.MembersList.members_list,city=select)
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
        
        #remove area
        #if same tag + floor and same center: correct floor selection!
        """for select in selected:
            if block is not None and block in canvas.gettags(select) and 'floor' in canvas.gettags(select) and center(canvas.coords(select)) == center(canvas.coords(new_building)):
                #if erase is on, erase block instead of painting or moving
                if erase:
                    canvas.addtag('erase', 'withtag', select)
                else:
                    canvas.new_block.append(select)
                    canvas.itemconfig(select,fill='blue')
                    canvas.addtag('move', 'withtag', select)
                #break"""
        if erase:
            eraseBlock(canvas)
            return
        if block is not None:
            # define new block type
            canvas.block = eval(f"{block}()")
            canvas.block.canvas= canvas
                
    #else:
    #    canvas.new_block = canvas.block.paint(canvas,[event.x,event.y],grid=False)
    #    canvas.addtag('move', 'withtag', canvas.new_block)
    #    canvas.startxy = (event.x, event.y)

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
            #TODO: make proper building class and methods

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
