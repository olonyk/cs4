import tkinter as tk
from tkinter import ttk

class ScrollableFrame(ttk.Frame):
    """
    Consider me a regular frame with a vertical scrollbar 
    on the right, after adding/removing widgets to/from me 
    call my method update() to refresh the scrollable area. 
    Don't pack() me, nor place() nor grid(). 
    I work best when I am alone in the parent frame.
    """
    def __init__(self, parent, *args, **kw):

        # scrollbar on right in parent 
        yscrollbar = tk.Scrollbar(parent, width=32)
        yscrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)

        # canvas on left in parent
        self.canvas = tk.Canvas(parent, yscrollcommand=yscrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        def fill_canvas(event):
            "enlarge the windows item to the canvas width"
            canvas_width = event.width
            self.canvas.itemconfig(self.windows_item, width = canvas_width)

        self.canvas.bind("<Configure>", fill_canvas)

        yscrollbar.config(command=self.canvas.yview)    

        # create the scrollable frame and assign it to the windows item of the canvas
        ttk.Frame.__init__(self, parent, *args, **kw)
        self.windows_item = self.canvas.create_window(0,0, window=self, anchor=tk.NW)

    def update(self):
        """
        Update changes to the canvas before the program gets
        back the mainloop, then update the scrollregion
        """
        self.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(self.windows_item))


if __name__ == '__main__':
    root = tk.Tk()

    frame1 = ttk.Frame(root)
    frame1.pack(pady=10)

    frame2 = ttk.Frame(root)
    frame2.pack()

    frame3 = ttk.Frame(root)
    frame3.pack(pady=10)

    another_fr = ScrollableFrame(frame2)

    for i in range(30):
        ttk.Button(another_fr, text="I'm a button in the scrollable frame").grid()

    for i in range(10):
        ttk.Label(frame1, text="I'm a label in frame 1").grid()
    another_fr.update()

    for i in range(10):
        ttk.Label(frame3, text="I'm a label in frame 3").grid()

    root.mainloop()
