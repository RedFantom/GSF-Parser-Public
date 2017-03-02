# -*- coding: utf-8 -*-

# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
try:
    import mtTkinter as tk
except ImportError:
    import Tkinter as tk
import ttk
import tkMessageBox
import tkFileDialog
import operator
import os
import re
from datetime import datetime

from PIL import Image, ImageTk

import variables
from parsing import statistics, parse, abilities
import toplevels
import widgets


# Class for the _frame in the fileTab of the parser
class file_frame(ttk.Frame):
    """
    Class for a frame that contains three listboxes, one for files, one for matches and
    one for spawns, and updates them and other widgets after parsing the files using the
    methods found in the parse.py module accordingly. This frame controls the whole of file
    parsing, the other frames only display the results.
    --------------------
    | combatlog_1 | /\ |
    | combatlog_2 | || |
    | combatlog_3 | \/ |
    --------------------
    | match_1     | /\ |
    | match_2     | || |
    | match_3     | \/ |
    --------------------
    | spawn_1     | /\ |
    | spawn_2     | || |
    | spawn_3     | \/ |
    --------------------
    """

    # __init__ creates all widgets
    def __init__(self, root_frame, main_window):
        """
        Create all widgets and make the links between them
        :param root_frame:
        :param main_window:
        """
        ttk.Frame.__init__(self, root_frame, width=200, height=420)
        self.main_window = main_window
        self.file_box = tk.Listbox(self)
        self.file_box_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.file_box_scroll.config(command=self.file_box.yview)
        self.file_box.config(yscrollcommand=self.file_box_scroll.set)
        self.match_box = tk.Listbox(self)
        self.match_box_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.match_box_scroll.config(command=self.match_box.yview)
        self.match_box.config(yscrollcommand=self.match_box_scroll.set)
        self.spawn_box = tk.Listbox(self)
        self.spawn_box_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.spawn_box.yview)
        self.spawn_box.config(yscrollcommand=self.spawn_box_scroll.set)

        self.file_box.bind("<Double-Button-1>", self.file_update)
        self.match_box.bind("<Double-Button-1>", self.match_update)
        self.spawn_box.bind("<Double-Button-1>", self.spawn_update)
        self.file_box.bind("<Return>", self.file_update)
        self.match_box.bind("<Return>", self.match_update)
        self.spawn_box.bind("<Return>", self.spawn_update)

        self.file_box.bind("<Enter>", self.bind_file)
        self.file_box.bind("<Leave>", self.unbind_file)
        self.match_box.bind("<Enter>", self.bind_match)
        self.match_box.bind("<Leave>", self.unbind_match)
        self.spawn_box.bind("<Enter>", self.bind_spawn)
        self.spawn_box.bind("<Leave>", self.unbind_spawn)

        self.statistics_object = statistics.statistics()
        self.refresh_button = ttk.Button(self, text="Refresh", command=self.add_files_cb)
        self.filters_button = ttk.Button(self, text="Filters", command=self.filters)
        self.old_file = 0
        self.old_match = 0
        self.old_spawn = 0

    def scroll_file(self, event):
        self.file_box.yview_scroll(-1 * (event.delta / 100), "units")

    def bind_file(self, event):
        self.main_window.bind("<MouseWheel>", self.scroll_file)
        self.file_box.focus()

    def unbind_file(self, event):
        self.main_window.unbind("<MouseWheel>")

    def scroll_match(self, event):
        self.match_box.yview_scroll(-1 * (event.delta / 100), "units")

    def bind_match(self, event):
        self.main_window.bind("<MouseWheel>", self.scroll_match)
        self.match_box.focus()

    def unbind_match(self, event):
        self.main_window.unbind("<MouseWheel>")

    def scroll_spawn(self, event):
        self.spawn_box.yview_scroll(-1 * (event.delta / 100), "units")

    def bind_spawn(self, event):
        self.main_window.bind("<MouseWheel>", self.scroll_spawn)
        self.spawn_box.focus()

    def unbind_spawn(self, event):
        self.main_window.unbind("<MouseWheel>")

    def filters(self):
        """
        Opens Toplevel to enable filters and then adds the filtered CombatLogs to the Listboxes
        """
        tkMessageBox.showinfo("Notice", "This button is not yet functional.")

    def grid_widgets(self):
        """
        Put all widgets in the right places
        :return:
        """

        self.file_box.config(height=6)
        self.match_box.config(height=6)
        self.spawn_box.config(height=6)
        self.file_box.grid(column=0, row=0, columnspan=2, padx=5, pady=5)
        self.file_box_scroll.grid(column=2, row=0, rowspan=8, columnspan=1, sticky=tk.N + tk.S, pady=5)
        self.match_box.grid(column=0, row=8, columnspan=2, padx=5, pady=5)
        self.match_box_scroll.grid(column=2, row=8, columnspan=1, sticky=tk.N + tk.S, pady=5)
        self.spawn_box.grid(column=0, row=16, columnspan=2, padx=5, pady=5)
        self.spawn_box_scroll.grid(column=2, row=16, columnspan=1, sticky=tk.N + tk.S, pady=5)
        self.refresh_button.grid(column=0, columnspan=3, row=17, rowspan=1, sticky=tk.N + tk.S + tk.E + tk.W)
        self.filters_button.grid(column=0, columnspan=3, row=18, rowspan=1, sticky=tk.N + tk.S + tk.E + tk.W)

    def add_matches(self):
        """
        Function that adds the matches found in the file selected to the appropriate listbox
        :return:
        """

        self.spawn_box.delete(0, tk.END)
        self.main_window.middle_frame.enemies_treeview.delete(
            *self.main_window.middle_frame.enemies_treeview.get_children())
        self.main_window.ship_frame.ship_label_var.set("")
        with open(variables.settings_obj.cl_path + "/" + variables.file_name, "r") as file:
            variables.player_name = parse.determinePlayerName(file.readlines())
        self.spawn_box.delete(0, tk.END)
        self.match_timing_strings = []
        self.match_timing_strings = [str(time.time()) for time in variables.match_timings]
        self.match_timing_strings = self.match_timing_strings[::2]
        """
        for number in range(0, len(self.match_timing_strings) + 1):
            self.match_box.delete(number)
        """
        self.match_box.delete(0, tk.END)
        self.match_box.insert(tk.END, "All matches")
        if len(self.match_timing_strings) == 0:
            self.match_box.delete(0, tk.END)
            self.add_spawns()
        else:
            for time in self.match_timing_strings:
                self.match_box.insert(tk.END, time)

    def add_spawns(self):
        """
        Function that adds the spawns found in the selected match to the appropriate listbox
        :return:
        """

        self.main_window.middle_frame.abilities_treeview.delete(
            *self.main_window.middle_frame.abilities_treeview.get_children(""))
        self.main_window.middle_frame.enemies_treeview.delete(
            *self.main_window.middle_frame.enemies_treeview.get_children())
        self.main_window.ship_frame.ship_label_var.set("")
        self.spawn_timing_strings = []
        if variables.match_timing:
            try:
                index = self.match_timing_strings.index(variables.match_timing)
            except ValueError:
                self.spawn_box.delete(0, tk.END)
                return
            variables.spawn_index = index
            self.spawn_box.delete(0, tk.END)
            self.spawn_box.insert(tk.END, "All spawns")
            for spawn in variables.spawn_timings[index]:
                self.spawn_timing_strings.append(str(spawn.time()))
            for spawn in self.spawn_timing_strings:
                self.spawn_box.insert(tk.END, spawn)

    def add_files_cb(self):
        """
        Function that adds the files to the list that are currently in the directory when the
        :return:
        """

        self.file_strings = []
        self.files_dict = {}
        self.file_box.delete(0, tk.END)
        self.match_box.delete(0, tk.END)
        self.spawn_box.delete(0, tk.END)
        self.main_window.middle_frame.abilities_treeview.delete(*self.main_window.abilities_treeview.get_children(""))
        self.main_window.middle_frame.enemies_treeview.delete(
            *self.main_window.middle_frame.enemies_treeview.get_children())
        self.main_window.ship_frame.ship_label_var.set("")
        self.splash = toplevels.splash_screen(self.main_window)
        try:
            old_path = os.getcwd()
            os.chdir(variables.settings_obj.cl_path)
            os.chdir(old_path)
        except OSError:
            tkMessageBox.showerror("Error", "The CombatLogs folder found in the settings file is not valid. Please "
                                            "choose another folder.")
            folder = tkFileDialog.askdirectory(title="CombatLogs folder")
            variables.settings_obj.write_settings_dict({('parsing', 'cl_path'): folder})
            variables.settings_obj.read_set()
        for file in os.listdir(variables.settings_obj.cl_path):
            if file.endswith(".txt"):
                if statistics.check_gsf(variables.settings_obj.cl_path + "/" + file):
                    try:
                        if variables.settings_obj.date_format == "ymd":
                            dt = datetime.strptime(file[:-10], "combat_%Y-%m-%d_%H_%M_%S_").strftime("%Y-%m-%d   %H:%M")
                        elif variables.settings_obj.date_format == "ydm":
                            dt = datetime.strptime(file[:-10], "combat_%Y-%m-%d_%H_%M_%S_").strftime(
                                "%Y-%d-%m   %H:%M:%S")
                        else:
                            tkMessageBox.showerror("No valid date format setting found.")
                            return
                    except ValueError:
                        dt = file
                    self.files_dict[dt] = file
                    self.file_strings.append(dt)
                variables.files_done += 1
                self.splash.update_progress()
        self.file_box.insert(tk.END, "All CombatLogs")
        for file in self.file_strings:
            self.file_box.insert(tk.END, file)
        self.splash.destroy()
        return

    def add_files(self, silent=False):
        """
        Function that checks files found in the in the settings specified folder for
        GSF matches and if those are found in a file, it gets added to the listbox
        Also calls for a splash screen if :param silent: is set to False
        :param silent:
        :return:
        """

        self.file_strings = []
        self.files_dict = {}
        self.file_box.delete(0, tk.END)
        self.match_box.delete(0, tk.END)
        self.spawn_box.delete(0, tk.END)
        self.main_window.middle_frame.abilities_treeview.delete(
            *self.main_window.middle_frame.abilities_treeview.get_children())
        self.main_window.middle_frame.enemies_treeview.delete(
            *self.main_window.middle_frame.enemies_treeview.get_children())
        self.main_window.ship_frame.ship_label_var.set("")
        if not silent:
            self.splash = toplevels.splash_screen(self.main_window)
        try:
            old_cwd = os.getcwd()
            os.chdir(variables.settings_obj.cl_path)
            os.chdir(old_cwd)
        except OSError:
            tkMessageBox.showerror("Error", "The CombatLogs folder found in the settings file is not valid. Please "
                                            "choose another folder.")
            folder = tkFileDialog.askdirectory(title="CombatLogs folder")
            variables.settings_obj.write_settings_dict({('parsing', 'cl_path'): folder})
            variables.settings_obj.read_set()
        for file in os.listdir(variables.settings_obj.cl_path):
            if file.endswith(".txt"):
                if statistics.check_gsf(variables.settings_obj.cl_path + "/" + file):
                    try:
                        dt = datetime.strptime(file[:-10], "combat_%Y-%m-%d_%H_%M_%S_").strftime("%Y-%m-%d   %H:%M")
                    except ValueError:
                        dt = file
                    self.files_dict[dt] = file
                    self.file_strings.append(dt)
                variables.files_done += 1
                if not silent:
                    self.splash.update_progress()
                else:
                    self.main_window.splash.update_progress()
        self.file_box.insert(tk.END, "All CombatLogs")
        for file in self.file_strings:
            self.file_box.insert(tk.END, file)
        if not silent:
            self.splash.destroy()
        return

    def file_update(self, instance):
        """
        Function either sets the file and calls add_matches to add the matches found in the file
        to the matches_listbox, or starts the parsing of all files found in the specified folder
        and displays the results in the other frames.
        :param instance: for Tkinter callback
        :return:
        """
        self.main_window.middle_frame.statistics_numbers_var.set("")
        self.main_window.ship_frame.ship_label_var.set("No match or spawn selected yet.")
        self.main_window.middle_frame.enemies_treeview.delete(
            *self.main_window.middle_frame.enemies_treeview.get_children())
        self.main_window.middle_frame.enemies_treeview.delete(
            *self.main_window.middle_frame.enemies_treeview.get_children())
        for index, filestring in enumerate(self.file_box.get(0, tk.END)):
            self.file_box.itemconfig(index, background="white")
        if self.file_box.curselection() == (0,) or self.file_box.curselection() == ('0',):
            self.old_file = 0
            self.file_box.itemconfig(self.old_file, background="lightgrey")
            (abilities_dict, statistics_string, shipsdict, enemies, enemydamaged,
             enemydamaget, uncounted) = statistics.statistics.folder_statistics()
            self.main_window.middle_frame.statistics_numbers_var.set(statistics_string)
            for key, value in abilities_dict.iteritems():
                self.main_window.middle_frame.abilities_treeview.insert('', tk.END, values=(key, value))
            self.main_window.middle_frame.events_button.config(state=tk.DISABLED)
            ships_string = "Ships used:\t\tCount:\n"
            for ship in abilities.ships_strings:
                try:
                    ships_string += ship + "\t\t" + str(shipsdict[ship.replace("\t", "", 1)]) + "\n"
                except KeyError:
                    ships_string += ship + "\t\t0\n"
            ships_string += "Uncounted\t\t" + str(uncounted)
            self.main_window.ship_frame.ship_label_var.set(ships_string)
            for enemy in enemies:
                if enemy == "":
                    self.main_window.middle_frame.enemies_treeview.insert('', tk.END,
                                                                          values=("System",
                                                                                  str(enemydamaged[enemy]),
                                                                                  str(enemydamaget[enemy])))
                elif re.search('[a-zA-Z]', enemy):
                    self.main_window.middle_frame.enemies_treeview.insert('', tk.END,
                                                                          values=(enemy,
                                                                                  str(enemydamaged[enemy]),
                                                                                  str(enemydamaget[enemy])))
                else:
                    self.main_window.middle_frame.enemies_treeview.insert('', tk.END,
                                                                          values=(enemy,
                                                                                  str(enemydamaged[enemy]),
                                                                                  str(enemydamaget[enemy])))

            self.main_window.middle_frame.events_button.config(state=tk.DISABLED)
            most_used_ship = max(shipsdict.iteritems(), key=operator.itemgetter(1))[0]
            self.main_window.ship_frame.update_ship([most_used_ship])
            self.main_window.ship_frame.update()
        else:
            self.match_box.focus()
            # Find the file name of the file selected in the list of file names
            numbers = self.file_box.curselection()
            self.old_file = numbers[0]
            self.file_box.itemconfig(self.old_file, background="lightgrey")
            try:
                variables.file_name = self.files_dict[self.file_strings[numbers[0] - 1]]
            except TypeError:
                variables.file_name = self.files_dict[self.file_strings[int(numbers[0]) - 1]]
            except KeyError:
                tkMessageBox.showerror("Error", "The parser encountered an error while selecting the file. Please "
                                                "consult the issues page of the GitHub repository.")
            # Read all the lines from the selected file
            with open(variables.settings_obj.cl_path + "/" + variables.file_name, "rU") as clicked_file:
                lines = clicked_file.readlines()
            # PARSING STARTS
            # Get the player ID numbers from the list of lines
            player = parse.determinePlayer(lines)
            # Parse the lines with the acquired player ID numbers
            variables.file_cube, variables.match_timings, variables.spawn_timings = parse.splitter(lines, player)
            # Start adding the matches from the file to the listbox
            self.add_matches()
            self.main_window.ship_frame.remove_image()

    def match_update(self, instance):
        """
        Either adds sets the match and calls add_spawns to add the spawns found in the match
        or starts the parsing of all files found in the specified file and displays the results
        in the other frames.
        :param instance: for Tkinter callback
        :return:
        """

        self.main_window.middle_frame.statistics_numbers_var.set("")
        self.main_window.ship_frame.ship_label_var.set("No match or spawn selected yet.")
        for index, matchstring in enumerate(self.match_box.get(0, tk.END)):
            self.match_box.itemconfig(index, background="white")
        self.main_window.middle_frame.enemies_treeview.delete(
            *self.main_window.middle_frame.enemies_treeview.get_children())
        self.main_window.middle_frame.enemies_treeview.delete(
            *self.main_window.middle_frame.enemies_treeview.get_children())
        if self.match_box.curselection() == (0,) or self.match_box.curselection() == ('0',):
            self.spawn_box.delete(0, tk.END)
            numbers = self.match_box.curselection()
            self.old_match = numbers[0]
            self.match_box.itemconfig(self.old_match, background="lightgrey")
            try:
                variables.match_timing = self.match_timing_strings[numbers[0] - 1]
            except TypeError:
                variables.match_timing = self.match_timing_strings[int(numbers[0]) - 1]
            file_cube = variables.file_cube
            (abilities_dict, statistics_string, shipsdict, enemies,
             enemydamaged, enemydamaget, uncounted) = self.statistics_object.file_statistics(file_cube)
            for key, value in abilities_dict.iteritems():
                self.main_window.middle_frame.abilities_treeview.insert('', tk.END, values=(key, value))
            self.main_window.middle_frame.statistics_numbers_var.set(statistics_string)
            ships_string = "Ships used:\t\tCount:\n"
            for ship in abilities.ships_strings:
                try:
                    ships_string += ship + "\t\t" + str(shipsdict[ship.replace("\t", "", 1)]) + "\n"
                except KeyError:
                    ships_string += ship + "\t\t0\n"
            ships_string += "Uncounted\t\t" + str(uncounted)
            self.main_window.ship_frame.ship_label_var.set(ships_string)
            for enemy in enemies:
                if enemy == "":
                    self.main_window.middle_frame.enemies_treeview.insert('', tk.END,
                                                                          values=("System",
                                                                                  str(enemydamaged[enemy]),
                                                                                  str(enemydamaget[enemy])))
                elif re.search('[a-zA-Z]', enemy):
                    self.main_window.middle_frame.enemies_treeview.insert('', tk.END,
                                                                          values=(enemy,
                                                                                  str(enemydamaged[enemy]),
                                                                                  str(enemydamaget[enemy])))
                else:
                    self.main_window.middle_frame.enemies_treeview.insert('', tk.END,
                                                                          values=(enemy,
                                                                                  str(enemydamaged[enemy]),
                                                                                  str(enemydamaget[enemy])))

            self.main_window.middle_frame.events_button.config(state=tk.DISABLED)
        else:
            self.spawn_box.focus()
            numbers = self.match_box.curselection()
            self.old_match = numbers[0]
            self.match_box.itemconfig(self.old_match, background="lightgrey")
            try:
                variables.match_timing = self.match_timing_strings[numbers[0] - 1]
            except TypeError:
                variables.match_timing = self.match_timing_strings[int(numbers[0]) - 1]
            self.add_spawns()
        self.main_window.ship_frame.remove_image()

    def spawn_update(self, instance):
        """
        Either starts the parsing of ALL spawns found in the specified match or just one of them
        and displays the results in the other frames accordingly
        :param instance: for Tkinter callback
        :return:
        """
        for index, spawnstring in enumerate(self.spawn_box.get(0, tk.END)):
            self.spawn_box.itemconfig(index, background="white")
        self.main_window.middle_frame.enemies_treeview.delete(
            *self.main_window.middle_frame.enemies_treeview.get_children())
        self.main_window.middle_frame.enemies_treeview.delete(
            *self.main_window.middle_frame.enemies_treeview.get_children())
        if self.spawn_box.curselection() == (0,) or self.spawn_box.curselection() == ('0',):
            self.old_spawn = self.spawn_box.curselection()[0]
            self.spawn_box.itemconfig(self.old_spawn, background="lightgrey")
            match = variables.file_cube[self.match_timing_strings.index(variables.match_timing)]
            for spawn in match:
                variables.player_numbers.update(parse.determinePlayer(spawn))
            (abilities_dict, statistics_string, shipsdict, enemies,
             enemydamaged, enemydamaget) = self.statistics_object.match_statistics(match)
            for key, value in abilities_dict.iteritems():
                self.main_window.middle_frame.abilities_treeview.insert('', tk.END, values=(key, value))
            self.main_window.middle_frame.statistics_numbers_var.set(statistics_string)
            ships_string = "Ships used:\t\tCount:\n"
            for ship in abilities.ships_strings:
                try:
                    ships_string += ship + "\t\t" + str(shipsdict[ship.replace("\t", "", 1)]) + "\n"
                except KeyError:
                    ships_string += ship + "\t\t0\n"
            ships_string += "Uncounted\t\t%s" % shipsdict["Uncounted"]
            for enemy in enemies:
                if enemy == "":
                    self.main_window.middle_frame.enemies_treeview.insert('', tk.END,
                                                                          values=("System",
                                                                                  str(enemydamaged[enemy]),
                                                                                  str(enemydamaget[enemy])))
                elif re.search('[a-zA-Z]', enemy):
                    self.main_window.middle_frame.enemies_treeview.insert('', tk.END,
                                                                          values=(enemy,
                                                                                  str(enemydamaged[enemy]),
                                                                                  str(enemydamaget[enemy])))
                else:
                    self.main_window.middle_frame.enemies_treeview.insert('', tk.END,
                                                                          values=(enemy,
                                                                                  str(enemydamaged[enemy]),
                                                                                  str(enemydamaget[enemy])))

            self.main_window.middle_frame.events_button.config(state=tk.DISABLED)
            self.main_window.ship_frame.remove_image()
        else:
            numbers = self.spawn_box.curselection()
            self.old_spawn = numbers[0]
            self.spawn_box.itemconfig(self.old_spawn, background="lightgrey")
            try:
                variables.spawn_timing = self.spawn_timing_strings[numbers[0] - 1]
            except TypeError:
                try:
                    variables.spawn_timing = self.spawn_timing_strings[int(numbers[0]) - 1]
                except:
                    tkMessageBox.showerror("Error",
                                           "The parser encountered a bug known as #19 in the repository. "
                                           "This bug has not been fixed. Check out issue #19 in the repository"
                                           " for more information.")
            try:
                match = variables.file_cube[self.match_timing_strings.index(variables.match_timing)]
            except ValueError:
                print "[DEBUG] vars.match_timing not in self.match_timing_strings!"
                return
            spawn = match[self.spawn_timing_strings.index(variables.spawn_timing)]
            variables.spawn = spawn
            variables.player_numbers = parse.determinePlayer(spawn)
            (abilities_dict, statistics_string, ships_list, ships_comps,
             enemies, enemydamaged, enemydamaget) = self.statistics_object.spawn_statistics(spawn)
            for key, value in abilities_dict.iteritems():
                self.main_window.middle_frame.abilities_treeview.insert('', tk.END, values=(key, value))
            self.main_window.middle_frame.statistics_numbers_var.set(statistics_string)
            ships_string = "Possible ships used:\n"
            for ship in ships_list:
                ships_string += str(ship) + "\n"
            ships_string += "\t\t\t\t\t\t\nWith the components:\n"
            for component in ships_comps:
                ships_string += component + "\n"
            self.main_window.ship_frame.ship_label_var.set(ships_string)
            for enemy in enemies:
                if enemy == "":
                    self.main_window.middle_frame.enemies_treeview.insert('', tk.END,
                                                                          values=("System",
                                                                                  str(enemydamaged[enemy]),
                                                                                  str(enemydamaget[enemy])))
                elif re.search('[a-zA-Z]', enemy):
                    self.main_window.middle_frame.enemies_treeview.insert('', tk.END,
                                                                          values=(enemy,
                                                                                  str(enemydamaged[enemy]),
                                                                                  str(enemydamaget[enemy])))
                else:
                    self.main_window.middle_frame.enemies_treeview.insert('', tk.END,
                                                                          values=(enemy,
                                                                                  str(enemydamaged[enemy]),
                                                                                  str(enemydamaget[enemy])))

            self.main_window.middle_frame.events_button.state(["!disabled"])
            self.main_window.ship_frame.update_ship(ships_list)


class ship_frame(ttk.Frame):
    """
    Simple frame with a picture and a string containing information about the ships
    used by the player.
    -----------------------------------
    | ------------------------------- |
    | |                             | |
    | | image of ship of player     | |
    | |                             | |
    | ------------------------------- |
    | string                          |
    | of                              |
    | text                            |
    |                                 |
    -----------------------------------
    """

    def __init__(self, root_frame):
        """
        Create all labels and variables
        :param root_frame:
        """
        ttk.Frame.__init__(self, root_frame, width=300, height=410)
        self.ship_label_var = tk.StringVar()
        self.ship_label_var.set("No match or spawn selected yet.")
        self.ship_label = ttk.Label(self, textvariable=self.ship_label_var, justify=tk.LEFT, wraplength=495)
        self.ship_image = ttk.Label(self)

    def grid_widgets(self):
        """
        Put the widgets in the right place
        :return:
        """
        self.ship_image.grid(column=0, row=0, sticky=tk.N+tk.S+tk.W+tk.E)
        self.ship_label.grid(column=0, row=1, sticky=tk.N+tk.S+tk.W+tk.E)
        self.remove_image()

    def update_ship(self, ships_list):
        """
        Update the picture of the ship by using the ships_list as reference
        If more ships are possible, set the default.
        If zero ships are possible, there must be an error somewhere in the abilities module
        :param ships_list:
        :return:
        """
        if len(ships_list) > 1:
            print "[DEBUG] Ship_list larger than 1, setting default.png"
            try:
                self.set_image(os.path.dirname(__file__).replace("frames", "") + "assets\\img\\default.png")
            except IOError:
                print "[DEBUG] File not found."
                tkMessageBox.showerror("Error",
                                       "The specified picture can not be found. Is the assets folder copied correctly?")
                return
        elif len(ships_list) == 0:
            raise ValueError("Ships_list == 0")
        else:
            print "[DEBUG]  Ship_list not larger than one, setting appropriate image"
            try:
                self.set_image(os.path.dirname(__file__).replace("frames", "") + "assets\\img\\" + ships_list[0]
                               + ".png")
            except IOError:
                print "[DEBUG] File not found: ", os.path.dirname(__file__).replace("frames", "") + "assets\\img\\" \
                                                  + ships_list[0] + ".png"
                tkMessageBox.showerror("Error",
                                       "The specified picture can not be found. Is the assets folder copied correctly?")
                return
        return

    def set_image(self, file):
        """
        Set the image file, unless there is an IOError, because  then the assets folder is not in place
        :param file:
        :return:
        """
        try:
            self.img = Image.open(file)
            self.img = self.img.resize((300, 180), Image.ANTIALIAS)
            self.pic = ImageTk.PhotoImage(self.img)
            self.ship_image.config(image=self.pic)
        except tk.TclError as e:
            print e

    def remove_image(self):
        """
        Set the default image
        :return:
        """
        try:
            self.pic = ImageTk.PhotoImage(Image.open(os.path.dirname(os.path.realpath(__file__)).
                                                     replace("frames", "") +
                                                     "assets\\img\\default.png").resize((300, 180), Image.ANTIALIAS))
        except IOError:
            print "[DEBUG] default.png can not be opened."
            return
        try:
            self.ship_image.config(image=self.pic)
        except tk.TclError:
            pass


class middle_frame(ttk.Frame):
    """
    A simple frame containing a notebook with three tabs to show statistics and information to the user
    Main frame:
    ----------------------------------
    |  _____ _____ _____             |
    | |_____|_____|_____|___________ |
    | | frame to display            ||
    | |_____________________________||
    ----------------------------------

    Statistics tab:
    ----------------------------------
    | list                           |
    | of                             |
    | stats                          |
    ----------------------------------

    Enemies tab:
    -----------------------------
    | Help string               |
    | ______ ______ ______ ____ |
    | |enem| |dmgd| |dmgt| |/\| |
    | |enem| |dmgd| |dmgt| |||| |
    | |enem| |dmgd| |dmgt| |\/| |
    | |____| |____| |____| |__| |
    -----------------------------

    Abilities tab:
    -----------------------------
    | ability              |/\| |
    | ability              |||| |
    | ability              |\/| |
    -----------------------------
    """

    def __init__(self, root_frame, main_window):
        """
        Set up all widgets and variables. StringVars can be manipulated by the file frame,
        so that frame can set the statistics to be shown in this frame. Strings for Tkinter
        cannot span multiple lines!
        :param root_frame:
        :param main_window:
        """
        ttk.Frame.__init__(self, root_frame)
        self.window = main_window
        self.notebook = ttk.Notebook(self, width=300, height=310)
        self.stats_frame = ttk.Frame(self.notebook)
        self.enemies_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistics")
        self.notebook.add(self.enemies_frame, text="Enemies")
        self.events_frame = ttk.Frame(self, width=300)
        self.events_button = ttk.Button(self.events_frame, text="Show events for spawn", command=self.show_events,
                                        state=tk.DISABLED, width=43)
        self.statistics_label_var = tk.StringVar()
        string = "Damage dealt to\nDamage dealt:\nDamage taken:\nDamage ratio:\nSelfdamage:\nHealing received:\n" + \
                 "Hitcount:\nCriticalcount:\nCriticalluck:\nDeaths:\nDuration:\nDPS:"
        self.statistics_label_var.set(string)
        self.statistics_label = ttk.Label(self.stats_frame, textvariable=self.statistics_label_var, justify=tk.LEFT,
                                          wraplength=145)
        self.statistics_numbers_var = tk.StringVar()
        self.statistics_label.setvar()
        self.statistics_numbers = ttk.Label(self.stats_frame, textvariable=self.statistics_numbers_var,
                                            justify=tk.LEFT, wraplength=145)
        self.enemies_treeview = ttk.Treeview(self.enemies_frame, columns=("Enemy name/ID", "Damage dealt",
                                                                          "Damage taken"),
                                             displaycolumns=("Enemy name/ID", "Damage dealt", "Damage taken"),
                                             height=14)
        self.enemies_treeview.heading("Enemy name/ID", text="Enemy name/ID",
                                      command=lambda: self.treeview_sort_column(self.enemies_treeview,
                                                                                "Enemy name/ID", False, "str"))
        self.enemies_treeview.heading("Damage dealt", text="Damage dealt",
                                      command=lambda: self.treeview_sort_column(self.enemies_treeview,
                                                                                "Damage dealt", False, "int"))
        self.enemies_treeview.heading("Damage taken", text="Damage taken",
                                      command=lambda: self.treeview_sort_column(self.enemies_treeview,
                                                                                "Damage taken", False, "int"))
        self.enemies_treeview["show"] = "headings"
        self.enemies_treeview.column("Enemy name/ID", width=125, stretch=False, anchor=tk.W)
        self.enemies_treeview.column("Damage taken", width=80, stretch=False, anchor=tk.E)
        self.enemies_treeview.column("Damage dealt", width=80, stretch=False, anchor=tk.E)
        self.enemies_scrollbar = ttk.Scrollbar(self.enemies_frame, orient=tk.VERTICAL,
                                               command=self.enemies_treeview.yview)
        self.enemies_treeview.config(yscrollcommand=self.enemies_scrollbar.set)
        self.abilities_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.abilities_frame, text="Abilities")
        self.abilities_treeview = ttk.Treeview(self.abilities_frame, columns=("Ability", "Times used"),
                                               displaycolumns=("Ability", "Times used"), height=14)
        self.abilities_treeview.column("Ability", width=200, stretch=False, anchor=tk.W)
        self.abilities_treeview.column("Times used", width=85, stretch=False, anchor=tk.E)
        self.abilities_treeview.heading("Ability", text="Ability",
                                        command=lambda: self.treeview_sort_column(self.abilities_treeview,
                                                                                  "Ability", False, "str"))
        self.abilities_treeview.heading("Times used", text="Times used",
                                        command=lambda: self.treeview_sort_column(self.abilities_treeview,
                                                                                  "Times used", False, "int"))
        self.abilities_treeview["show"] = "headings"
        self.abilities_scrollbar = ttk.Scrollbar(self.abilities_frame, orient=tk.VERTICAL,
                                                 command=self.abilities_treeview.yview)
        self.abilities_treeview.config(yscrollcommand=self.abilities_scrollbar.set)
        self.notice_label = ttk.Label(self.stats_frame, text="\n\n\n\nThe damage dealt for bombers can not be " +
                                                             "accurately calculated due to CombatLog limitations, "
                                                             "as damage dealt by bombs is not recorded.",
                                      justify=tk.LEFT, wraplength=290)

    def show_events(self):
        """
        Open a TopLevel of the overlay module to show the lines of a Combatlog in a human-readable manner
        :return:
        """
        self.toplevel = toplevels.events_view(self.window, variables.spawn, variables.player_numbers)

    def grid_widgets(self):
        """
        Put all widgets in the right place
        :return:
        """
        self.abilities_treeview.grid(column=0, row=0, sticky=tk.N+tk.W)
        self.abilities_scrollbar.grid(column=1, row=0, sticky=tk.N+tk.S+tk.W+tk.E)
        self.notebook.grid(column=0, row=0, columnspan=4, sticky=tk.N+tk.W+tk.E)
        self.events_frame.grid(column=0, row=1, columnspan=4, sticky=tk.N+tk.W + tk.S + tk.E)
        self.events_button.grid(column=0, row=1, sticky=tk.N+tk.W + tk.S + tk.E, columnspan=4, pady=12)
        self.statistics_label.grid(column=0, row=2, columnspan=2, sticky=tk.N+tk.S+tk.W+tk.E)
        self.statistics_numbers.grid(column=2, row=2, columnspan=2, sticky=tk.N+tk.W+tk.E)
        self.notice_label.grid(column=0, row=3, columnspan=4, sticky=tk.W+tk.E+tk.S)
        self.enemies_treeview.grid(column=0, row=0, sticky=tk.N+tk.S+tk.W+tk.E)
        self.enemies_scrollbar.grid(column=1, row=0, sticky=tk.N+tk.S+tk.W+tk.E)

    def treeview_sort_column(self, treeview, column, reverse, type):
        l = [(treeview.set(k, column), k) for k in treeview.get_children('')]
        if type == "int":
            l.sort(key=lambda t: int(t[0]), reverse=reverse)
        elif type == "str":
            l.sort(key=lambda t: t[0], reverse=reverse)
        else:
            raise NotImplementedError
        for index, (val, k) in enumerate(l):
            treeview.move(k, '', index)
        treeview.heading(column, command=lambda: self.treeview_sort_column(treeview, column, not reverse, type))


