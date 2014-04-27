#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2013, The Profitware Group'

from circuitry.adapters.matlab import MatlabAdapter

class ExtendedMatlabAdapter(MatlabAdapter):
    def matlab_code(self, **kwargs):
        if not 'model_name' in kwargs or not 'subsystems' in kwargs:
            model_name = 'newModel1'
            subsystems = ['straight']
        else:
            model_name = kwargs['model_name']
            subsystems = kwargs['subsystems']

        matlab_code_lines = super(ExtendedMatlabAdapter, self).matlab_code(**dict(
            [('%(model_name)s/%(subsystem)s' % {'model_name': model_name, 'subsystem': _subsystem}, _subsystem) for
             _subsystem in subsystems]))

        signal_const = zip(map(str, reduce(list.__add__, map(list, self._device.input_signals))),
                           reduce(list.__add__, self._device.truth_table[0][:-1]))

        output_signals_count = len(self._device.output_signals)

        _matlab_code_template = {
            'position': r"pos = [%(x)s %(y)s %(x)s + %(width)s %(y)s + %(height)s]",
            'add_line': r"add_line(sys, '%(connect_from)s', '%(connect_to)s', 'autorouting','on')",
            'add_block_const': r"add_block('built-in/Constant', [sys '/%(device_id)s'], " +
                               r"'Position', pos, 'Value', '%(value)s', 'OutDataTypeStr', 'boolean')",
            'add_block_display': r"add_block('built-in/Display', [sys '/Display%(device_id)s'], 'Position', pos)"
        }

        matlab_code_lines.append(r"sys = '%(model_name)s'" % {'model_name': model_name})

        # Constants
        position_y_counter = 20
        port_number = 1
        _device_height = 20
        for k, v in signal_const:
            matlab_code_lines.append(_matlab_code_template['position'] % {
                'x': 20,
                'y': position_y_counter,
                'width': 20,
                'height': _device_height
            })
            matlab_code_lines.append(_matlab_code_template['add_block_const'] % {
                'device_id': k,
                'value': v
            })
            for subsystem in subsystems:
                matlab_code_lines.append(_matlab_code_template['add_line'] % {
                    'connect_from': '%s/1' % k,
                    'connect_to': '%s/%s' % (subsystem, port_number)
                })

            port_number += 1
            position_y_counter += _device_height + 20

        # Displays
        position_y_counter = 20
        _device_height = 30
        for subsystem in subsystems:
            for output_signal_i in range(1, output_signals_count + 1):
                matlab_code_lines.append(_matlab_code_template['position'] % {
                    'x': 250,
                    'y': position_y_counter,
                    'width': 70,
                    'height': _device_height
                })
                matlab_code_lines.append(_matlab_code_template['add_block_display'] % {
                    'device_id': ('_%s_%s' % (subsystem, output_signal_i))
                })
                matlab_code_lines.append(_matlab_code_template['add_line'] % {
                    'connect_from': '%s/%s' % (subsystem, output_signal_i),
                    'connect_to': 'Display%s/1' % ('_%s_%s' % (subsystem, output_signal_i))
                })
                position_y_counter += _device_height + 20

        return matlab_code_lines