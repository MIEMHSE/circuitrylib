#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2013, The Profitware Group'

import inspect
import os

from circuitry.adapters import AbstractAdapter
from circuitry.devices import Device


def get_python_libraries(circuitry_dirname, essence_dirname, essence_root):
    """Walk through directories and find files to import"""
    import_list = list()
    for current_dir, dirs, files in os.walk(essence_root):
        current_dir = os.path.relpath(current_dir, essence_root)
        if current_dir == '.':  # Topmost dir
            for current_file in files:
                if current_file.endswith('.py') and not current_file.startswith('__init__'):
                    current_py = os.path.join(essence_dirname, current_file)
                    import_list.append(('.'.join([circuitry_dirname, essence_dirname, current_file[:-3]]), current_py))
            continue
        # Packages w/ __init__.py
        current_py = os.path.join(essence_dirname, current_dir, '__init__.py')
        import_list.append(('.'.join([circuitry_dirname, essence_dirname, current_dir]), current_py))
        # Ordinary python files
        for current_file in files:
            if current_file.endswith('.py') and not current_file.startswith('__init__'):
                current_py = os.path.join(essence_dirname, current_dir, current_file)
                import_list.append(('.'.join([circuitry_dirname, essence_dirname, current_dir, current_file[:-3]]),
                                    current_py))
    return import_list


def check_python_library_classes(libname, baseclass, libfile, classmembers=None):
    """Get classes from imported files"""
    library_classes = list()
    imported_library = __import__(libname, globals(), locals(), ['*'], -1)
    for library_function in dir(imported_library):
        class_object = imported_library.__dict__.get(library_function)
        if inspect.isclass(class_object):
            if not inspect.getabsfile(class_object).endswith(libfile):  # Check that class is defined in libfile
                continue
            if baseclass in inspect.getmro(class_object) and class_object != baseclass:  # Check for parents
                additional_members = dict()
                if classmembers:  # Get additional information from class
                    for classmember in classmembers:
                        additional_members[classmember] = class_object.__dict__.get(classmember)
                library_classes.append((libname, class_object.__name__, additional_members))
    return library_classes


def self_describe():
    """Full self-introspection for Adapters and Devices"""
    circuitry_root = os.path.dirname(os.path.abspath(__file__))
    _, circuitry_dirname = os.path.split(circuitry_root)

    # Adapters
    adapters_dirname = 'adapters'
    adapters_root = os.path.join(circuitry_root, adapters_dirname)

    adapters_import = get_python_libraries(circuitry_dirname, adapters_dirname, adapters_root)
    adapters_library_classes = list()
    for adapter_import, adapters_file in adapters_import:
        adapters_library_classes.extend(check_python_library_classes(adapter_import, AbstractAdapter, adapters_file))

    # Devices
    devices_dirname = 'devices'
    devices_root = os.path.join(circuitry_root, devices_dirname)

    devices_import = get_python_libraries(circuitry_dirname, devices_dirname, devices_root)
    devices_library_classes = list()
    for device_import, devices_file in devices_import:
        devices_library_classes.extend(check_python_library_classes(device_import, Device, devices_file,
                                                                    ['mandatory_signals', 'truth_table_signals']))

    # FIXME: There we should print out XML or JSON
    print {'adapters': adapters_library_classes,
           'devices': devices_library_classes}
    return


def main():
    self_describe()


if __name__ == '__main__':
    main()