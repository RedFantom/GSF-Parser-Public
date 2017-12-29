# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# Own modules
from tools.utilities import get_temp_directory
# General imports
from parsing.parser import Parser
from parsing.vision import get_tracking_degrees, get_distance_from_center
from parsing import abilities
from parsing.keys import keys
# General imports
from pynput.mouse import Button
from pynput.keyboard import Key
import pickle as pickle
import os
from datetime import datetime
import operator


class FileHandler(object):
    """
    Reads the files generated by ScreenParser for file parsing, for information on the contents of the database, please
    consult the screen_alt.py docstring.
    """
    colors = {
        "primaries": "#ff6666",
        "secondaries": "#ff003b",
        "shields_front": "green",
        "shields_rear": "green",
        "hull": "brown",
        "systems": "#668cff",
        "engines": "#b380ff",
        "shields": "#8cac20",
        "copilot": "#17a3ff",
        "tracking": "#ffcc00",
        "wpower": "#ff9933",
        "epower": "#751aff",
        "power_mgmt": "darkblue",
    }

    keys = {
        "1": "systems",
        "2": "shields",
        "3": "engines",
        "4": "copilot",
        "F1": ("power_mgmt", 1),
        "F2": ("power_mgmt", 2),
        "F3": ("power_mgmt", 3),
        "F4": ("power_mgmt", 4)
    }

    health_colors = {
        None: "grey",
        0: "black",
        25: "red",
        50: "orange",
        75: "yellow",
        100: "green",
        125: "blue"
    }

    power_mgmt_colors = {
        1: "orange",
        2: "cyan",
        3: "purple",
        4: "darkblue",
        None: "black"
    }

    click_colors = {
        "primaries": "#ff7070",
        "secondaries": "#ff5179",
        "engines": "#c9a5ff",
        "shields": "#c0d86e",
        "systems": "#9bb4ff",
        "copilot": "#77c3f4"
    }

    @staticmethod
    def get_dictionary_key(dictionary, timing, value=False):
        if not isinstance(dictionary, dict):
            raise ValueError()
        if not isinstance(timing, datetime):
            raise ValueError()
        for key, val in dictionary.items():
            if not isinstance(key, datetime):
                continue
            if key == timing:
                if value:
                    return val
                return key
        return None

    @staticmethod
    def get_dictionary_key_secondsless(dictionary, timing):
        # The match_dt as received is not found in the dictionary, so further searching is required
        # First, searching starts by removing the seconds from the match_dt
        timing_secondsless = timing.replace(second=0, microsecond=0)
        # Now we build a dictionary that also has secondsless keys
        dictionary_secondsless_keys = \
            {key.replace(second=0, microsecond=0): value for key, value in dictionary.items()}
        # Now we attempt to match the secondsless key in the secondsless file_dict
        correct_key = FileHandler.get_dictionary_key(dictionary_secondsless_keys, timing_secondsless)
        if correct_key:
            # We have found the correct key for the match
            return correct_key
        return None

    @staticmethod
    def get_spawn_dictionary(data, file_name, match_dt, spawn_dt):
        """
        Function to get the data dictionary for a spawn based on a file name, match datetime and spawn datetime. Uses
        a lot of code to make the searching as reliable as possible.
        """
        print("Spawn data requested for:\n{}\n{}\n{}".format(file_name, match_dt, spawn_dt))
        # First check if the file_name is available
        if file_name not in data:
            return "Not available for this file.\n\nScreen parsing results are only available for spawns in files " \
                   "which were spawned while screen parsing was enabled and real-time parsing was running."
        try:
            file_dt = datetime.strptime(file_name[:-10], "combat_%Y-%m-%d_%H_%M_%S_")
        except ValueError:
            return "Not available for this file.\n\nScreen parsing results are not supported for file names which do " \
                   "not match the original Star Wars - The Old Republic CombatLog file name format."
        file_dict = data[file_name]
        # Next up comes the checking of datetimes, which is slightly more complicated due to the fact that even equal
        # datetime objects with the == operators, are not equal with the 'is' operator
        # Also, for backwards compatibility, different datetimes must be supported in this searching process
        # Datetimes always have a correct time, but the date is not always the same as the filename date
        # If this is the case, the date is actually set to January 1 1900, the datetime default
        # Otherwise the file name of the CombatLog must have been altered
        match_dict = None
        for key, value in file_dict.items():
            if key.hour == match_dt.hour and key.minute == match_dt.minute:
                match_dict = value
        if match_dict is None:
            return "Not available for this match\n\nScreen parsing results are only available for spawns " \
                   "in matches which were spawned while screen parsing was enabled and real-time parsing " \
                   "was running"
        # Now a similar process starts for the spawns, except that seconds matter here.
        spawn_dict = None
        for key, value in match_dict.items():
            if key is None:
                # If the key is None, something weird is going on, but we do not want to throw any data away
                # This may be caused by a bug in the ScreenParser
                # For now, we reset key to a sensible value, specifically the first moment the data was recorded, if
                # that's possible. If not, we'll skip it.
                try:
                    key = list(value[list(value.keys())[0]].keys())[0]
                except (KeyError, ValueError, IndexError):
                    continue
            if key.hour == spawn_dt.hour and key.minute == spawn_dt.minute and key.second == spawn_dt.second:
                spawn_dict = value
        if spawn_dict is None:
            return "Not available for this spawn\n\nScreen parsing results are not available for spawns which " \
                   "were not  spawned while screen parsing was enabled and real-time parsing were running."
        print("Retrieved data: {}".format(spawn_dict))
        return spawn_dict

    @staticmethod
    def get_data_dictionary(name="realtime.db"):
        file_name = os.path.join(get_temp_directory(), name)
        if not os.path.exists(file_name):
            return {}
        with open(file_name, "rb") as fi:
            data = pickle.load(fi)
        return data

    @staticmethod
    def get_markers(screen_dict, spawn_list):
        """
        Parse spawn screen data dictionary and spawn CombatLog data
        """
        results = {}
        start_time = Parser.line_to_dictionary(spawn_list[-1])["time"]
        results.update(FileHandler.get_weapon_markers(screen_dict, spawn_list))
        results.update(FileHandler.get_health_markers(screen_dict, start_time))
        results.update(FileHandler.get_tracking_markers(screen_dict))
        results.update(FileHandler.get_power_mgmt_markers(screen_dict, start_time))
        results.update(FileHandler.get_ability_markers(spawn_list, None))
        return results

    @staticmethod
    def get_spawn_stats(file_name, match_dt, spawn_dt):
        """
        Function to return the spawn statistics
        :param file_name:
        :param match_dt:
        :param spawn_dt:
        :return:
        """
        data = FileHandler.get_data_dictionary()
        value = FileHandler.get_spawn_dictionary(data, file_name, match_dt, spawn_dt)
        if isinstance(value, str):
            return value
        elif isinstance(value, dict):
            spawn_dicts = value
        else:
            raise ValueError("Returned value from get_spawn_dictionary is neither str nor dict")
        # Start calculations on this spawn data
        power_mgmt = {1: 0, 2: 0, 3: 0, 4: 0}
        for key, value in spawn_dicts["power_mgmt"].items():
            if not value:
                continue
            power_mgmt[value] += 1
        power_mgmt_max = max(power_mgmt.items(), key=operator.itemgetter(1))[0]
        tracking = 0
        amount = 0
        for key, value in spawn_dicts["tracking"].items():
            if not value:
                continue
            tracking += value
            amount += 1
        if amount == 0:
            tracking = "Not available for this spawn"
        else:
            tracking = tracking / amount
        total = (0, 0, 0)
        for key, value in spawn_dicts["health"].items():
            if not value:
                break
            total += value
        try:
            average_health = tuple(key / len(spawn_dicts["health"]) for key in total)
        except (ZeroDivisionError, TypeError):
            average_health = "Not available for this spawn"
        return FileHandler.get_formatted_stats_string(*(power_mgmt_max, tracking, average_health))

    @staticmethod
    def get_formatted_stats_string(*values):
        return """
        Most used power management: \t{0}
        Average tracking degrees: \t\t{1:.2f}
        Average ship health: \t\t{2}
        """.format(*values)

    @staticmethod
    def get_weapon_markers(dictionary, spawn):
        """
        Mouse button press intervals
        :param dictionary:
        :return: {"primaries": [(start, finish), ], "secondaries": ...}
        """
        player_list = Parser.get_player_id_list(spawn)
        if not isinstance(dictionary, dict):
            raise TypeError("Invalid argument received: {}".format(repr(dictionary)))
        clicks = dictionary["clicks"]
        buttons = {Button.left: None, Button.right: None}
        results = {"primaries": [], "secondaries": []}
        for time, (press, button) in sorted(clicks.items()):
            if not isinstance(time, datetime) or not isinstance(press, str):
                raise TypeError("Invalid types detected while parsing. time: {}, press: {}, button: {}".format(
                    repr(time), repr(press), repr(button)))
            press = "press" in press
            category = "primaries" if button == Button.left else ("secondaries" if button == Button.right else None)
            if category is None:
                continue
            if press is True:
                buttons[button] = time
            else:
                results[category].append(
                    ((category, buttons[button], time), {"background": FileHandler.click_colors[category]})
                )
        for line in spawn:
            if not isinstance(line, dict):
                line = Parser.line_to_dictionary(line)
            ability = line["ability"]
            if line["source"] == line["target"] or line["source"] not in player_list:
                continue
            if ability in abilities.primaries:
                category = "primaries"
            elif ability in abilities.secondaries:
                category = "secondaries"
            else:
                continue
            start = FileHandler.datetime_to_float(line["time"])
            args = (category, start, start + 1 / 60)
            results[category].append((args, {"background": FileHandler.colors[category]}))
        return results

    @staticmethod
    def get_health_markers(screen_dict, start_time):
        """
        Return health markers for TimeLine
        """
        sub_dict = screen_dict["health"]
        categories = ["hull", "shields_f", "shields_r"]
        health = {key: (None, None) for key in categories}
        results = {key: [] for key in categories}
        for time, (hull, shields_f, shields_r) in sorted(sub_dict.items()):
            new_values = {key: (time, locals()[key]) for key in categories}
            for category in categories:
                if health[category][1] != new_values[category][1]:
                    start = health[category][0]
                    start = start if start is not None else start_time
                    finish = time
                    args = (category, FileHandler.datetime_to_float(start), FileHandler.datetime_to_float(finish))
                    kwargs = {"background": FileHandler.health_colors[health[category][1]]}
                    results[category].append((args, kwargs))
        return results

    @staticmethod
    def get_power_mgmt_markers(screen_dict, start_time):
        categories = ["power_mgmt"]
        power_mgmt = (None, None)
        results = {key: [] for key in categories}
        sub_dict = screen_dict["keys"]
        if len(sub_dict) != 0:
            power_mode = 4
            previous = start_time
            for time, (key, pressed) in sorted(sub_dict.items()):
                pressed = "pressed" in pressed
                if pressed is False or key not in FileHandler.keys:
                    continue
                result = FileHandler.keys[key]
                if not isinstance(result, tuple) or len(result) != 2:
                    continue
                category, mode = result
                if power_mode == mode:
                    continue
                args = ("power_mgmt", previous, time)
                previous = time
                kwargs = {"background": FileHandler.power_mgmt_colors[power_mode]}
                power_mode = mode
                results["power_mgmt"].append((args, kwargs))
        else:
            sub_dict = screen_dict["power_mgmt"]
            for time, value in sorted(sub_dict.items()):
                if power_mgmt[0] != value:
                    start = power_mgmt[0]
                    start = start if start is not None else start_time
                    finish = time
                    args = ("power_mgmt", FileHandler.datetime_to_float(start), FileHandler.datetime_to_float(finish))
                    kwargs = {"background": FileHandler.power_mgmt_colors[value]}
                    results["power_mgmt"].append((args, kwargs))
                    power_mgmt = (time, value)
        return results

    @staticmethod
    def get_tracking_markers(screen_dict, max_firing_arc=40):
        sub = screen_dict["cursor_pos"]
        results = {"tracking": []}
        for key, value in sorted(sub.items()):
            degrees = get_tracking_degrees(get_distance_from_center(value))
            degrees = max(min(degrees, max_firing_arc), 1)
            start = FileHandler.datetime_to_float(key)
            finish = start + 0.01
            args = ("tracking", start, finish)
            background = FileHandler.color_html_to_tuple(FileHandler.colors["tracking"])
            background = FileHandler.color_darken(background, 1 / degrees)
            background = FileHandler.color_tuple_to_html(background)
            kwargs = {"background": background}
            results["tracking"].append((args, kwargs))
        return results

    @staticmethod
    def get_ability_markers(spawn_list, ship_statistics):
        """
        Parse a spawn list of lines and take the Engine, Shield, Systems and CoPilot ability activations and create
        markers for them to be put in the TimeLine.
        """
        # TODO: Use ship_statistics to create availability markers
        categories = ["engines", "shields", "copilot", "systems"]
        player_id_list = Parser.get_player_id_list(spawn_list)
        results = {key: [] for key in categories}
        for line in spawn_list:
            if not isinstance(line, dict):
                line = Parser.line_to_dictionary(line)
            ability = line["ability"]
            if (line["source"] != line["target"] or line["source"] not in player_id_list or
                    "AbilityActivate" not in line["effect"]):
                continue
            if ability in abilities.copilots:
                category = "copilot"
            elif ability in abilities.shields:
                category = "shields"
            elif ability in abilities.systems:
                category = "systems"
            elif ability in abilities.engines:
                category = "engines"
            else:
                continue
            start = FileHandler.datetime_to_float(line["time"])
            args = ("abilities", start, start + 1/60)
            kwargs = {"background": FileHandler.colors[category]}
            results[category].append((args, kwargs))
        return results

    @staticmethod
    def datetime_to_float(date_time_obj):
        """
        Convert a datetime object to a float value
        """
        if not isinstance(date_time_obj, datetime):
            raise TypeError("date_time_obj not of datetime type but {}".format(repr(date_time_obj)))
        return float(
            "{}.{}{}".format(date_time_obj.minute, (int((date_time_obj.second / 60) * 100)), date_time_obj.microsecond))

    @staticmethod
    def color_darken(rgb, factor):
        darkened = tuple(max(int(item * factor), 0) for item in rgb)
        print("Darkening {} to {} with factor {}".format(rgb, darkened, factor))
        return darkened

    @staticmethod
    def color_tuple_to_html(rgb):
        rgb = tuple(int(round(item)) for item in rgb)
        html = "#" + format(rgb[0] << 16 | rgb[1] << 8 | rgb[2], '06x')
        print("Converted {} to {}".format(rgb, html))
        return html

    @staticmethod
    def color_html_to_tuple(html):
        return tuple(int(html.replace("#", "")[i:i + 2], 16) for i in (0, 2, 4))
