/*
 * JACK Backend code for Carla
 * Copyright (C) 2011-2012 Filipe Coelho <falktx@gmail.com>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * For a full copy of the GNU General Public License see the COPYING file
 */

#include "carla_shared.h"

#include <QtCore/QMutex>
#include <QtCore/QString>

// Global variables (shared)
const char* unique_names[MAX_PLUGINS]  = { nullptr };
CarlaPlugin* CarlaPlugins[MAX_PLUGINS] = { nullptr };

volatile double ains_peak[MAX_PLUGINS*2]  = { 0.0 };
volatile double aouts_peak[MAX_PLUGINS*2] = { 0.0 };

// Global options
carla_options_t carla_options = {
    /* initiated */          false,
    #ifdef BUILD_BRIDGE
    /* global_jack_client */ false,
    /* use_dssi_chunks    */ false,
    /* prefer_ui_bridges  */ false,
    #else
    /* global_jack_client */ true,
    /* use_dssi_chunks    */ false,
    /* prefer_ui_bridges  */ true,
    #endif
    /* bridge_unix32 */ nullptr,
    /* bridge_unix64 */ nullptr,
    /* bridge_win32  */ nullptr,
    /* bridge_win64  */ nullptr
};

CallbackFunc Callback  = nullptr;
const char* last_error = nullptr;

QMutex carla_proc_lock_var;
QMutex carla_midi_lock_var;

const unsigned short max_client_name_size = 32 - 5; // 32 = jack1 max name; 5 = strlen(" (10)")

// -------------------------------------------------------------------------------------------------------------------
// Exported symbols (API)

void set_callback_function(CallbackFunc func)
{
    qDebug("set_callback_function(%p)", func);
    Callback = func;
}

const char* get_last_error()
{
    qDebug("get_last_error()");
    return last_error;
}

// End of exported symbols (API)
// -------------------------------------------------------------------------------------------------------------------

const char* bool2str(bool yesno)
{
    if (yesno)
        return "true";
    else
        return "false";
}

const char* binarytype2str(BinaryType type)
{
    switch (type)
    {
    case BINARY_UNIX32:
        return carla_options.bridge_unix32;
    case BINARY_UNIX64:
        return carla_options.bridge_unix64;
    case BINARY_WIN32:
        return carla_options.bridge_win32;
    case BINARY_WIN64:
        return carla_options.bridge_win64;
    default:
        return nullptr;
    }
}

const char* plugintype2str(PluginType type)
{
    switch (type)
    {
    case PLUGIN_LADSPA:
        return "LADSPA";
    case PLUGIN_DSSI:
        return "DSSI";
    case PLUGIN_LV2:
        return "LV2";
    case PLUGIN_VST:
        return "VST";
    case PLUGIN_SF2:
        return "SF2";
    default:
        return "Unknown";
    }
}

// -------------------------------------------------------------------------------------------------------------------

short get_new_plugin_id()
{
    for (unsigned short i=0; i<MAX_PLUGINS; i++)
    {
        if (CarlaPlugins[i] == nullptr)
            return i;
    }

    return -1;
}

const char* get_unique_name(const char* name)
{
    QString qname(name);

    if (qname.isEmpty())
        qname = "(No name)";

    qname.truncate(max_client_name_size);
    //qname.replace(":", "."); // ":" is used in JACK to split client/port names

    for (unsigned short i=0; i<MAX_PLUGINS; i++)
    {
        // Check if unique name already exists
        if (unique_names[i] && qname == unique_names[i])
        {
            // Check if string has already been modified
            uint len = qname.size();

            if (qname.at(len-3) == QChar('(') && qname.at(len-2).isDigit() && qname.at(len-1) == QChar(')'))
            {
                int number = qname.at(len-2).toAscii()-'0';

                if (number == 9)
                    // next number is 10, 2 digits
                    qname.replace(" (9)", " (10)");
                else
                    qname[len-2] = QChar('0'+number+1);

                continue;
            }
            else if (qname.at(len-4) == QChar('(') && qname.at(len-3).isDigit() && qname.at(len-2).isDigit() && qname.at(len-1) == QChar(')'))
            {
                QChar n2 = qname.at(len-2);
                QChar n3 = qname.at(len-3);

                if (n2 == QChar('9'))
                {
                    n2 = QChar('0');
                    n3 = QChar(n3.toAscii()+1);
                }
                else
                    n2 = QChar(n2.toAscii()+1);

                qname[len-2] = n2;
                qname[len-3] = n3;

                continue;
            }

            // Modify string if not
            qname += " (2)";
        }
    }

    return strdup(qname.toUtf8().constData());
}

void* get_pointer(intptr_t ptr_addr)
{
    intptr_t* ptr = (intptr_t*)ptr_addr;
    return (void*)ptr;
}

void set_last_error(const char* error)
{
    if (last_error)
        free((void*)last_error);

    if (error)
        last_error = strdup(error);
    else
        last_error = nullptr;
}

void carla_proc_lock()
{
    carla_proc_lock_var.lock();
}

void carla_proc_unlock()
{
    carla_proc_lock_var.unlock();
}

void carla_midi_lock()
{
    carla_midi_lock_var.lock();
}

void carla_midi_unlock()
{
    carla_midi_lock_var.unlock();
}

void callback_action(CallbackType action, unsigned short plugin_id, int value1, int value2, double value3)
{
    if (Callback)
        Callback(action, plugin_id, value1, value2, value3);
}