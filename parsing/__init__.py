"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
from parsing.characters import CharacterDatabase
from parsing.filehandler import FileHandler
from parsing.filestats import file_statistics
from parsing.folderstats import folder_statistics
from parsing.gsfinterface import GSFInterface
from parsing.guiparsing import GUIParser, get_gui_profiles, get_player_guiname
from parsing.imageops import get_brightest_pixel, get_similarity, get_similarity_pixels
from parsing.logstalker import LogStalker
from parsing.matchstats import match_statistics
from parsing.parser import Parser
from parsing.patterns import Patterns
from parsing.realtime import RealTimeParser
from parsing.shipops import get_ship_from_lineup, get_time_to_kill, get_time_to_kill_stats
from parsing.ships import Ship, Component
from parsing.spawnstats import spawn_statistics
from parsing.strategies import Strategy, StrategyDatabase, Phase
from parsing.vision import *
