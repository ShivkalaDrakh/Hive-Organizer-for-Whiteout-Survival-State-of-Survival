import tkinter as tk
from tkinter import ttk
from hive.utils import listadd, listsub, center, find
from hive.styles import used_colors, used_colors_default

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
    
    def paint(self,canvas,coords,grid=True,color=None,floor_color = None):
        if color is None:
            color = self.color
        self.canvas = canvas
        if grid:
            self.coords = self.convGrid2Coord(coords)
        else:
            self.coords=coords

        building = canvas.create_rectangle(self.coords[0]-self.size*self.multiplier,self.coords[1]-self.size*self.multiplier,
                                self.coords[0]+self.size*self.multiplier, self.coords[1]+self.size*self.multiplier, 
                                fill=color,tags=('building',self.tag))
        self.id.update({'building' : building})
        canvas.buildings.append(self)
        #if it is HQ or Trap, give it a popup text
        if self.tag in ['Trap','HQ','Rock','Flag']:
            self.canvas.tag_bind(building,'<Enter>',func=lambda event: showAssignment(event=event,canvas = self.canvas,tag=self.tag))
            self.canvas.tag_bind(building,'<Leave>',func=lambda event: showAssignment(event=event,canvas = self.canvas))

        #if building provides Area, add it here
        if self.area > 0:
            if floor_color is None:
                floor_color = used_colors["floor"]
            floor=canvas.create_rectangle(self.coords[0]-self.area*self.multiplier,self.coords[1]-self.area*self.multiplier,
                        self.coords[0]+self.area*self.multiplier, self.coords[1]+self.area*self.multiplier, 
                        stipple="gray12", fill=floor_color,outline ='',tags=('floor',self.tag))
            #floor is lowest unless in 'Show Floor' mode
            if not canvas.top_floor:
                canvas.tag_lower(floor)
            else:
                canvas.tag_raise(floor)
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

class Castle(Block):
    def __init__(self,size=6, area=28,coords=[0,0],color=used_colors["castle"], tag='Castle'):
          super().__init__(size, area,coords,color,tag) 

class Tower(Block):
    def __init__(self,size=2, area=0,coords=[0,0],color=used_colors["tower"], tag='Tower'):
          super().__init__(size, area,coords,color,tag) 

def showAssignment(event, canvas, tag=None):
    #show name of assigned member in a box
    #get active object

    current = canvas.find_withtag(tk.CURRENT)[0]
    # if it's a member:
    if tag is None:
        #get member from tag of event
        member = canvas.findAssignee(current)
    # else HQ, Trap, Rock, Flag
    else:
        member=tag
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
        #delete if erase mode on
        if canvas.erase.get():
            canvas.addtag_withtag('erase','selected')
        else:
            #move selected block
            canvas.addtag_withtag('move','selected')
            canvas.dtag('all', 'selected')

    #if erase is on, erase block instead of painting or moving
    erase = canvas.erase.get()
    
    #only paint new building if mouse not over existing building and building button is active
    paint_mode = canvas.master.active_button and not erase and not canvas.assign_mode.get()
    if not selected.intersection(set(canvas.find_withtag('building'))) and paint_mode:
        #list makes it easier than working with int
        selected = list()
        #extend list if more than one object selected, else append value
        block_name = getBlockName(canvas.block)
        #select correct color and paint it
        nb = canvas.block.paint(canvas,[event.x,event.y],grid=False,
                                color=used_colors[block_name],floor_color = used_colors["floor"])
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
                elif canvas.assign_mode.get() and 'City' in canvas.gettags(select):    
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
                block = list(set(canvas.gettags(canvas.new_block)) & set(canvas.master.buildings))[0]
                # Only take highest building, leave loop if found
                break
        
        if erase:
            eraseBlock(canvas)
            return
        if block is not None:
            # define new block type
            canvas.block = eval(f"{block}()")
            canvas.block.canvas= canvas

def getBlockName(block):
    return str(type(block)).split('.')[-1].split("'")[0].lower()

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
    #global used_colors
    canvas = event.widget
    # if canvas.new_block is not defined, set it to 'None'
    try:
        type(canvas.new_block)
    except AttributeError:
        canvas.new_block = None

    # Do not put or delete block if in assign mode
    if canvas.new_block is not None and not canvas.assign_mode.get():
        #get the building from the building list
        new_building = canvas.getBuildingFromId(canvas.new_block)
        if isinstance(new_building,Block):
            new_block = new_building.id['building']
            #correct colors
            for part in new_building.id.values():
                if 'floor' in canvas.gettags(part):
                    canvas.itemconfig(part,fill=used_colors["floor"])
                elif 'member' in canvas.gettags(part):
                    canvas.itemconfig(part,fill=used_colors["assign"])
                else:
                    #set color to the current selection for this building
                    canvas.itemconfig(part,fill=used_colors[getBlockName(new_building)],stipple='')
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
                # There can be only one HQ and two Traps
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
    #but still have the floor on top if so indicated
    if canvas.top_floor:
        canvas.tag_raise('floor','all')

class IsoCanvas(tk.Canvas):
    def __init__(self, master, width=0, height=0, bg='white', print_coords = True):
        super().__init__(master=master,width=width, height=height, bg=bg)
        # Create a canvas object and a vertical and a horizontal scrollbar for scrolling it.

    def findAssignee(self,id):
        #find the name of the member assigned to the id of the canvas object
        ret_val = list(set(self.gettags(id)).intersection(set(self.cities.keys())))
        #if only one member (which should always be the case) return string, not list
        if len(ret_val) == 0:
            return None
        elif len(ret_val) == 1:
            ret_val = ret_val[0] 
        return ret_val
    
#TODO: make PaintCanvas scrollable to allow for larger hives
class PaintCanvas(IsoCanvas):
    def __init__(self, master, width=0, height=0, bg="white", print_coords = True):
        super().__init__(master=master,width=width, height=height, bg=bg)
        self.master = self.winfo_toplevel()
        self.width = width
        self.height = height
        self.origin = [0,0]

        #setup button defaults
        self.erase = tk.BooleanVar()
        self.erase.set(False)
        self.print_coords = print_coords
        self.block = None
        self.top_floor= False
        self.grid_on = False
        self.assign_mode = tk.BooleanVar()
        self.assign_mode.set(False)
        self.zoom_on = False
        self.buildings=list()
        self.cities = dict()
        self.showMember = None
        self.grid_size = 6

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
        self.makeGrid(self.grid_size)

    def zoom(self, zoom_factor = 2.0):
        self.zoom_on = not self.zoom_on
        origin = self.origin
        if not self.zoom_on:
            self.master.zoom_button.state(['!pressed'])
            zoom_factor = 1/zoom_factor
        else:
            self.master.zoom_button.state(['pressed'])
        #remove coordinates
        self.delete(self.find_withtag('c_coords'))
        self.delete(self.find_withtag('g_coords'))
        #change canvas size
        self.config(height=int(self.cget('height'))*zoom_factor)
        self.config(width=int(self.cget('width'))*zoom_factor)
        size = (int(self.cget('width')), int(self.cget('height')))
        self.master.cs_frame.scrollArea(size,zoom_factor)
        #up- or downscale everything
        self.scale('all',*origin,zoom_factor,zoom_factor)
        Block.multiplier *= zoom_factor
        #re-draw the grid
        self.makeGrid(self.grid_size)

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
            self.makeGrid(self.grid_size)
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

            #remove previous coordinates
            self.removeCoords()
            #then build them anew
            #coords = fraction of visible part * canvas size
            try:
                #fraction of visible part * canvas size
                x_master = self.master.int_frame.master.xview()
                y_master = self.master.int_frame.master.yview()[1]
                #x needs two coords, left & right
                x_coords = [x * self.winfo_width() for x in x_master]
                y_coord = y_master * self.winfo_height()
            except:
                y_coord = self.winfo_height()
                x_coords = [0, self.winfo_width()]

            self.text_coord = self.create_text(x_coords[1]-10, y_coord-10, anchor=tk.SE, 
                                                    text=text, tag=('c_coords','coords'))
            self.itemconfig(self.text_coord,font=('Helvetica', 15))

            self.text_grid_coord = self.create_text(x_coords[0]+10, y_coord-10,  anchor=tk.SW,  
                                                    text=text_grid,tag=('g_coords','coords'))
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
            if 'assigned' in self.gettags(building):
                self.master.MembersList.removeCityAssignment(building, self.assignments[building])
                self.cities.pop(self.assignments[building])
                self.assignments.pop(building)
                self.delete(*self.showMember)
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
                    # the assignment indicator (canvas text) has only 2 coordinates, not 4
                    if 'member' in self.gettags(id):
                        box =[box[0]+2,box[1]+2]
                    self.coords(id,*box)
            #put assignment indicators on top
            self.tag_raise('member','all')
            #but still have the floor on top if so indicated
            if self.top_floor:
                self.tag_raise('floor','all')
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
        #check if selection was actually done by self.showArea and not just right click
        #so release event has to be different to click event (otherwise size = 0)
        if self.area[0:2] != [event.x, event.y]:
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
        #draw HQ, Trap and Grid, reset colors
        global used_colors, used_colors_default
        used_colors = used_colors_default
        #clear canvas before drawing
        self.delete('all')
        self.master.resetTrapCoord()
        self.buildings = []
        #but add the grid
        self.makeGrid(self.grid_size)

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
        width = self.winfo_width()*2
        height = self.winfo_height()*2
        # initialize grid line:
        grid_pos = grid_space/2
        # if grid_space is an even number, add a half grid point to match full gridpoint roster1
        grid_pos += (grid_space+1)%2*0.5
        pix_pos = grid_pos*multiplier
        while pix_pos < max(width, height):
            #horizontal (plus and minus of origin)
            self.create_line(-width,self.origin[1]+pix_pos,width,self.origin[1]+pix_pos,dash=(1,5),tag='grid')
            self.create_line(-width,self.origin[1]-pix_pos,width,self.origin[1]-pix_pos,dash=(1,5),tag='grid')
            #vertical
            self.create_line(self.origin[0]+pix_pos,-height,self.origin[0]+pix_pos,height,dash=(1,5),tag='grid')
            self.create_line(self.origin[0]-pix_pos,-height,self.origin[0]-pix_pos,height,dash=(1,5),tag='grid')
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

    def changeGridSize(self,new_grid_size = None ):
        #This is just a test function for now
        #TODO: implement grid size selection on MainWindow level!
        #use default if nothing is send
        if new_grid_size == None:
            new_grid_size = self.grid_size 
        if new_grid_size == 6:
            self.grid_size = 2 
        else:
            self.grid_size = 6
        #then remove old grid
        self.removeGrid()
        #and paint the new one
        self.makeGrid(grid_space=self.grid_size)


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
        member_name = member.name.get()
        
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
        self.assignments = { id : city for city, id in self.cities.items()}
        member.city_id = city
        member.canvas = self

        # provide coordinates if trap coordinates are activated
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
        #autoselect next unassigned member
        # remark: index produces an error when member does not exist in the list, but as it was just extracted from the list, it has to be there anyway
        cur_mem = ML.members.index(member)
        #check next member for assognment
        self.selectNextMember(ML,cur_mem)
  
    def selectNextMember(self,MList,cur_member,found_member = False):
        #select the next unassigned member in MemberList after cur_member     
        for next_member in MList.members[cur_member+1:]:
            if "assigned" not in next_member.status:
                next_member.changeState("new current")
                return True
        #no member found after cur_member? Just start again at the beginning
        if found_member is False:
            found_member = self.selectNextMember(MList,-1,True)
            #we have to return even if the complete list is already assigned
            #TODO: give warning that all members have been assigned if found_member is still False
            return True

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
            member.coord_widget.config(text='[ ---, --- ]')

    def findAssignee(self,id):
        #find the name of the member assigned to the id of the canvas object
        ret_val = list(set(self.gettags(id)).intersection(set(self.cities.keys())))
        #if only one member (which should always be the case) return string, not list
        if len(ret_val) == 0:
            return None
        elif len(ret_val) == 1:
            ret_val = ret_val[0] 
        return ret_val

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

