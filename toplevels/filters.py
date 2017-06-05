# -*- coding: utf-8 -*-
#
# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
import tkinter as tk
import tkinter.ttk
import tkinter.messagebox
import os
import re
import widgets
import variables
import parsing.parse as parse
from datetime import datetime
from frames.statsframe import StatsFrame
from widgets.verticalscrollframe import VerticalScrollFrame
from . import splashscreens
from parsing import abilities as abls
from parsing.filestats import file_statistics


class Filters(tk.Toplevel):
    """
    A class for a Toplevel that shows all possible filters that can be applied to CombatLogs. Using expandable frames,
    the settings in a certain category can be shown or hidden. If all settings are set, the user can click OK and a
    special function is called passing a dictionary of files.
    """

    def __init__(self, window=None):
        tk.Toplevel.__init__(self, window)
        if window:
            self.window = window
        else:
            self.window = variables.main_window
        self.wm_resizable(False, False)
        self.description_label = tkinter.ttk.Label(self, text="Please enter the filters you want to apply",
                                                   font=("Calibri", 12))
        self.filter_types = ["Date", "Components", "Ships", "Statistics", "Duration"]
        self.filter_type_checkbuttons = []
        self.filter_type_vars = {}
        for type in self.filter_types:
            self.filter_type_vars[type] = tk.IntVar()
            self.filter_type_checkbuttons.append(
                tkinter.ttk.Checkbutton(self, text=type, variable=self.filter_type_vars[type]))
        print("[DEBUG] Setting up Type filters")
        self.type_frame = widgets.ToggledFrame(self, text="Type", labelwidth=100)
        self.type_variable = tk.StringVar()
        self.type_variable.set("logs")
        self.logs_radio = tkinter.ttk.Radiobutton(self.type_frame.sub_frame, text="CombatLogs",
                                                  variable=self.type_variable,
                                                  value="logs", width=20)
        self.matches_radio = tkinter.ttk.Radiobutton(self.type_frame.sub_frame, text="Matches",
                                                     variable=self.type_variable,
                                                     value="matches", width=20)
        self.spawns_radio = tkinter.ttk.Radiobutton(self.type_frame.sub_frame, text="Spawns",
                                                    variable=self.type_variable,
                                                    value="spawns", width=20)
        print("[DEBUG] Setting up date filters")
        self.dateframe = widgets.ToggledFrame(self, text="Date", labelwidth=100)
        self.start_date_widget = widgets.Calendar(self.dateframe.sub_frame)
        self.end_date_widget = widgets.Calendar(self.dateframe.sub_frame)
        print("[DEBUG] Setting up components filters")
        self.components_frame = widgets.ToggledFrame(self, text="Components", labelwidth=100)
        self.primaries_frame = widgets.ToggledFrame(self.components_frame.sub_frame, text="Primaries", labelwidth=100)
        self.secondaries_frame = widgets.ToggledFrame(self.components_frame.sub_frame, text="Secondaries",
                                                      labelwidth=100)
        self.engines_frame = widgets.ToggledFrame(self.components_frame.sub_frame, text="Engines", labelwidth=100)
        self.shields_frame = widgets.ToggledFrame(self.components_frame.sub_frame, text="Shields", labelwidth=100)
        self.systems_frame = widgets.ToggledFrame(self.components_frame.sub_frame, text="Sytems", labelwidth=100)
        self.primaries_tickboxes = {}
        self.primaries_tickboxes_vars = {}
        self.secondaries_tickboxes = {}
        self.secondaries_tickboxes_vars = {}
        self.engines_tickboxes = {}
        self.engines_tickboxes_vars = {}
        self.shields_tickboxes = {}
        self.shields_tickboxes_vars = {}
        self.systems_tickboxes = {}
        self.systems_tickboxes_vars = {}
        for primary in abls.primaries:
            primary_var = tk.IntVar()
            primary_chk = tkinter.ttk.Checkbutton(self.primaries_frame.sub_frame, text=primary, variable=primary_var,
                                                  width=20)
            self.primaries_tickboxes[primary] = primary_chk
            self.primaries_tickboxes_vars[primary] = primary_var
        for secondary in abls.secondaries:
            secondary_var = tk.IntVar()
            secondary_chk = tkinter.ttk.Checkbutton(self.secondaries_frame.sub_frame, text=secondary,
                                                    variable=secondary_var,
                                                    width=20)
            self.secondaries_tickboxes[secondary] = secondary_chk
            self.secondaries_tickboxes_vars[secondary] = secondary_var
        for engine in abls.engines:
            engine_var = tk.IntVar()
            engine_chk = tkinter.ttk.Checkbutton(self.engines_frame.sub_frame, text=engine, variable=engine_var,
                                                 width=20)
            self.engines_tickboxes[engine] = engine_chk
            self.engines_tickboxes_vars[engine] = engine_var
        for shield in abls.shields:
            shield_var = tk.IntVar()
            shield_chk = tkinter.ttk.Checkbutton(self.shields_frame.sub_frame, text=shield, variable=shield_var,
                                                 width=20)
            self.shields_tickboxes[shield] = shield_chk
            self.shields_tickboxes_vars[shield] = shield_var
        for system in abls.systems:
            system_var = tk.IntVar()
            system_chk = tkinter.ttk.Checkbutton(self.systems_frame.sub_frame, text=system, variable=system_var,
                                                 width=20)
            self.systems_tickboxes[system] = system_chk
            self.systems_tickboxes_vars[system] = system_var
        self.comps_dicts = [self.primaries_tickboxes, self.secondaries_tickboxes, self.engines_tickboxes,
                            self.shields_tickboxes, self.systems_tickboxes]

        self.ships_frame = widgets.ToggledFrame(self, text="Ships", labelwidth=100)
        self.ships_checkboxes = {}
        self.ships_intvars = {}
        if variables.settings_obj.faction == "imperial":
            for name in abls.rep_ships.keys():
                self.ships_intvars[name] = tk.IntVar()
                self.ships_checkboxes[name] = tkinter.ttk.Checkbutton(self.ships_frame.sub_frame, text=name,
                                                                      variable=self.ships_intvars[name], width=12)
        elif variables.settings_obj.faction == "republic":
            for name in abls.rep_ships.values():
                self.ships_intvars[name] = tk.IntVar()
                self.ships_checkboxes[name] = tkinter.ttk.Checkbutton(self.ships_frame.sub_frame, text=name,
                                                                      variable=self.ships_intvars[name], width=12)
        else:
            raise ValueError("No valid faction found.")

        self.complete_button = tkinter.ttk.Button(self, text="Filter", command=self.filter)
        self.cancel_button = tkinter.ttk.Button(self, text="Cancel", command=self.destroy)
        self.search_button = tkinter.ttk.Button(self, text="Search", command=self.search)
        print("[DEBUG] Gridding widgets")
        self.grid_widgets()

    def search_files(self):
        """
        Take the inserted filters and calculate how many files/matches/spawns are found when the filters are applied.
        Display a tkMessageBox.showinfo() box to show the user how many are found and show a splash screen while
        searching.
        :return:
        """
        pass

    def search(self):
        self.filter(search=True)

    def filter(self, search=False):
        # logs, matches or spawns
        results = []
        results_toplevel = Results(self.window)
        if self.type_variable.get() == "logs":
            files = os.listdir(variables.settings_obj.cl_path)
            variables.files_done = 0
            splash = splashscreens.SplashScreen(self, max=len(files))
            for file_name in files:
                passed = True
                variables.files_done += 1
                splash.update_progress()
                if not file_name.endswith(".txt"):
                    continue
                with open(os.path.join(variables.settings_obj.cl_path, file_name)) as f:
                    lines = f.readlines()
                player_list = parse.determinePlayer(lines)
                file_cube, match_timings, spawn_timings = parse.splitter(lines, player_list)
                (abilities, damagetaken, damagedealt,
                 selfdamage, healingreceived, enemies,
                 criticalcount, criticalluck, hitcount,
                 enemydamaged, enemydamaget, match_timings,
                 spawn_timings) = parse.parse_file(file_cube, player_list, match_timings, spawn_timings)
                damagetaken = self.file_number(damagetaken)
                damagedealt = self.file_number(damagedealt)
                selfdamage = self.file_number(selfdamage)
                healingreceived = self.file_number(healingreceived)
                if self.filter_type_vars["Ships"].get() == 1:
                    tkinter.messagebox.showerror("Error", "Ships filters have not yet been implemented.")
                    return
                    print("Checking ships")
                    if not self.check_ships_file(self.ships_intvars, abilities):
                        continue
                abilities = self.file_dictionary(abilities)
                if self.filter_type_vars["Components"].get() == 1:
                    for dictionary in self.comps_dicts:
                        if not self.check_components(dictionary, abilities):
                            passed = False
                            break
                if not passed:
                    continue
                frame = StatsFrame(results_toplevel.frame.interior, variables.main_window)
                self.setup_frame_file(frame, file_name)
                results.append((tkinter.ttk.Label(results_toplevel.frame.interior, text=self.parse_file_name(file_name),
                                                  font=("Calibiri", 12)),
                                frame))
                print(len(files))
            splash.destroy()
        elif self.type_variable.get() == "matches":
            pass
        elif self.type_variable.get() == "spawns":
            pass
        else:
            raise ValueError("type_variable.get() did not return a valid value")
        if search:
            tkinter.messagebox.showinfo("Search results", "With the filters you specified, %s results were found." %
                                        len(results))
            results_toplevel.destroy()
        else:
            if len(results) == 0:
                tkinter.messagebox.showinfo("Search results", "With the filters you specified, no results were found.")
                return
            results_toplevel.grid_widgets(results)
            self.destroy()

    def grid_widgets(self):
        self.description_label.grid(row=0, column=1, columnspan=len(self.filter_types),
                                    sticky="nswe")
        set_column = 1
        for widget in self.filter_type_checkbuttons:
            widget.grid(row=1, column=set_column, sticky="w")
            set_column += 1
        self.type_frame.grid(row=2, column=1, columnspan=len(self.filter_types), sticky="nswe")
        self.dateframe.grid(row=3, column=1, columnspan=len(self.filter_types), sticky="nswe")
        self.components_frame.grid(row=4, column=1, columnspan=len(self.filter_types), sticky="nswe")
        self.ships_frame.grid(row=5, column=1, columnspan=len(self.filter_types), sticky="nswe")
        self.complete_button.grid(row=6, column=1, sticky="nswe")
        self.search_button.grid(row=6, column=2, sticky="nswe")
        self.cancel_button.grid(row=6, column=3, sticky="nswe")

        self.logs_radio.grid(row=1, column=2, sticky="nswe")
        self.matches_radio.grid(row=1, column=3, sticky="nswe")
        self.spawns_radio.grid(row=1, column=4, sticky="nswe")

        self.start_date_widget.grid(row=1, column=1, sticky="nswe")
        self.end_date_widget.grid(row=1, column=2, sticky="nswe")

        self.primaries_frame.grid(row=0, column=0, sticky="nswe")
        self.secondaries_frame.grid(row=1, column=0, sticky="nswe")
        self.engines_frame.grid(row=2, column=0, sticky="nswe")
        self.shields_frame.grid(row=3, column=0, sticky="nswe")
        self.systems_frame.grid(row=4, column=0, sticky="nswe")

        start_row = 1
        start_column = 1
        for dictionary in self.comps_dicts:
            for widget in dictionary.values():
                widget.grid(row=start_row, column=start_column, sticky="w" + tk.N)
                start_column += 1
                if start_column == 5:
                    start_column = 1
                    start_row += 1
            start_row = 1
            start_column = 1
            start_row += 1

        set_row = 1
        set_column = 1
        for widget in self.ships_checkboxes.values():
            widget.grid(row=set_row, column=set_column, sticky="nw")
            set_column += 1
            if set_column == 7:
                set_column = 1
                set_row += 1
        return

    @staticmethod
    def setup_frame_file(frame, file_name):
        with open(os.path.join(variables.settings_obj.cl_path, file_name)) as f:
            lines = f.readlines()
        player_list = parse.determinePlayer(lines)
        file_cube, _, _ = parse.splitter(lines, player_list)
        (abilities_dict, statistics_string, shipsdict, enemies, enemydamaged,
         enemydamaget, uncounted) = file_statistics(file_cube)
        frame.statistics_numbers_var.set(statistics_string)
        for key, value in abilities_dict.items():
            frame.abilities_treeview.insert('', tk.END, values=(key, value))
        frame.events_button.grid_forget()
        for enemy in enemies:
            if enemy == "":
                frame.enemies_treeview.insert('', tk.END,
                                              values=("System",
                                                      str(enemydamaged[enemy]),
                                                      str(enemydamaget[enemy])))
            elif re.search('[a-zA-Z]', enemy):
                frame.enemies_treeview.insert('', tk.END,
                                              values=(enemy,
                                                      str(enemydamaged[enemy]),
                                                      str(enemydamaget[enemy])))
            else:
                frame.enemies_treeview.insert('', tk.END,
                                              values=(enemy,
                                                      str(enemydamaged[enemy]),
                                                      str(enemydamaget[enemy])))

    @staticmethod
    def file_dictionary(abilities):
        return_value = {}
        for abl_list in abilities:
            for abl in abl_list:
                return_value.update(abl)
        return return_value

    @staticmethod
    def file_number(matrix):
        return_value = 0
        for list in matrix:
            return_value += sum(list)
        return return_value

    @staticmethod
    def check_components(dictionary, abilities):
        for component, intvar in dictionary.items():
            if component not in abilities:
                return False
        return True

    @staticmethod
    def check_ships_file(dictionary, abilities):
        for list in abilities:
            for dict in list:
                ships_list = parse.determineShip(dict)
                print(ships_list)
                passed = True
                for ship, intvar in dictionary.items():
                    if intvar.get() == 1:
                        print("Required: ", ship)
                        if variables.settings_obj.faction == "imperial":
                            pass
                        elif variables.settings_obj.faction == "republic":
                            ships_list = [abls.rep_ships[name] for name in ships_list]
                        else:
                            raise ValueError("faction found not valid")
                        if ship not in ships_list:
                            passed = False
                if not passed:
                    return False
        print("Returning True")
        return True

    @staticmethod
    def parse_file_name(name):
        try:
            if variables.settings_obj.date_format == "ymd":
                return datetime.strptime(name[:-10], "combat_%Y-%m-%d_%H_%M_%S_").strftime("%Y-%m-%d   %H:%M")
            elif variables.settings_obj.date_format == "ydm":
                return datetime.strptime(name[:-10], "combat_%Y-%m-%d_%H_%M_%S_").strftime(
                    "%Y-%d-%m   %H:%M:%S")
            else:
                tkinter.messagebox.showerror("No valid date format setting found.")
                return -1
        except ValueError:
            return name


class Results(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.frame = VerticalScrollFrame(self, canvaswidth=650, canvasheight=395)
        self.wm_resizable(False, False)
        self.wm_title("GSF Parser: Search Results")
        self.iconify()

    def grid_widgets(self, results_list):
        self.frame.grid()
        self.deiconify()
        set_row = 0
        set_column = 0
        for (title, item) in results_list:
            item.grid_widgets()
            item.notice_label.grid_forget()
            item.notebook.config(height=200, width=310)
            item.config(width=310)
            item.events_frame.grid_forget()
            item.enemies_treeview.config(height=8)
            item.abilities_treeview.config(height=8)
            title.grid(row=set_row, column=set_column)
            item.grid(row=set_row + 1, column=set_column)
            set_column += 1
            if set_column == 2:
                set_column = 0
                set_row += 2
            print("Gridded a widget with title: ", title["text"])
        print("Gridded the results")
        return
