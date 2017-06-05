# Written by RedFantom, Wing Commander of Thranta Squadron,
# Daethyra, Squadron Leader of Thranta Squadron and Sprigellania, Ace of Thranta Squadron
# Thranta Squadron GSF CombatLog Parser, Copyright (C) 2016 by RedFantom, Daethyra and Sprigellania
# All additions are under the copyright of their respective authors
# For license see LICENSE

# UI imports
import decimal
from . import parse
from parsing import abilities


def file_statistics(file_cube):
    """
     Puts the statistics found in a file_cube from parse.splitter() into a
     format that is usable by the file_frame to display them to the user
     :param file_cube: An already split file into a file_cube
     :return: abilities_string, a string for in the abilities tab
              statistics_string, a string for in the statistics label in the
                                 statistics tab
              total_shipsdict, a dictionary with ships as keys and the amount
                               of times they occurred as values
              total_enemies, a list of all enemies encountered in the whole
                             folder
              total_enemydamaged, a dictionary with the enemies as keys and
                                  their respective damage taken from you as
                                  values
              total_enemydamaget, a dictionary with the enemies as keys and
                                  their respective damage dealt to you as
                                  values
              uncounted, the amount of ships that was not counted in the
                         total_shipsdict, if there was more than one
                         possibility
    """
    lines = []
    for match in file_cube:
        for spawn in match:
            for line in spawn:
                lines.append(line)
    player_list = parse.determinePlayer(lines)
    _, match_timings, spawn_timings = parse.splitter(lines, player_list)

    (abs, damagetaken, damagedealt, selfdamage, healingreceived, enemies, criticalcount, criticalluck,
     hitcount, enemydamaged, enemydamaget, match_timings, spawn_timings) = \
        parse.parse_file(file_cube, player_list, match_timings, spawn_timings)
    total_abilities = {}
    total_damagetaken = 0
    total_damagedealt = 0
    total_selfdamage = 0
    total_healingrecv = 0
    total_enemies = []
    total_criticalcount = 0
    total_hitcount = 0

    for mat in abs:
        for dic in mat:
            for (key, value) in dic.items():
                if key not in total_abilities:
                    total_abilities[key] = value
                else:
                    total_abilities[key] += value
    for lst in damagetaken:
        for amount in lst:
            total_damagetaken += amount
    for lst in damagedealt:
        for amount in lst:
            total_damagedealt += amount
    for lst in selfdamage:
        for amount in lst:
            total_selfdamage += amount
    for lst in healingreceived:
        for amount in lst:
            total_healingrecv += amount
    for matrix in enemies:
        for lst in matrix:
            for enemy in lst:
                if enemy not in total_enemies:
                    total_enemies.append(enemy)
    for lst in criticalcount:
        for amount in lst:
            total_criticalcount += amount
    for lst in hitcount:
        for amount in lst:
            total_hitcount += amount
    try:
        total_criticalluck = decimal.Decimal(float(total_criticalcount / total_hitcount))
    except ZeroDivisionError:
        total_criticalluck = 0
    total_enemydamaged = enemydamaged
    total_enemydamaget = enemydamaget
    total_shipsdict = {}
    uncounted = 0
    for ship in abilities.ships:
        total_shipsdict[ship] = 0
    for match in file_cube:
        for spawn in match:
            ships_possible = parse.parse_spawn(spawn, player_list)[9]
            if len(ships_possible) == 1:
                if ships_possible[0] == "Razorwire":
                    total_shipsdict["Razorwire"] += 1
                elif ships_possible[0] == "Legion":
                    total_shipsdict["Legion"] += 1
                elif ships_possible[0] == "Decimus":
                    total_shipsdict["Decimus"] += 1
                elif ships_possible[0] == "Bloodmark":
                    total_shipsdict["Bloodmark"] += 1
                elif ships_possible[0] == "Sting":
                    total_shipsdict["Sting"] += 1
                elif ships_possible[0] == "Blackbolt":
                    total_shipsdict["Blackbolt"] += 1
                elif ships_possible[0] == "Mangler":
                    total_shipsdict["Mangler"] += 1
                elif ships_possible[0] == "Dustmaker":
                    total_shipsdict["Dustmaker"] += 1
                elif ships_possible[0] == "Jurgoran":
                    total_shipsdict["Jurgoran"] += 1
                elif ships_possible[0] == "Imperium":
                    total_shipsdict["Imperium"] += 1
                elif ships_possible[0] == "Quell":
                    total_shipsdict["Quell"] += 1
                elif ships_possible[0] == "Rycer":
                    total_shipsdict["Rycer"] += 1
            else:
                uncounted += 1
    total_killsassists = 0
    for enemy in total_enemies:
        if total_enemydamaget[enemy] > 0:
            total_killsassists += 1
    total_criticalluck = round(total_criticalluck * 100, 2)
    deaths = 0
    for match in file_cube:
        deaths += len(match)
    try:
        damage_ratio_string = str(
            str(round(float(total_damagedealt) / float(total_damagetaken), 1)) + " : 1") + "\n"
    except ZeroDivisionError:
        damage_ratio_string = "0.0 : 1\n"
    statistics_string = (
        str(total_killsassists) + " enemies" + "\n" + str(total_damagedealt) + "\n" +
        str(total_damagetaken) + "\n" + damage_ratio_string + str(total_selfdamage) + "\n" +
        str(total_healingrecv) + "\n" + str(total_hitcount) + "\n" +
        str(total_criticalcount) + "\n" + str(total_criticalluck) + "%" +
        "\n" + str(deaths) + "\n-\n-")
    return (total_abilities, statistics_string, total_shipsdict, total_enemies, total_enemydamaged,
            total_enemydamaget, uncounted)
