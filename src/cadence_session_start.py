#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Imports (Global)
import dbus, sys
from PyQt4.QtCore import QCoreApplication

# Imports (Custom Stuff)
from shared_cadence import *

# Cadence Global Settings
GlobalSettings = QSettings("Cadence", "GlobalSettings")

# DBus
class DBus(object):
    __slots__ = [
      'bus',
      'a2j',
      'jack'
    ]
DBus = DBus()

def forceReset():
    # Kill all audio processes
    stopAllAudioProcesses()

    # Remove configs
    configFiles = (
        # Cadence GlobalSettings
        os.path.join(HOME, ".asoundrc"),
        # ALSA settings
        os.path.join(HOME, ".config", "Cadence", "GlobalSettings.conf"),
        # JACK2 settings
        os.path.join(HOME, ".config", "jack", "conf.xml"),
        # JACK1 settings
        os.path.join(HOME, ".config", "jack", "conf-jack1.xml")
    )

    for config in configFiles:
        if os.path.exists(config):
            os.remove(config)

# Start JACK, A2J and Pulse, according to user settings
def startSession(systemStarted, secondSystemStartAttempt):
    # Check if JACK is set to auto-start
    if systemStarted and not GlobalSettings.value("JACK/AutoStart", False, type=bool):
        print("JACK is set to NOT auto-start on login")
        return True

    # Called via autostart desktop file
    if systemStarted and secondSystemStartAttempt:
        tmp_bus  = dbus.SessionBus()
        tmp_jack = tmp_bus.get_object("org.jackaudio.service", "/org/jackaudio/Controller")
        started  = bool(tmp_jack.IsStarted())

        # Cleanup
        del tmp_bus, tmp_jack

        # If already started, do nothing
        if started:
            return True

    # Kill all audio processes first
    stopAllAudioProcesses()

    # Connect to DBus
    DBus.bus  = dbus.SessionBus()
    DBus.jack = DBus.bus.get_object("org.jackaudio.service", "/org/jackaudio/Controller")

    try:
        DBus.a2j = dbus.Interface(DBus.bus.get_object("org.gna.home.a2jmidid", "/"), "org.gna.home.a2jmidid.control")
    except:
        DBus.a2j = None

    if GlobalSettings.value("JACK/AutoLoadLadishStudio", False, type=bool):
        try:
            ladish_control = DBus.bus.get_object("org.ladish", "/org/ladish/Control")
        except:
            startJack()
            return False

        try:
            ladish_conf = DBus.bus.get_object("org.ladish.conf", "/org/ladish/conf")
        except:
            ladish_conf = None

        ladishStudioName = dbus.String(GlobalSettings.value("JACK/LadishStudioName", "", type=str))
        ladishStudioListDump = ladish_control.GetStudioList()

        for thisStudioName, thisStudioDict in ladishStudioListDump:
            if ladishStudioName == thisStudioName:
                try:
                    if ladish_conf and ladish_conf.get('/org/ladish/daemon/notify')[0] == "true":
                        ladish_conf.set('/org/ladish/daemon/notify', "false")
                        ladishNotifyHack = True
                    else:
                      ladishNotifyHack = False
                except:
                    ladishNotifyHack = False

                ladish_control.LoadStudio(thisStudioName)
                ladish_studio = DBus.bus.get_object("org.ladish", "/org/ladish/Studio")

                if not bool(ladish_studio.IsStarted()):
                    ladish_studio.Start()

                if ladishNotifyHack:
                    ladish_conf.set('/org/ladish/daemon/notify', "true")

                break

        else:
            startJack()

    else:
        startJack()

    if not bool(DBus.jack.IsStarted()):
        print("JACK Failed to Start")
        return False

    # Start bridges according to user settings

    # ALSA-Audio
    if GlobalSettings.value("ALSA-Audio/BridgeIndexType", iAlsaFileNone, type=int) == iAlsaFileLoop:
        startAlsaAudioLoopBridge()
        sleep(0.5)

    # ALSA-MIDI
    if GlobalSettings.value("A2J/AutoStart", True, type=bool) and DBus.a2j and not bool(DBus.a2j.is_started()):
        a2jExportHW = GlobalSettings.value("A2J/ExportHW", True, type=bool)
        DBus.a2j.set_hw_export(a2jExportHW)
        DBus.a2j.start()

    # PulseAudio
    if GlobalSettings.value("Pulse2JACK/AutoStart", True, type=bool):
        if GlobalSettings.value("Pulse2JACK/PlaybackModeOnly", False, type=bool):
            os.system("cadence-pulse2jack -p")
        else:
            os.system("cadence-pulse2jack")

    print("JACK Started Successfully")
    return True

def startJack():
    if not bool(DBus.jack.IsStarted()):
        DBus.jack.StartServer()

def printLADSPA_PATH():
    EXTRA_LADSPA_DIRS = GlobalSettings.value("AudioPlugins/EXTRA_LADSPA_PATH", "", type=str).split(":")
    LADSPA_PATH_str   = ":".join(DEFAULT_LADSPA_PATH)

    for i in range(len(EXTRA_LADSPA_DIRS)):
        if EXTRA_LADSPA_DIRS[i]:
            LADSPA_PATH_str += ":"+EXTRA_LADSPA_DIRS[i]

    print(LADSPA_PATH_str)

def printDSSI_PATH():
    EXTRA_DSSI_DIRS = GlobalSettings.value("AudioPlugins/EXTRA_DSSI_PATH", "", type=str).split(":")
    DSSI_PATH_str   = ":".join(DEFAULT_DSSI_PATH)

    for i in range(len(EXTRA_DSSI_DIRS)):
        if EXTRA_DSSI_DIRS[i]:
            DSSI_PATH_str += ":"+EXTRA_DSSI_DIRS[i]

    print(DSSI_PATH_str)

def printLV2_PATH():
    EXTRA_LV2_DIRS = GlobalSettings.value("AudioPlugins/EXTRA_LV2_PATH", "", type=str).split(":")
    LV2_PATH_str   = ":".join(DEFAULT_LV2_PATH)

    for i in range(len(EXTRA_LV2_DIRS)):
        if EXTRA_LV2_DIRS[i]:
            LV2_PATH_str += ":"+EXTRA_LV2_DIRS[i]

    print(LV2_PATH_str)

def printVST_PATH():
    EXTRA_VST_DIRS = GlobalSettings.value("AudioPlugins/EXTRA_VST_PATH", "", type=str).split(":")
    VST_PATH_str   = ":".join(DEFAULT_VST_PATH)

    for i in range(len(EXTRA_VST_DIRS)):
      if EXTRA_VST_DIRS[i]:
        VST_PATH_str += ":"+EXTRA_VST_DIRS[i]

    print(VST_PATH_str)

def printVST3_PATH():
    EXTRA_VST3_DIRS = GlobalSettings.value("AudioPlugins/EXTRA_VST3_PATH", "", type=str).split(":")
    VST3_PATH_str   = ":".join(DEFAULT_VST3_PATH)

    for i in range(len(EXTRA_VST3_DIRS)):
      if EXTRA_VST3_DIRS[i]:
        VST3_PATH_str += ":"+EXTRA_VST3_DIRS[i]

    print(VST3_PATH_str)

def printGIG_PATH():
    EXTRA_GIG_DIRS = GlobalSettings.value("AudioPlugins/EXTRA_GIG_PATH", "", type=str).split(":")
    GIG_PATH_str   = ":".join(DEFAULT_GIG_PATH)

    for i in range(len(EXTRA_GIG_DIRS)):
      if EXTRA_GIG_DIRS[i]:
        GIG_PATH_str += ":"+EXTRA_GIG_DIRS[i]

    print(GIG_PATH_str)

def printSF2_PATH():
    EXTRA_SF2_DIRS = GlobalSettings.value("AudioPlugins/EXTRA_SF2_PATH", "", type=str).split(":")
    SF2_PATH_str   = ":".join(DEFAULT_SF2_PATH)

    for i in range(len(EXTRA_SF2_DIRS)):
      if EXTRA_SF2_DIRS[i]:
        SF2_PATH_str += ":"+EXTRA_SF2_DIRS[i]

    print(SF2_PATH_str)

def printSFZ_PATH():
    EXTRA_SFZ_DIRS = GlobalSettings.value("AudioPlugins/EXTRA_SFZ_PATH", "", type=str).split(":")
    SFZ_PATH_str   = ":".join(DEFAULT_SFZ_PATH)

    for i in range(len(EXTRA_SFZ_DIRS)):
      if EXTRA_SFZ_DIRS[i]:
        SFZ_PATH_str += ":"+EXTRA_SFZ_DIRS[i]

    print(SFZ_PATH_str)

def printArguments():
    print(" -s, --start           \tUsed when started from user's desktop menu")
    print(" --reset, --force-reset\tForce-reset all JACK daemons and settings")
    print("                       \t(including removal of auto-start at login)")
    print("")
    print(" -h, --help            \tShow this help message")
    print(" -v, --version         \tShow version")
    print("")
    print("Options for system services:")
    print(" --system-start        \tUsed for auto-start by graphical display manager,")
    print("                       \thandling of D-Bus, a2jmidi, JACK, Ladish, etc.\n")
    print(" --system-start-desktop\tUsed for auto-start by X-Desktop session manager,")
    print("                       \thandling of a2jmidi, JACK, Ladish, etc.")
    print("\nOptions for applications, etc.:")
    print(" --printLADSPA_PATH    \tPrints value of LADSPA_PATH, to find LADSPA plugins")
    print(" --printDSSI_PATH      \tPrints value of DSSI_PATH, to find DSSI plugins")
    print(" --printLV2_PATH       \tPrints value of LV2_PATH, to find LV2 plugins")
    print(" --printVST_PATH       \tPrints value of VST_PATH, to find VST plugins")
    print(" --printVST3_PATH      \tPrints value of VST3_PATH, to find VST3 plugins")
    print(" --printGIG_PATH       \tPrints value of GIG_PATH, to find GIG samples")
    print(" --printSF2_PATH       \tPrints value of SF2_PATH, to find SF2 soundfonts")
    print(" --printSFZ_PATH       \tPrints value of SFZ_PATH, to find SFZ soundfonts")

def printError(cmd):
    print("Invalid arguments")
    print("Run '%s -h' for help" % (cmd))

def printHelp(cmd):
    print("Usage: %s [cmd]" % (cmd))
    printArguments()

def printVersion():
    print("Cadence version %s" % (VERSION))
    print("Developed by falkTX and the rest of the KXStudio Team")

#--------------- main ------------------
if __name__ == '__main__':
    # App initialization
    app = QCoreApplication(sys.argv)
    app.setApplicationName("Cadence")
    app.setApplicationVersion(VERSION)
    app.setOrganizationName("Cadence")

    # Check arguments
    cmd = sys.argv[0]

    if len(app.arguments()) == 1:
        printHelp(cmd)
    elif len(app.arguments()) == 2:
        arg = app.arguments()[1]
        if arg == "--printLADSPA_PATH":
            printLADSPA_PATH()
        elif arg == "--printDSSI_PATH":
            printDSSI_PATH()
        elif arg == "--printLV2_PATH":
            printLV2_PATH()
        elif arg == "--printVST_PATH":
            printVST_PATH()
        elif arg == "--printVST3_PATH":
            printVST3_PATH()
        elif arg == "--printGIG_PATH":
            printSF2_PATH()
        elif arg == "--printSF2_PATH":
            printSFZ_PATH()
        elif arg == "--printSFZ_PATH":
            printVST_PATH()
        elif arg == "--reset":
            forceReset()
        elif arg in ("--system-start", "--system-start-desktop"):
            sys.exit(startSession(True, arg == "--system-start-desktop"))
        elif arg in ("-s", "--s", "-start", "--start"):
            sys.exit(startSession(False, False))
        elif arg in ("-h", "--h", "-help", "--help"):
            printHelp(cmd)
        elif arg in ("-v", "--v", "-version", "--version"):
            printVersion()
        else:
            printError(cmd)
    else:
        printError(cmd)

    # Exit
    sys.exit(0)
