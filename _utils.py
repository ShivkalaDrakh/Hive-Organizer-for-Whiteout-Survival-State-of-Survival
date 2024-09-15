import tkinter as tk
from tkinter import ttk
import webbrowser

def callweb(url):
    webbrowser.open_new(url)

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
                scroll_values = list(map(lambda x: x + delta_scroll, vscrollbar.get()))
                
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