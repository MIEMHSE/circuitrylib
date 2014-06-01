#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2013, The Profitware Group'

from circuitry.adapters import AbstractAdapter
from circuitry.adapters.graph import GraphAdapter


class MatlabAdapter(AbstractAdapter):
    public_methods = ('matlab_code',)
    default_method = lambda self: '\n'.join(self.matlab_code())

    def _matlab_code_handle_counters(self, counters, device_type, device_func_name, device_height, position_x):
        counters['current_position_x'] = position_x

        # Inputs @ position=1, inverted inputs @ position=2
        if device_type == 'input':
            counters['current_position_x'] = 1
            if device_func_name == 'not':
                counters['current_position_x'] = 2

        # # Shift output to position + 1
        # if device_type == 'output' and counters['prev_type'] == 'common':
        #     counters['current_position_x'] += 1
        #
        # # Shift common to position + 1
        # if device_type == 'common' and counters['prev_type'] == 'input':
        #     counters['current_position_x'] += 1
        #
        # if device_type == '' and counters['prev_type'] == 'output':
        #     counters['current_position_x'] += 1

        counters['prev_type'] = device_type

        # Get device start y-position by device type
        if not counters['current_position_x'] in counters['current_position_y_by_x']:
            if device_type == 'input':
                counters['current_position_y_by_x'][counters['current_position_x']] = 0
            elif device_type == 'common':
                counters['current_position_y_by_x'][counters['current_position_x']] = counters['inputs_max_y']
            else:
                counters['current_position_y_by_x'][counters['current_position_x']] = counters['common_max_y']

        # Count maximal y for inputs
        if device_type == 'input':
            _new_max_y = counters['current_position_y_by_x'][counters['current_position_x']] + device_height + 50
            counters['inputs_max_y'] = max(_new_max_y, counters['inputs_max_y'])

        # Count maximal y for common
        if device_type == 'common':
            _new_max_y = counters['current_position_y_by_x'][counters['current_position_x']] + device_height + 50
            # if _new_max_y > counters['inputs_max_y'] * 2:
            #     counters['current_position_x'] += 1
            #     counters['current_position_y_by_x'][counters['current_position_x']] = counters['inputs_max_y']
            counters['common_max_y'] = max(_new_max_y, counters['common_max_y'])

        return counters

    def _matlab_code_generate(self, matlab_code_lines, matlab_code_template):
        # Counters are used at each step to handle current and previous data
        _counters = {
            'inport': 0,
            'outport': 0,
            'and': 0,
            'or': 0,
            'not': 0,
            'current_position_x': 1,
            'current_position_y_by_x': dict(),
            'inputs_max_y': 0,
            'common_max_y': 0,
            'prev_type': '',
            'edges': dict()
        }

        _graph_type_order = {
            'input': 1,
            'common': 2,
            'output': 3
        }

        _matlab_device_name_and_id = ''

        graph_adapter = GraphAdapter(self._device)
        graph = graph_adapter.graph

        def _sorting_function(rec):
            second_param = 0
            if graph.node[rec]['type'] == 'input' and not 'device' in graph.node[rec]:
                second_param = map(str, reduce(list.__add__, map(list, self._device.input_signals))).index(rec)
            if graph.node[rec]['type'] == 'output':
                second_param = graph.node[rec]['global_device_number']
            return _graph_type_order[graph.node[rec]['type']], second_param

        _output_device_list = list()

        for graph_node in sorted(graph.nodes(), key=_sorting_function):
            node = graph.node[graph_node]
            _device, _device_type, _device_func_name, _device_height, _device_ports_count = \
                None, node['type'], '', 10, 1

            # not is_Atom
            if 'device' in node:
                _device = node['device']
                _device_ports_count = len(_device.input_signals[0])
                _device_func_name = str(_device.functions[0].func).lower()
                _device_height = 10 * (_device_ports_count + 1)

            _counters = self._matlab_code_handle_counters(_counters, _device_type, _device_func_name, _device_height,
                                                          graph_adapter.max_distance - node['distance'] + 2)

            # Count position
            matlab_code_lines.append(matlab_code_template['position'] % {
                'x': 100 * (_counters['current_position_x'] * 2),
                'y': _counters['current_position_y_by_x'][_counters['current_position_x']],
                'width': 30,
                'height': _device_height
            })

            # Y-distance between between current and next device
            _counters['current_position_y_by_x'][_counters['current_position_x']] += _device_height + 20

            _matlab_device_name_and_id = ''
            # Straight inputs
            if _device_type == 'input' and _device_func_name != 'not':
                _counters['inport'] += 1
                _device_options = {
                    'device_id': graph_node # _counters['inport']
                }
                matlab_code_lines.append(matlab_code_template['add_block_input'] % _device_options)
                _matlab_device_name_and_id = graph_node  # 'In%(device_id)s' % _device_options

            # Not, And, Or
            if _device_func_name in _counters:
                _counters[_device_func_name] += 1
                _matlab_device_name = _device_func_name[:1].upper() + _device_func_name[1:]
                _device_options = {
                    'device_name': _matlab_device_name,
                    'device_id': _counters[_device_func_name]
                }
                matlab_code_lines.append(matlab_code_template['add_block_logical'] % {
                    'device_name': _matlab_device_name,
                    'device_name_upper': _matlab_device_name.upper(),
                    'ports_number': _device_ports_count,
                    'device_id': _counters[_device_func_name]
                })
                _matlab_device_name_and_id = '%(device_name)s%(device_id)s' % _device_options
            _counters['edges'][graph_node] = _matlab_device_name_and_id

            if node['type'] == 'output':
                _output_device_list.append(_matlab_device_name_and_id)

        # Add output
        _counters = self._matlab_code_handle_counters(_counters, '', '', 0, graph_adapter.max_distance + 3)

        for _matlab_device_name_and_id in _output_device_list:
            matlab_code_lines.append(matlab_code_template['position'] % {
                'x': 100 * (_counters['current_position_x'] * 2),
                'y': _counters['current_position_y_by_x'][_counters['current_position_x']],
                'width': 30,
                'height': 20
            })

            # Y-distance between between current and next device
            _counters['current_position_y_by_x'][_counters['current_position_x']] += 40

            _counters['outport'] += 1
            _device_options = {
                'device_id': _counters['outport']
            }
            matlab_code_lines.append(matlab_code_template['add_block_output'] % _device_options)

            matlab_code_lines.append(matlab_code_template['add_line'] % {
                'connect_from': '%s/1' % _matlab_device_name_and_id,
                'connect_to': 'Out%s/1' % _counters['outport']
            })

        # Connect devices using edges
        _connection_ports = dict()
        for edge in graph.edges_iter():
            _connect_from = '%s/1' % _counters['edges'][edge[0]]
            if not _counters['edges'][edge[1]] in _connection_ports:
                _connection_ports[_counters['edges'][edge[1]]] = 1
            _connect_to = '%s/%s' % (_counters['edges'][edge[1]], _connection_ports[_counters['edges'][edge[1]]])
            _connection_ports[_counters['edges'][edge[1]]] += 1

            matlab_code_lines.append(matlab_code_template['add_line'] % {
                'connect_from': _connect_from,
                'connect_to': _connect_to
            })
        return matlab_code_lines

    def matlab_code(self, **kwargs):
        model_dict = kwargs
        _matlab_code_template = {
            'position': r"pos = [%(x)s %(y)s %(x)s + %(width)s %(y)s + %(height)s]",
            'add_block_logical': r"add_block('built-in/Logical Operator', " +
                                 r"[sys '/%(device_name)s%(device_id)s'], 'Position', pos, " +
                                 r"'Operator', '%(device_name_upper)s', 'Number of input ports', '%(ports_number)s')",
            # 'add_block_input': r"add_block('built-in/Inport', [sys '/In%(device_id)s'], 'Position', pos)",
            'add_block_input': r"add_block('built-in/Inport', [sys '/%(device_id)s'], 'Position', pos)",
            'add_line': r"add_line(sys, '%(connect_from)s', '%(connect_to)s', 'autorouting','on')",
            'add_block_output': r"add_block('built-in/Outport', [sys '/Out%(device_id)s'], 'Position', pos)",
            'add_block_subsystem': r"add_block('built-in/SubSystem', sys, 'Position', pos)"
        }
        if model_dict is None or len(model_dict) == 0:
            model_dict = {
                'newModel1/straight': 'straight'
            }
        _matlab_code_lines = list()
        root_created = False
        position_y_counter = 0
        for model_name in model_dict:
            _model_name_part_full_list = list()
            for model_name_part in model_name.split('/'):
                _model_name_part_full_list.append(model_name_part)
                _model_name_part_full = '/'.join(_model_name_part_full_list)
                _matlab_code_lines.append(r"sys = '%(model_name)s'" % {
                    'model_name': _model_name_part_full
                })
                if len(_model_name_part_full_list) == 1:
                    if not root_created:
                        _matlab_code_lines += [
                            r"new_system(sys)",
                            r"open_system(sys)"
                        ]
                        root_created = True
                else:
                    # Count position
                    _device_height = (sum(map(len, self._device.input_signals)) + 1) * 15
                    _matlab_code_lines.append(_matlab_code_template['position'] % {
                        'x': 100,
                        'y': position_y_counter,
                        'width': 70,
                        'height': _device_height
                    })
                    position_y_counter += _device_height + 50
                    _matlab_code_lines.append(_matlab_code_template['add_block_subsystem'])
            self._matlab_code_generate(_matlab_code_lines, _matlab_code_template)

        return _matlab_code_lines