from tkinter import (BOTH, GROOVE, HORIZONTAL, LEFT, NW, RIGHT, Button, Canvas,
                     Frame, Label, Scrollbar, StringVar, X, Y, ttk)
from tkinter.colorchooser import askcolor


class ScrollableFrame(ttk.Frame):
    """ Consider me a regular frame with a vertical scrollbar 
        on the right, after adding/removing widgets to/from me 
        call my method update() to refresh the scrollable area. 
        Don't pack() me, nor place() nor grid(). 
        I work best when I am alone in the parent frame.
        https://stackoverflow.com/questions/3085696/adding-a-scrollbar-to-a-group-of-widgets-in-tkinter/3092341#3092341
    """
    def __init__(self, win_frame, x_frame, y_frame, *args, **kw):
        # scrollbar on right in parent 
        yscrollbar = Scrollbar(y_frame)
        yscrollbar.pack(side=RIGHT, fill=Y, expand=False)

        # scrollbar on bottom in parent 
        xscrollbar = Scrollbar(x_frame, orient=HORIZONTAL)
        xscrollbar.pack(side="top", fill=X, expand=False, pady=10)

        # canvas on left in parent
        self.canvas = Canvas(win_frame,
                                yscrollcommand=yscrollbar.set,
                                xscrollcommand=xscrollbar.set,
                                background="#ffffff")
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        def fill_canvas(event):
            "enlarge the windows item to the canvas width"
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.canvas.bind("<Configure>", fill_canvas)

        yscrollbar.config(command=self.canvas.yview)
        xscrollbar.config(command=self.canvas.xview)

        # create the scrollable frame and assign it to the windows item of the canvas
        style = ttk.Style()
        style.configure("BW.TLabel", foreground="black", background="white")
        kw["style"] = "BW.TLabel"
        ttk.Frame.__init__(self, win_frame, *args, **kw)

        self.windows_item = self.canvas.create_window(0,0, window=self, anchor=NW)

    def update(self):
        """
        Update changes to the canvas before the program gets
        back the mainloop, then update the scrollregion
        """
        self.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(self.windows_item))

class ColorWidget(Frame):
    def __init__(self, master=None, text="", color=None):
        Frame.__init__(self, master)
        Label(self, text=text).pack(side=LEFT)
        self.color = color
        if not color:
            self.color = StringVar(master)
            self.color.set("#ff0000")
        self.color_lbl = Label(self, text="    ", background=self.color.get(), bd=1, relief=GROOVE)
        self.color_lbl.pack(side=LEFT)
        Button(self, text='Select Color', command=self.getColor).pack(side=LEFT)

    def getColor(self):
        color = askcolor()
        if color[1]:
            self.color.set(color[1])
            self.color_lbl.configure(background=self.color.get())
