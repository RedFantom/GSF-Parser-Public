"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""

# UI Libraries
import tkinter as tk
# Standard Library
from pynput import keyboard
import sys
# Project Modules
import variables
from utils import admin


factions = {
    "Imperial": "imp",
    "Republic": "rep"
}

railguns = {
    "Slug Railgun": {"imp": "03", "rep": "03"},
    "Ion Railgun": {"imp": "02", "rep": "01"},
    "Plasma Railgun": {"imp": "04", "rep": "04"}
}


class CartelFix(tk.Toplevel):
    """Tiny overlay to display secondary weapon icons for Cartel GS"""

    def __init__(self, master: tk.Tk, first: tk.PhotoImage, second: tk.PhotoImage, coordinates: tuple):
        """
        :param master: Master MainWindow
        :param first: PhotoImage of first SecondaryWeapon
        :param second: PhotoImage of second SecondaryWeapon
        :param coordinates: Coordinates to create overlay in
        """
        if not admin.check_privileges() and sys.platform == "win32":
                variables.main_window.destroy()
                admin.escalate_privileges()
                exit()
        tk.Toplevel.__init__(self, master)
        self.label = tk.Label(self)
        self.railgun = 1
        self.first = first
        self.second = second
        self.label.config(image=self.first, )
        self.label.grid()
        self.listener = keyboard.Listener(on_press=self.switch)
        self.coordinates = coordinates
        self.set_geometry()

    def switch(self, key: keyboard.Key):
        """
        Callback for the keyboard press Listener

        Only if the pressed key is `1` on the keyboard (either NumPad
        or numeric row) will the icon switch status.
        """
        try:
            if int(key.char) != 1:
                return True
        except AttributeError:
            return True
        except ValueError:
            return True
        if self.railgun == 1:
            self.label.config(image=self.second)
            self.railgun = 2
        elif self.railgun == 2:
            self.label.config(image=self.first)
            self.railgun = 1
        else:
            raise ValueError("Not a valid railgun number: {0}".format(self.railgun))
        return True

    def set_geometry(self):
        """Update window geometry and attributes"""
        self.configure(background="white")
        if sys.platform == "win32":
            self.wm_attributes("-transparentcolor", "white")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.wm_geometry("+{0}+{1}".format(self.coordinates[0], self.coordinates[1]))

    def start_listener(self):
        self.listener.start()

    @staticmethod
    def generate_icon_path(faction: str, railgun: str):
        """Generate the filename for specified railgun for faction"""
        base = "spvp.{}.gunship.sweapon.{}.jpg"
        return base.format(factions[faction], railguns[railgun][factions[faction]])
