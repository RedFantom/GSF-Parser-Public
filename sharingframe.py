# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom and Daethyra
# For license see LICENSE

# UI imports
import ttk
import Tkinter as tk

class share_frame(ttk.Frame):
    def __init__(self, root_frame):
        ttk.Frame.__init__(self, root_frame)
        self.label = ttk.Label(self, font = ("Calibri", 40),
                               text = "Coming soon!", justify = tk.CENTER)
        self.label.grid(sticky = tk.N + tk.S + tk.W + tk.E, padx = 250, pady = 150)