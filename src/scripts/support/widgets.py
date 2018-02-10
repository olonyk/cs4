from tkinter import (BOTH, GROOVE, HORIZONTAL, LEFT, NW, RIGHT, Button, Canvas,
                     Frame, Label, Scrollbar, StringVar, X, Y, ttk, Tk, Text, END)
from tkinter.colorchooser import askcolor
from os.path import dirname, isfile, join
import os
import sys

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

class ViewLog(object):
    def __init__(self):
        root = Tk()
        ViewLogGUI(root)
        root.mainloop()

class ViewLogGUI(Frame):
    def __init__(self, master):
        self.master = master
        master.title("Log file")
        content_frame = Frame(master, width=400, height=200)
        content_frame.pack(fill=BOTH)
        master.resizable(width=False, height=False)

        log_text = self.get_log_file()

        text_area = Text(content_frame, height=20, width=30)
        text_area.pack()
        text_area.insert(END, log_text)

        close_button = Button(content_frame, text="Close", command=master.quit)
        close_button.pack()
    
    def get_log_file(self):
        if getattr(sys, 'frozen', False):
            # We are running in a bundle, figure out the bundle dir.
            bundle_dir = sys._MEIPASS
            # Find stdout and stderr file.
            stdout_file = join(bundle_dir, "src", "resources", "settings", "stdout.txt")
            # Temporary put stdout back
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
        else:
            # We are running in a normal Python environment.
            # Find the settings file.
            stdout_file = join(dirname(dirname(dirname(dirname(__file__)))), "src", "resources",
                               "settings",
                               "stdout.txt")
        # Read settings file
        with open(stdout_file) as open_file:
            content = open_file.readlines()
        
        # Redirect stdout back to logfile
        if getattr(sys, 'frozen', False):
            sys.stdout = open(stdout_file, 'w')
            sys.stderr = open(stdout_file, 'w')
        return "".join(content)