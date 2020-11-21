import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image


class InvalidDimension(Exception):
    pass


class SettingsWindow:

    def __init__(self, swell_simulator):
        self.swell_sim = swell_simulator
        self.initial_dim = self.swell_sim.D.copy()
        self.root = tk.Tk()
        self.root.title("Settings")
        self.root.geometry('450x450')
        # self.root.iconbitmap('icon.ico')
        self.root.resizable(True, True)

        self.dimensions = [{"name": "l1"},
                           {"name": "l2"},
                           {"name": "l3"},
                           {"name": "l4"},
                           {"name": "l4'"},
                           {"name": "l5"},
                           {"name": "a"},
                           {"name": "b"},
                           {"name": "c"},
                           {"name": "d"}]

        for index, dimension in enumerate(self.dimensions):
            ttk.Label(self.root, text=f"{dimension['name'].upper()} : ").grid()
            dimension["value"] = tk.StringVar(value=self.swell_sim.D[dimension["name"]])
            dimension["dim_entry"] = ttk.Entry(self.root, width=11, textvariable=dimension["value"])
            dimension["dim_entry"].grid(row=index*2+1, column=1)
            dimension["label"] = ttk.Label(self.root)

        self.error_label = ttk.Label(self.root, text="Impossible shape !", foreground='red')

        action_ok = ttk.Button(self.root, text="OK", command=self.update_dim)
        action_ok.grid(row=len(self.dimensions*2), column=2)

        action_rst = ttk.Button(self.root, text="Reset", command=self.reset)
        action_rst.grid(row=len(self.dimensions*2), column=1)

        self.root.bind("<Return>", self.update_dim)
        self.root.bind("<Escape>", self.close)
        self.root.bind("<Control-r>", self.reset)

        image = Image.open("sketch.png")
        image = image.resize((281, 380), Image.ANTIALIAS) # image original size 1209x1619
        render = ImageTk.PhotoImage(image)
        img_label = ttk.Label(self.root, image=render)
        img_label.image = render
        img_label.place(x=153, y=15)

    def update_dim(self, event=None):
        for index, dimension in enumerate(self.dimensions):
            try:
                dimension["label"].grid_remove()
                dim = float(dimension["value"].get())
                if dim < 0 and not dimension["name"] in ["a", "b", "c", "d"]:
                    raise InvalidDimension
                self.swell_sim.D[dimension["name"]] = dim
                
            except ValueError:
                dimension["label"].configure(text="Give a real number", foreground='red')
                dimension["label"].grid(column=1, row=index*2)
            except InvalidDimension:
                dimension["label"].configure(text="Give a positive number", foreground='red')
                dimension["label"].grid(column=1, row=index*2)

    def reset(self, event=None):
        self.swell_sim.D = self.initial_dim.copy()
        for index, dimension in enumerate(self.dimensions):
            dimension["value"] = tk.StringVar(value=self.swell_sim.D[dimension["name"]])
            dimension["dim_entry"] = ttk.Entry(self.root, width=11, textvariable=dimension["value"])
            dimension["dim_entry"].grid(row=index * 2 + 1, column=1)
            dimension["label"].grid_remove()

    def math_er(self):
        self.error_label.grid(column=2)

    def close(self, event=None):
        self.root.destroy()
