import tkinter as tk
from tkinter import ttk
import webbrowser

def callweb(url):
    webbrowser.open_new(url)

def find(f, seq):
  #Return first item in sequence where f(item) == True.
  #Call example: find(lambda person: person.name == 'me', persons)
  for item in seq:
    if f(item): 
      return item
    
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

class VerticalScrolledFrame(ttk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame.
    * Construct and pack/place/grid normally.
    * This frame only allows vertical scrolling.
    """
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        # Reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=tk.NW)

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the canvas's width to fit the inner frame.
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

        def _on_mousewheel(event):
            #exclude the scrollbar not to double the scrolling
            if event.widget is not vscrollbar:

                #reduce the amount of scrolling by a factor of:
                slow_mo = 20
                delta_scroll = vscrollbar.delta(0,event.delta)/slow_mo
                scroll_values = list(map(lambda x: x - delta_scroll, vscrollbar.get()))
                
                #check orrect behaviour between 0 and 1
                if scroll_values[0] < 0: #scroll outside of upper bound
                    delta_scroll += scroll_values[0]
                    scroll_values[1] = scroll_values[1] - scroll_values[0]
                    scroll_values[0] = 0.0
                    #jump view to top
                    canvas.yview_moveto(0.0)
                    
                elif scroll_values[1] > 1: #scroll outside of lower bound
                    delta_scroll -= scroll_values[1] - 1
                    scroll_values[0] =  scroll_values[0] - scroll_values[1] + 1
                    scroll_values[1] = 1.0
                    #jump view to bottom
                    canvas.yview_moveto(1.0)
                else:                    
                    #always scroll 2 units = 1 row
                    #scroll to the fraction of the scroll
                    canvas.yview_moveto(scroll_values[0])

                vscrollbar.set(scroll_values[0],scroll_values[1])
        canvas.bind_all('<MouseWheel>', _on_mousewheel)
# End of VerticalScrolledFrame

class VerticalScrolledText(ttk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame.
    * Construct and pack/place/grid normally.
    * This frame only allows vertical scrolling.
    """
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)

        # Create a textbox object and a vertical scrollbar for scrolling it.
        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        self.textbox = textbox = tk.Text(self, bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set)
        textbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=textbox.yview)

        # Reset the view
        textbox.xview_moveto(0)
        textbox.yview_moveto(0)

        def _on_mousewheel(event):
            #exclude the scrollbar not to double the scrolling
            if event.widget is not vscrollbar:
                #amount of pixel per wheel movement
                #ppw = abs(event.delta)
                #reduce the amount of scrolling by a factor of:
                slow_mo = 20
                delta_scroll = vscrollbar.delta(0,event.delta)/slow_mo
                scroll_values = list(map(lambda x: x - delta_scroll, vscrollbar.get()))
                
                #check orrect behaviour between 0 and 1
                if scroll_values[0] < 0: #scroll outside of upper bound
                    delta_scroll += scroll_values[0]
                    scroll_values[1] = scroll_values[1] - scroll_values[0]
                    scroll_values[0] = 0.0
                    #jump view to top
                    textbox.yview_moveto(0.0)
                    
                elif scroll_values[1] > 1: #scroll outside of lower bound
                    delta_scroll -= scroll_values[1] - 1
                    scroll_values[0] =  scroll_values[0] - scroll_values[1] + 1
                    scroll_values[1] = 1.0
                    #jump view to bottom
                    textbox.yview_moveto(1.0)
                else:                    
                    #scroll to the fraction of the scroll
                    textbox.yview_moveto(scroll_values[0])
                vscrollbar.set(scroll_values[0],scroll_values[1])

        textbox.bind_all('<MouseWheel>', _on_mousewheel)
# End of VerticalScrolledFrame