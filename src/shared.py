#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Common/Shared code
# Copyright (C) 2010-2013 Filipe Coelho <falktx@falktx.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# For a full copy of the GNU General Public License see the COPYING file

# ------------------------------------------------------------------------------------------------------------
# Imports (Global)

import os
import sys
from codecs import open as codecopen
from unicodedata import normalize
from PyQt4.QtCore import qWarning, SIGNAL, SLOT, qDir
from PyQt4.QtGui import QApplication, QFileDialog, QIcon, QMessageBox

# ------------------------------------------------------------------------------------------------------------
# Set Platform

if sys.platform == "darwin":
    from PyQt4.QtGui import qt_mac_set_menubar_icons
    qt_mac_set_menubar_icons(False)
    HAIKU   = False
    LINUX   = False
    MACOS   = True
    WINDOWS = False
elif "haiku" in sys.platform:
    HAIKU   = True
    LINUX   = False
    MACOS   = False
    WINDOWS = False
elif "linux" in sys.platform:
    HAIKU   = False
    LINUX   = True
    MACOS   = False
    WINDOWS = False
elif sys.platform in ("win32", "win64", "cygwin"):
    WINDIR  = os.getenv("WINDIR")
    HAIKU   = False
    LINUX   = False
    MACOS   = False
    WINDOWS = True
else:
    HAIKU   = False
    LINUX   = False
    MACOS   = False
    WINDOWS = False

# ------------------------------------------------------------------------------------------------------------
# Try Import Signal

try:
    from signal import signal, SIGINT, SIGTERM, SIGUSR1, SIGUSR2
    haveSignal = True
except:
    haveSignal = False

# ------------------------------------------------------------------------------------------------------------
# Set Version

VERSION = "0.8.1"

# ------------------------------------------------------------------------------------------------------------
# Set Debug mode

DEBUG = bool("-d" in sys.argv or "-debug" in sys.argv or "--debug" in sys.argv)

# ------------------------------------------------------------------------------------------------------------
# Global variables

global gGui
gGui = None

# ------------------------------------------------------------------------------------------------------------
# Set directory for temporary files

if WINDOWS:
    envTMP = os.getenv("TMP")
else:
    # POSIX.1-2008: Linux, Mac OS X, BSD, ..
    envTMP = os.getenv("TMPDIR")

if envTMP is None:
    qWarning("TMP(DIR) variable not set, using Qt.tempPath")
    TMP = QDir.tempPath()
else:
    TMP = envTMP

del envTMP

if not os.path.exists(TMP):
    qWarning("TMP(DIR) does not exist, using Qt.tempPath")
    TMP = QDir.tempPath()

# ------------------------------------------------------------------------------------------------------------
# Set HOME

HOME = os.getenv("HOME")

if HOME is None:
    HOME = os.path.expanduser("~")

    if not WINDOWS:
        qWarning("HOME variable not set")

if not os.path.exists(HOME):
    qWarning("HOME does not exist")
    HOME = TMP

# ------------------------------------------------------------------------------------------------------------
# Set PATH

PATH = os.getenv("PATH")

if PATH is None:
    qWarning("PATH variable not set")

    if MACOS:
        PATH = ("/opt/local/bin", "/usr/local/bin", "/usr/bin", "/bin")
    elif WINDOWS:
        PATH = (os.path.join(WINDIR, "system32"), WINDIR)
    else:
        PATH = ("/usr/local/bin", "/usr/bin", "/bin")

else:
    PATH = PATH.split(os.pathsep)

# ------------------------------------------------------------------------------------------------------------
# User environment LADSPA plugin paths

ENV_LADSPA_PATH = os.getenv("LADSPA_PATH")

if ENV_LADSPA_PATH is None:
    qWarning("LADSPA_PATH not set, using default.")
else:
    ENV_LADSPA_PATH = ENV_LADSPA_PATH.split(os.pathsep)

# ------------------------------------------------------------------------------------------------------------
# User environment DSSI plugin paths

ENV_DSSI_PATH = os.getenv("DSSI_PATH")

if ENV_DSSI_PATH is None:
    qWarning("DSSI_PATH not set, using default.")
else:
    ENV_DSSI_PATH = ENV_DSSI_PATH.split(os.pathsep)

# ------------------------------------------------------------------------------------------------------------
# User environment LV2 plugin paths

ENV_LV2_PATH = os.getenv("LV2_PATH")

if ENV_LV2_PATH is None:
    qWarning("LV2_PATH not set, using default.")
else:
    ENV_LV2_PATH = ENV_LV2_PATH.split(os.pathsep)

# ------------------------------------------------------------------------------------------------------------
# User environment VST plugin paths

ENV_VST_PATH = os.getenv("VST_PATH")

if ENV_VST_PATH is None:
    qWarning("VST_PATH not set, using default.")
else:
    ENV_VST_PATH = ENV_VST_PATH.split(os.pathsep)

# ------------------------------------------------------------------------------------------------------------
# Remove/convert non-ascii chars from a string

def asciiString(string):
    return normalize("NFKD", string).encode("ascii", "ignore").decode("utf-8")

# ------------------------------------------------------------------------------------------------------------
# Convert a ctypes c_char_p into a python string

def cString(value):
    if not value:
        return ""
    if isinstance(value, str):
        return value
    return value.decode("utf-8", errors="ignore")

# ------------------------------------------------------------------------------------------------------------
# Check if a value is a number (float support)

def isNumber(value):
    try:
        float(value)
        return True
    except:
        return False

# ------------------------------------------------------------------------------------------------------------
# Convert a value to a list

def toList(value):
    if value is None:
        return []
    elif not isinstance(value, list):
        return [value]
    else:
        return value

# ------------------------------------------------------------------------------------------------------------
# Unicode open

def uopen(filename, mode="r"):
    return codecopen(filename, encoding="utf-8", mode=mode)

# ------------------------------------------------------------------------------------------------------------
# QLineEdit and QPushButton combo

def getAndSetPath(self_, currentPath, lineEdit):
    newPath = QFileDialog.getExistingDirectory(self_, self_.tr("Set Path"), currentPath, QFileDialog.ShowDirsOnly)
    if newPath:
        lineEdit.setText(newPath)
    return newPath

# ------------------------------------------------------------------------------------------------------------
# Get Icon from user theme, using our own as backup (Oxygen)

def getIcon(icon, size=16):
    return QIcon.fromTheme(icon, QIcon(":/%ix%i/%s.png" % (size, size, icon)))

# ------------------------------------------------------------------------------------------------------------
# Custom MessageBox

def CustomMessageBox(self_, icon, title, text, extraText="", buttons=QMessageBox.Yes|QMessageBox.No, defButton=QMessageBox.No):
    msgBox = QMessageBox(self_)
    msgBox.setIcon(icon)
    msgBox.setWindowTitle(title)
    msgBox.setText(text)
    msgBox.setInformativeText(extraText)
    msgBox.setStandardButtons(buttons)
    msgBox.setDefaultButton(defButton)
    return msgBox.exec_()

# ------------------------------------------------------------------------------------------------------------
# Signal handler

def setUpSignals(self_):
    global gGui

    if gGui is None:
        gGui = self_

    if not haveSignal:
        return

    signal(SIGINT,  signalHandler)
    signal(SIGTERM, signalHandler)
    signal(SIGUSR1, signalHandler)
    signal(SIGUSR2, signalHandler)

    gGui.connect(gGui, SIGNAL("SIGTERM()"), closeWindowHandler)
    gGui.connect(gGui, SIGNAL("SIGUSR2()"), showWindowHandler)

def signalHandler(sig, frame):
    global gGui

    if gGui is None:
        return

    if sig in (SIGINT, SIGTERM):
        gGui.emit(SIGNAL("SIGTERM()"))
    elif sig == SIGUSR1:
        gGui.emit(SIGNAL("SIGUSR1()"))
    elif sig == SIGUSR2:
        gGui.emit(SIGNAL("SIGUSR2()"))

def closeWindowHandler():
    global gGui

    if gGui is None:
        return

    gGui.hide()
    gGui.close()
    QApplication.instance().quit()

    gGui = None

def showWindowHandler():
    global gGui

    if gGui is None:
        return

    if gGui.isMaximized():
        gGui.showMaximized()
    else:
        gGui.showNormal()

# ------------------------------------------------------------------------------------------------------------
# Shared Icons

def setIcons(self_, modes):
    global gGui

    if gGui is None:
        gGui = self_

    if "canvas" in modes:
        gGui.ui.act_canvas_arrange.setIcon(getIcon("view-sort-ascending"))
        gGui.ui.act_canvas_refresh.setIcon(getIcon("view-refresh"))
        gGui.ui.act_canvas_zoom_fit.setIcon(getIcon("zoom-fit-best"))
        gGui.ui.act_canvas_zoom_in.setIcon(getIcon("zoom-in"))
        gGui.ui.act_canvas_zoom_out.setIcon(getIcon("zoom-out"))
        gGui.ui.act_canvas_zoom_100.setIcon(getIcon("zoom-original"))
        gGui.ui.act_canvas_print.setIcon(getIcon("document-print"))
        gGui.ui.b_canvas_zoom_fit.setIcon(getIcon("zoom-fit-best"))
        gGui.ui.b_canvas_zoom_in.setIcon(getIcon("zoom-in"))
        gGui.ui.b_canvas_zoom_out.setIcon(getIcon("zoom-out"))
        gGui.ui.b_canvas_zoom_100.setIcon(getIcon("zoom-original"))

    if "jack" in modes:
        gGui.ui.act_jack_clear_xruns.setIcon(getIcon("edit-clear"))
        gGui.ui.act_jack_configure.setIcon(getIcon("configure"))
        gGui.ui.act_jack_render.setIcon(getIcon("media-record"))
        gGui.ui.b_jack_clear_xruns.setIcon(getIcon("edit-clear"))
        gGui.ui.b_jack_configure.setIcon(getIcon("configure"))
        gGui.ui.b_jack_render.setIcon(getIcon("media-record"))

    if "transport" in modes:
        gGui.ui.act_transport_play.setIcon(getIcon("media-playback-start"))
        gGui.ui.act_transport_stop.setIcon(getIcon("media-playback-stop"))
        gGui.ui.act_transport_backwards.setIcon(getIcon("media-seek-backward"))
        gGui.ui.act_transport_forwards.setIcon(getIcon("media-seek-forward"))
        gGui.ui.b_transport_play.setIcon(getIcon("media-playback-start"))
        gGui.ui.b_transport_stop.setIcon(getIcon("media-playback-stop"))
        gGui.ui.b_transport_backwards.setIcon(getIcon("media-seek-backward"))
        gGui.ui.b_transport_forwards.setIcon(getIcon("media-seek-forward"))

    if "misc" in modes:
        gGui.ui.act_quit.setIcon(getIcon("application-exit"))
        gGui.ui.act_configure.setIcon(getIcon("configure"))
