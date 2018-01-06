# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE
# General imports
import os
import shelve
# UI imports
import tkinter.ttk as ttk
import tkinter as tk
from tkinter import messagebox
from ttkwidgets import CheckboxTreeview
# Own modules
from server.sharing_client import SharingClient
from variables import settings
from parsing.parser import Parser
from tools.utilities import get_temp_directory
from server.sharing_data import *


def get_connected_client():
    """
    Setup a SharingClient and return the functional instance, or None
    if it failed. Also provides error handling if the SharingClient
    fails to connect to the server.
    """
    client = SharingClient()
    try:
        client.connect()
    except ConnectionRefusedError:
        messagebox.showerror("Error", "The remote server refused the connection.")
        return None
    except Exception as e:
        messagebox.showerror("Error", "An unidentified error occurred while connecting to the remote server:\n\n"
                                      "{}".format(repr(e)))
        return None
    client.start()
    return client


class SharingFrame(ttk.Frame):
    """
    A Frame to contain widgets to allow uploading of CombatLogs to the server
    and viewing leaderboards that keep track of individual player performance
    on different fronts. A connection to the server is required, and as the
    GSF Server is not done yet, this Frame is still empty.
    """

    def __init__(self, root_frame, window):
        """
        :param root_frame: The MainWindow.notebook
        :param window: The MainWindow instance
        """
        ttk.Frame.__init__(self, root_frame)
        self.window = window
        self.cancel_sync = False
        # Open the sharing database
        sharing_db_path = os.path.join(get_temp_directory(), "share.db")
        self.sharing_db = shelve.open(sharing_db_path)
        # Initialize SharingClient
        self.client = SharingClient()
        # Initialize CheckboxTreeview
        self.file_tree_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.file_tree = CheckboxTreeview(
            self, height=14, columns=("name", "legacy", "pcount", "psync", "ecount", "esync"),
            yscrollcommand=self.file_tree_scroll.set, show=("headings", "tree"))
        self.setup_treeview()
        self.update_tree()
        # Setup the progress bar and Synchronize button
        self.progress_bar = ttk.Progressbar(self, orient=tk.HORIZONTAL, mode="determinate")
        self.progress_bar["maximum"] = 1
        self.synchronize_button = ttk.Button(self, text="Synchronize", command=self.synchronize, width=5)
        # Create a binding to F5
        self.bind("<F5>", self.update_tree)

    def grid_widgets(self):
        """
        The usual for putting the widgets into their correct positions
        """
        self.file_tree.grid(row=1, column=1, columnspan=4, padx=5, pady=5, sticky="nswe")
        self.file_tree_scroll.grid(row=1, column=5, padx=(0, 5), pady=5, sticky="ns")
        self.progress_bar.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="we")
        self.synchronize_button.grid(row=2, column=4, columnspan=2, padx=(0, 5), pady=5, sticky="nswe")

    def setup_treeview(self):
        """
        Setup the Treeview with column names and headings
        """
        self.file_tree_scroll.config(command=self.file_tree.yview)

        self.file_tree.column("#0", width=180, stretch=False, anchor=tk.E)
        self.file_tree.heading("#0", text="CombatLog")
        self.file_tree.column("name", width=110, anchor=tk.W)
        self.file_tree.heading("name", text="Player name")
        self.file_tree.column("legacy", width=110, stretch=False, anchor=tk.W)
        self.file_tree.heading("legacy", text="Legacy name")
        self.file_tree.column("pcount", width=70, stretch=False, anchor=tk.E)
        self.file_tree.heading("pcount", text="ID Count\nPlayer")
        self.file_tree.column("psync", width=100, stretch=False, anchor=tk.E)
        self.file_tree.heading("psync", text="Synchronized\nPlayer")
        self.file_tree.column("ecount", width=70, stretch=False, anchor=tk.E)
        self.file_tree.heading("ecount", text="ID Count\nEnemy")
        self.file_tree.column("esync", width=100, stretch=False, anchor=tk.E)
        self.file_tree.heading("esync", text="Synchronized\nEnemy")

        self.file_tree.tag_configure("complete", background="lawn green")
        self.file_tree.tag_configure("checked", background="light goldenrod")
        self.file_tree.tag_configure("incomplete", background="#ffb5b5")
        self.file_tree.tag_configure("invalid", background="gray60")

    def synchronize(self):
        """
        Function for the sync_button to call when pressed. Connects to the server.
        """
        print("[SharingFrame] Starting synchronization")
        # Connect to the server
        client = get_connected_client()
        if client is None:
            return
        character_data = self.window.characters_frame.characters
        character_names = self.window.characters_frame.get_player_servers()
        skipped = []
        completed = []
        self.synchronize_button.config(text="Cancel", command=self.cancel_synchronize)
        # Loop over files selected for sharing
        file_list = self.file_tree.get_checked()
        self.progress_bar["maximum"] = len(file_list)
        for file_name in file_list:
            self.progress_bar["value"] += 1
            if self.cancel_sync is True or not client.is_alive():
                break
            print("[SharingFrame] Synchronizing file '{}'".format(file_name))
            lines = self.read_file(file_name)
            id_list = Parser.get_player_id_list(lines)
            enemy_ids = Parser.get_enemy_id_list(lines, id_list)
            synchronized = self.get_amount_synchronized(file_name, id_list, enemy_ids)
            if synchronized == "Complete":
                print("[SharingFrame] Already synchronized:", file_name)
                continue
            player_name = Parser.get_player_name(lines)
            # Skip files with ambiguous server
            if player_name not in character_names:
                skipped.append(file_name)
                print("[SharingFrame] Skipping file:", file_name)
                continue
            server = character_names[player_name]
            self.sharing_db[file_name] = 0
            # Actually start synchronizing
            print("[ShareFrame] Sending player ID list")
            result = self.send_player_id_list(id_list, character_data, server, player_name, file_name, client)
            if result is False:
                messagebox.showerror("Error", "Failed to send ID numbers.")
                break
            completed.append(file_name)
        client.close()
        print("[SharingFrame] Synchronization completed.")
        self.cancel_sync = False
        self.synchronize_button.config(state=tk.NORMAL, text="Synchronize", command=self.synchronize)
        self.update_tree()
        self.progress_bar["value"] = 0

    def send_player_id_list(self, id_list, character_data, server, player_name, file_name, client):
        for player_id in id_list:
            print("[SharingFrame] Sharing ID '{}' for name '{}'".format(player_id, player_name))
            legacy_name = character_data[(server, player_name)]["Legacy"]
            faction = character_data[(server, player_name)]["Faction"]
            print("[SharingFrame] Sending data: {}, {}, {}".format(player_id, legacy_name, server))
            result = client.send_name_id(server, factions_dict[faction], legacy_name, player_name, player_id)
            if result is False:
                return False
            self.sharing_db[file_name] += 1
        return True

    @staticmethod
    def show_confirmation_dialog(skipped, completed):
        """
        Show a confirmation dialog listing the skipped and completed
        files during synchronization.
        :param skipped: List of skipped file names
        :param completed: List of completed file names
        """
        # Build information string
        string = "The following files were skipped because the server of the character could not be determined:\n"
        for skipped_file in skipped:
            string += skipped_file + "\n"
        string += "The following files were successfully synchronized:\n"
        for completed_file in completed:
            string += completed_file + "\n"
        messagebox.showinfo("Info", string)

    def cancel_synchronize(self):
        """
        Callback for button to stop the synchronization process. Does
        not actually stop the process, only sets a flag that gets
        checked by the synchronization function.
        """
        self.cancel_sync = True
        self.synchronize_button.config(state=tk.DISABLED)

    def update_tree(self, *args):
        """
        Updates the contents of the Treeview with files. Parses the
        files in the process to determine the following:
        - Whether the file is a valid GSF CombatLog
        - A string for the file
        - The player name
        - The player ID numbers
        - The enemy ID numbers
        """
        self.file_tree.delete(*self.file_tree.get_children(""))
        # This function provides a dictionary with player names as keys and servers as values
        character_names = self.window.characters_frame.characters.get_player_servers()
        for item in os.listdir(settings["parsing"]["path"]):
            # Skip non-GSF CombatLogs
            if not Parser.get_gsf_in_file(item):
                continue
            # Parse file name
            file_string = Parser.parse_filename(item)
            if file_string is None:
                # Renamed CombatLogs are not valid for use
                continue
            # Read the file
            lines = self.read_file(item)
            # Parse the file
            player_name = Parser.get_player_name(lines)
            legacy_name = "" if player_name not in character_names else character_names[player_name]
            player_ids = Parser.get_player_id_list(lines)
            enemy_ids = Parser.get_enemy_id_list(lines, player_ids)
            # Check how much of the IDs in this file were already synchronized
            player_sync, enemy_sync = self.get_amount_synchronized(item, player_ids, enemy_ids)
            # Generate a tag to give a background color
            tags = ("complete",) if player_sync == "Complete" and enemy_sync == "Complete" else ("incomplete",)
            tags = tags if legacy_name != "" else ("invalid",)
            # Insert the file into the Treeview
            self.file_tree.insert(
                "", tk.END, text=file_string, iid=item, tags=(tags,),
                values=(player_name, legacy_name, len(player_ids), player_sync, len(enemy_ids), enemy_sync))
        return

    @staticmethod
    def read_file(file_name):
        path = os.path.join(settings["parsing"]["path"], file_name)
        with open(path, "rb") as fi:
            lines = []
            for line in fi:
                try:
                    lines.append(line.decode())
                except UnicodeDecodeError:
                    continue
        return lines

    def __exit__(self):
        self.save_database()

    """
    The following functions are for database operations.
    """

    def save_database(self):
        self.sharing_db.close()

    def get_amount_synchronized(self, file_name, player_ids, enemy_ids):
        """
        Return the amount of ID numbers that was synchronized for this
        file, or "Complete" if all were synchronized.
        """
        # First open the file to determine the amount of IDs
        if file_name not in self.sharing_db:
            self.sharing_db[file_name] = {"player_sync": 0, "enemy_sync": 0, "enemies": {}}
        player_sync = self.sharing_db[file_name]["player_sync"]
        enemy_sync = self.sharing_db[file_name]["enemy_sync"]
        result = ("Complete" if player_sync == len(player_ids) else player_sync,
                  "Complete" if enemy_sync == len(enemy_ids) else enemy_sync)
        return result
