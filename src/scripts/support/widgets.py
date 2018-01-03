import tkinter as tk
from tkinter import ttk

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
        yscrollbar = tk.Scrollbar(y_frame)
        yscrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)

        # scrollbar on bottom in parent 
        xscrollbar = tk.Scrollbar(x_frame, orient=tk.HORIZONTAL)
        xscrollbar.pack(side="top", fill=tk.X, expand=False, pady=10)

        # canvas on left in parent
        self.canvas = tk.Canvas(win_frame,
                                yscrollcommand=yscrollbar.set,
                                xscrollcommand=xscrollbar.set,
                                background="#ffffff")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        #self.canvas.pack(side=tk.LEFT)

        def fill_canvas(event):
            "enlarge the windows item to the canvas width"
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.canvas.bind("<Configure>", fill_canvas)

        yscrollbar.config(command=self.canvas.yview)
        xscrollbar.config(command=self.canvas.xview)

        # create the scrollable frame and assign it to the windows item of the canvas
        ttk.Frame.__init__(self, win_frame, *args, **kw)
        self.windows_item = self.canvas.create_window(0,0, window=self, anchor=tk.NW)

    def update(self):
        """
        Update changes to the canvas before the program gets
        back the mainloop, then update the scrollregion
        """
        self.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(self.windows_item))