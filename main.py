﻿"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from os.path import dirname, join, basename, exists
import sys
import shutil
import platform
# Packages
from raven import Client as RavenClient
# UI Libraries
from tkinter import messagebox


def handle_exception(raven: RavenClient):
    """Handle an occurred exception"""
    if not exists("development"):
        try:
            from settings import Settings
            Settings().write_defaults()
            written = True
        except Exception:
            written = False
    else:
        written = False
    raven.captureException()
    messagebox.showerror(
        "Error", "Window initialization failed. The error has been "
                 "reported. {}".format(
            "Settings have been reset to defaults." if written is True else ""))


def create_window():
    """
    Attempt to create a new MainWindow and provide error handling and
    user interaction for when an error occurs which causes the
    window creation to fail.
    """
    try:
        raven = connect_to_sentry()
    except Exception:
        messagebox.showerror(
            "Error", "The GSF Parser failed to connect to the error "
                     "reporting service.")
        raise
    try:
        import gui
        main_window = gui.MainWindow(raven)
    except Exception:
        if exists("development"):
            raise
        handle_exception(raven)
        raise
    try:
        main_window.mainloop()
    except KeyboardInterrupt:
        main_window.exit()


def connect_to_sentry() -> RavenClient:
    """Connect to Sentry and enable sys hook for pyinstaller failures"""
    with open("sentry") as fi:
        link = fi.read().strip()
    raven = RavenClient(link)
    raven.install_sys_hook()
    return raven


def setup_tkinter():
    """Fixes bug in PyInstaller, see issue #17"""
    if "Windows-7" not in platform.platform():
        return
    try:
        tcl_lib = join(sys._MEIPASS, "lib")
        tcl_new_lib = join(dirname(dirname(tcl_lib)), basename(tcl_lib))
        shutil.copytree(src=tcl_lib, dst=tcl_new_lib)
    except (AttributeError, FileNotFoundError, FileExistsError):
        pass
    return


if __name__ == '__main__':
    setup_tkinter()
    create_window()
