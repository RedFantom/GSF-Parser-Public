# -*- coding: utf-8 -*-

"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""

# UI Imports
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog
import tkinter.colorchooser
# General imports
import collections
import os
# Own modules
from tools import utilities
import variables


class EventColors(tk.Toplevel):
    """
    A class for a Toplevel that lets the user set their own custom HTML colors for events.
    List of colors that need to be set:
    Damage dealt primaries
    Damage taken primaries
    Damage dealt secondaries
    Damage taken secondaries
    Selfdamage
    Healing
    Selfhealing
    Engine ability
    Shield ability
    System ability
    Other abilities
    """

    def __init__(self, window):
        tk.Toplevel.__init__(self, window)
        self.title("GSF Parser: Choose event colors")
        self.resizable(False, False)
        self.column_label_one = ttk.Label(self, text="Type of event", font=("Calibri", 12))
        self.column_label_two = ttk.Label(self, text="Background color", font=("Calibri", 12))
        self.column_label_three = ttk.Label(self, text="Text color", font=("Calibri", 12))
        self.colors = collections.OrderedDict()
        variables.colors.set_scheme(variables.settings["gui"]["event_scheme"])
        self.color_descriptions = collections.OrderedDict()
        self.color_descriptions["dmgd_pri"] = "Damage dealt by Primary Weapons: "
        self.color_descriptions["dmgt_pri"] = "Damage taken from Primary Weapons: "
        self.color_descriptions["dmgd_sec"] = "Damage dealt by Secondary Weapons: "
        self.color_descriptions["dmgt_sec"] = "Damage taken from Secondary Weapons: "
        self.color_descriptions["selfdmg"] = "Selfdamage: "
        self.color_descriptions["healing"] = "Healing received from others: "
        self.color_descriptions["selfheal"] = "Healing received from yourself: "
        self.color_descriptions["engine"] = "Activation of engine abilities: "
        self.color_descriptions["shield"] = "Activation of shield abilities: "
        self.color_descriptions["system"] = "Activation of system abilities: "
        self.color_descriptions["other"] = "Activation of other abilities: "
        self.color_descriptions["spawn"] = "End of a spawn: "
        self.color_descriptions["match"] = "End of a match: "
        self.color_descriptions["default"] = "Unmatched categories: "
        for color in self.color_descriptions.keys():
            self.colors[color] = [variables.colors[color][0], variables.colors[color][1]]
        self.color_labels = {}
        self.color_entry_vars_bg = {}
        self.color_entry_vars_fg = {}
        self.color_entry_widgets_bg = {}
        self.color_entry_widgets_fg = {}
        self.color_button_widgets_fg = {}
        self.color_button_widgets_bg = {}
        for key in self.colors.keys():
            self.color_labels[key] = ttk.Label(self, text=self.color_descriptions[key], justify=tk.LEFT)
            self.color_button_widgets_fg[key] = ttk.Button(self, text="Choose",
                                                           command=lambda color=key: self.set_color(color, fg=True))
            self.color_button_widgets_bg[key] = ttk.Button(self, text="Choose",
                                                           command=lambda color=key: self.set_color(color))
            self.color_entry_widgets_fg[key] = tk.Entry(self, font=("Consolas", 10), width=10)
            self.color_entry_widgets_bg[key] = tk.Entry(self, font=("Consolas", 10), width=10)
        self.separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.ok_button = ttk.Button(self, text="OK", width=10, command=self.ok_button_cb)
        self.cancel_button = ttk.Button(self, text="Cancel", width=10, command=self.cancel_button_cb)
        self.import_button = ttk.Button(self, text="Import", width=10, command=self.import_button_cb)
        self.export_button = ttk.Button(self, text="Export", width=10, command=self.export_button_cb)
        for key in self.color_descriptions.keys():
            self.color_entry_widgets_bg[key].delete(0, tk.END)
            self.color_entry_widgets_fg[key].delete(0, tk.END)
            self.color_entry_widgets_bg[key].insert(0, self.colors[key][0])
            self.color_entry_widgets_fg[key].insert(0, self.colors[key][1])
            color_tuple = tuple(int(self.colors[key][0].replace("#", "")[i:i + 2], 16) for i in (0, 2, 4))
            red = int(color_tuple[0])
            green = int(color_tuple[1])
            blue = int(color_tuple[2])
            foreground_color = '#000000' if (red * 0.299 + green * 0.587 + blue * 0.114) > 186 else "#ffffff"
            self.color_entry_widgets_bg[key].config(foreground=foreground_color, background=self.colors[key][0])
            color_tuple = tuple(int(self.colors[key][1].replace("#", "")[i:i + 2], 16) for i in (0, 2, 4))
            red = int(color_tuple[0])
            green = int(color_tuple[1])
            blue = int(color_tuple[2])
            foreground_color = '#000000' if (red * 0.299 + green * 0.587 + blue * 0.114) > 186 else "#ffffff"
            self.color_entry_widgets_fg[key].config(foreground=foreground_color, background=self.colors[key][1])

    def import_button_cb(self):
        file_to_open = tkinter.filedialog.askopenfile(filetypes=[("Settings file", ".ini")],
                                                      initialdir=os.path.join(utilities.get_temp_directory(),
                                                                              "event_colors.ini"),
                                                      parent=self, title="GSF Parser: Import colors from file")
        if not file_to_open:
            self.focus_set()
            return
        variables.colors.set_scheme("custom", custom_file=file_to_open)
        for color in self.color_descriptions.keys():
            self.colors[color] = [variables.colors[color][0], variables.colors[color][1]]
        for key in self.color_entry_vars_bg.keys():
            self.color_entry_widgets_bg[key].delete(0, tk.END)
            self.color_entry_widgets_fg[key].delete(0, tk.END)
            self.color_entry_widgets_bg[key].insert(self.colors[key][0])
            self.color_entry_widgets_fg[key].insert(self.colors[key][1])
        self.focus_set()

    def export_button_cb(self):
        file_to_save = tkinter.filedialog.asksaveasfilename(defaultextension=".ini",
                                                            filetypes=[("Settings file", ".ini")],
                                                            initialdir=os.path.join(utilities.get_temp_directory(),
                                                                                    "event_colors.ini"),
                                                            parent=self, title="GSF Parser: Export colors to file")
        if not file_to_save:
            self.focus_set()
            return
        for color, variable in self.color_entry_vars_bg.items():
            self.colors[color][0] = variable.get()
        for color, variable in self.color_entry_vars_fg.items():
            self.colors[color][1] = variable.get()
        for color, lst in self.colors.items():
            variables.colors[color] = lst
        variables.colors.write_custom(custom_file=file_to_save)
        self.focus_set()

    def set_color(self, key, fg=False):
        if not fg:
            color_tuple = tkinter.colorchooser.askcolor(color=self.color_entry_widgets_bg[key].get(),
                                                        title="GSF Parser: Choose color for %s" %
                                                              self.color_descriptions[
                                                                  key])
            try:
                red = int(color_tuple[0][0])
                green = int(color_tuple[0][1])
                blue = int(color_tuple[0][2])
            except TypeError:
                self.focus_set()
                return
            foreground_color = '#000000' if (red * 0.299 + green * 0.587 + blue * 0.114) > 186 else "#ffffff"
            self.color_entry_widgets_bg[key].delete(0, tk.END)
            self.color_entry_widgets_bg[key].insert(0, color_tuple[1])
            self.color_entry_widgets_bg[key].config(background=color_tuple[1],
                                                    foreground=foreground_color)
        else:
            color_tuple = tkinter.colorchooser.askcolor(color=self.color_entry_widgets_fg[key].get(),
                                                        title="GSF Parser: Choose color for %s" %
                                                              self.color_descriptions[
                                                                  key])
            try:
                red = int(color_tuple[0][0])
                green = int(color_tuple[0][1])
                blue = int(color_tuple[0][2])
            except TypeError:
                self.focus_set()
                return
            foreground_color = '#000000' if (red * 0.299 + green * 0.587 + blue * 0.114) > 186 else "#ffffff"
            self.color_entry_widgets_fg[key].delete(0, tk.END)
            self.color_entry_widgets_fg[key].insert(0, color_tuple[1])
            self.color_entry_widgets_fg[key].config(background=color_tuple[1],
                                                    foreground=foreground_color)
        self.focus_set()

    def ok_button_cb(self):
        for color, widget in self.color_entry_widgets_bg.items():
            self.colors[color][0] = widget.get()
        for color, widget in self.color_entry_widgets_fg.items():
            self.colors[color][1] = widget.get()
        for color, lst in self.colors.items():
            variables.colors[color] = lst
        variables.colors.write_custom()
        self.destroy()

    def cancel_button_cb(self):
        self.destroy()

    def grid_widgets(self):
        self.column_label_one.grid(column=0, columnspan=2, row=0, sticky="w")
        self.column_label_two.grid(column=2, columnspan=2, row=0, sticky="w")
        self.column_label_three.grid(column=4, columnspan=2, row=0, sticky="w")
        set_row = 1
        for key in self.colors.keys():
            self.color_labels[key].grid(column=0, columnspan=2, row=set_row, sticky="w")
            self.color_entry_widgets_bg[key].grid(column=2, row=set_row, sticky="w", padx=5)
            self.color_button_widgets_bg[key].grid(column=3, row=set_row, sticky="w")
            self.color_entry_widgets_fg[key].grid(column=4, row=set_row, sticky="w", padx=5)
            self.color_button_widgets_fg[key].grid(column=5, row=set_row, sticky="w")
            set_row += 1
        self.separator.grid(column=0, columnspan=6, sticky="nswe", pady=5)
        set_row += 1
        self.cancel_button.grid(column=3, columnspan=2, row=set_row, sticky="ns" + tk.E)
        self.ok_button.grid(column=5, row=set_row, sticky="nswe")
        self.import_button.grid(column=0, row=set_row, sticky="nswe")
        self.export_button.grid(column=1, row=set_row, sticky="nswe")
