import tkinter as tk
from tkinter import ttk


class InvalidDimension(Exception):
    pass


class SettingsWindow:

    def __init__(self, swell_simulator):
        self.swell_sim = swell_simulator
        self.initial_dim = self.swell_sim.D.copy()
        self.root = tk.Tk()
        self.root.title("Settings")
        self.root.geometry('230x450')
        # self.root.iconbitmap('icon.ico')
        self.root.resizable(False, False)

        self.dimensions = [{"name": "l1"},
                           {"name": "l2"},
                           {"name": "l3"},
                           {"name": "l4"},
                           {"name": "l4'"},
                           {"name": "l5"},
                           {"name": "a"},
                           {"name": "b"},
                           {"name": "c"},
                           {"name": "b"}]

        for dimension in self.dimensions:
            ttk.Label(self.root, text=f"{dimension['name']} : ").grid()
            dimension["value"] = tk.StringVar(value=self.swell_sim.D[dimension["name"]])
            dim_entry = ttk.Entry(self.root, width=11, textvariable=dimension["value"])
            dim_entry.grid(column=1)
            dimension["label"] = ttk.Label(self.root)

        self.error_label = ttk.Label(self.root, text="Impossible shape !", foreground='red')

        action = ttk.Button(self.root, text="OK", command=self.update_dim)
        action.grid(row=len(self.dimensions*2),column=2)
        action = ttk.Button(self.root, text="Reset", command=self.reset)
        action.grid(row=len(self.dimensions*2), column=1)

    def update_dim(self):
        for index, dimension in enumerate(self.dimensions):
            try:
                dimension["label"].grid_remove()
                dim = float(dimension["value"].get())
                if dim < 0:
                    raise InvalidDimension
                self.swell_sim.D[dimension["name"]] = dim
                
            except ValueError:
                dimension["label"].configure(text="Give a real number")
                dimension["label"].configure(foreground='red')
                dimension["label"].grid(column=1, row=index*2)
            except InvalidDimension:
                dimension["label"].configure(text="Give a positive number")
                dimension["label"].configure(foreground='red')
                dimension["label"].grid(column=1, row=index*2)

    def reset(self):
        pass
        # self.swell_sim.D = self.initial_dim.copy()
        # for dimension in self.dimensions:
        #    dimension["value"] = self.swell_sim.D[dimension["name"]]
        #    dimension["value"] = tk.StringVar(value=dimension["value"])

    def math_er(self):
        self.error_label.grid(column=2)
