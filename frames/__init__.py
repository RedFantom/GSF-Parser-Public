"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE.md
Copyright (C) 2016-2018 RedFantom
"""
from frames.builds import BuildsFrame
from frames.characters import CharactersFrame
from frames.chat import ChatFrame
from frames.realtime import RealTimeFrame
from frames.settings import SettingsFrame
from frames.ship import ShipFrame
from frames.shipstats import ShipStatsFrame
from frames.stats import StatsFrame
from frames.strategies import StrategiesFrame
from frames.tools import ToolsFrame

import variables
if variables.settings["gui"]["fileframe"]:
    from frames.file import FileFrame
else:
    from widgets.results.fileframe import FileFrame
