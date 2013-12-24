#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2013, The Profitware Group'

from PIL import Image, ImageDraw
from networkx import DiGraph

from circuitry.devices.simple import create_simple_device_by_function
from circuitry.graphical import load_font
from circuitry.graphical.symbol import DefaultElectronicSymbol
from circuitry.graphical.wires import Wire, WiresPool


class DefaultSchematics(object):
    _image = None
    _font = None
    _surface = None
    _device = None

    _options = None
    _inputs = None
    _inputs_not = None

    _graph = None

    @property
    def image(self):
        self._draw_device()
        self._draw_inputs()
        return self._image

    @property
    def graph(self):
        # Populate graph
        self._walk_through_device_function(self._device.function)
        return self._graph

    def _matlab_code_handle_counters(self, counters, device_type, device_func_name, device_height):
        # Inputs @ position=1, inverted inputs @ position=2
        if device_type == 'input':
            counters['current_position_x'] = 1
            if device_func_name == 'not':
                counters['current_position_x'] = 2

        # Shift output to position + 1
        if device_type == 'output' and counters['prev_type'] == 'common':
            counters['current_position_x'] += 1

        # Shift common to position + 1
        if device_type == 'common' and counters['prev_type'] == 'input':
            counters['current_position_x'] += 1

        if device_type == '' and counters['prev_type'] == 'output':
            counters['current_position_x'] += 1

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
            if _new_max_y > counters['inputs_max_y'] * 2:
                counters['current_position_x'] += 1
                counters['current_position_y_by_x'][counters['current_position_x']] = counters['inputs_max_y']
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

        graph = self.graph

        def _sorting_function(rec):
            second_param = 0
            if graph.node[rec]['type'] == 'input' and not 'device' in graph.node[rec]:
                second_param = map(str, reduce(list.__add__, map(list, self._device.input_signals))).index(rec)
            return _graph_type_order[graph.node[rec]['type']], second_param

        for graph_node in sorted(graph.nodes(), key=_sorting_function):
            node = graph.node[graph_node]
            _device, _device_type, _device_func_name, _device_height, _device_ports_count = \
                None, node['type'], '', 10, 1

            # not is_Atom
            if 'device' in node:
                _device = node['device']
                _device_ports_count = len(_device.input_signals[0])
                _device_func_name = str(_device.function.func).lower()
                _device_height = 10 * (_device_ports_count + 1)

            _counters = self._matlab_code_handle_counters(_counters, _device_type, _device_func_name, _device_height)

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

        # Add output
        _counters = self._matlab_code_handle_counters(_counters, '', '', 0)
        matlab_code_lines.append(matlab_code_template['position'] % {
            'x': 100 * (_counters['current_position_x'] * 2),
            'y': _counters['current_position_y_by_x'][_counters['current_position_x']],
            'width': 30,
            'height': 20
        })
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

    def matlab_code(self, model_dict=None):
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
        if model_dict is None:
            model_dict = {
                'newModel/straight': 'straight',
                'newModel/nand': 'nand'
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


    def __init__(self, **kwargs):
        self._options = {
            'background': 'white',
            'foreground': 'black',
            'fontname': 'sans-serif.ttf',
            'pins_interval_height': 15,
            'width': 800,
            'height': 600,
            'indent_x': 40,
            'indent_y': 10
        }
        self._inputs = set()
        self._inputs_not = set()
        # Here we may set width, height, device and other options
        self._options.update(kwargs)
        # Create directed graph
        self._graph = DiGraph()
        # Load device
        self._device = self._options['device']
        # PIL manipulations
        self._image = Image.new('RGB', (self._options['width'], self._options['height']),
                                self._options['background'])
        self._font = load_font(self._options['fontname'])
        self._surface = ImageDraw.Draw(self._image)

    def _draw_simple_device(self, device_function_list, position_index, device_offset):
        _device_distance_height = self._options['height'] / (len(device_function_list) + 1) + device_offset
        _device_height = _device_distance_height
        for device_function in device_function_list:
            device_type, _device = create_simple_device_by_function(device_function)
            if _device is not None:
                _created_device_function = _device.function
                if device_type == 'input':
                    if str(_created_device_function.func).lower() == 'not':
                        self._inputs_not |= {device_function}
                _device_symbol = DefaultElectronicSymbol(device=_device)
                self._image.paste(_device_symbol.image,
                                  (self._options['width'] - _device_symbol._options['width'] * position_index,
                                   _device_height - _device_symbol._options['height'] / 2))
            _device_height += _device_distance_height
        pass

    def _walk_through_device_function(self, device_function, is_start=True):
        function_identifier = str(device_function)
        device_type, _device = create_simple_device_by_function(device_function, is_start)
        if not function_identifier in self._graph.nodes():
            if _device is not None:
                self._graph.add_node(function_identifier, device=_device, type=device_type)
                for subfunction in device_function.args:
                    self._walk_through_device_function(subfunction, is_start=False)
                    self._graph.add_edge(str(subfunction), function_identifier)
            else:
                self._graph.add_node(function_identifier, type='input')

    def _draw_device(self):
        pass

    def _draw_inputs(self):
        pass


class MultiplexerSchematics(DefaultSchematics):
    def _draw_device(self, function_list=None, position=1, _device_offset=None):
        if function_list is None:
            _args_list = [self._device.function]
        else:
            _args_list = function_list
        _device_offset = len(_args_list) * self._options['pins_interval_height']
        self._inputs |= set(filter(lambda x: x.is_Atom, _args_list))
        self._draw_simple_device(_args_list, position, _device_offset)
        _next_function_list = reduce(list.__add__, [list(_arg.args) for _arg in _args_list])
        if reduce(lambda x, y: x and y.is_Atom, _next_function_list):
            return
        self._draw_device(_next_function_list, position + 2, _device_offset)

    def _draw_inputs(self):
        # FIXME: Draw wires and connect devices to input bus
        wires_pool = WiresPool()
        for _signals_tuple in self._device.input_signals:
            for _signal in _signals_tuple:
                if _signal in self._inputs:
                    wires_pool += [Wire(signal=_signal)]
        inputs_not_list = list(self._inputs_not)
        for _signal in sorted(inputs_not_list, key=lambda rec: wires_pool.index(rec.args[0])):
            wires_pool += [Wire(signal=_signal)]
        _input_height = self._options['pins_interval_height']
        for i in range(0, len(wires_pool)):
            _current_y = (i + 1) * _input_height
            if wires_pool[i].signal.is_Atom:
                _offset_x = 30
            else:
                _offset_x = 60
                self._surface.line((_offset_x + i * 15, _current_y, _offset_x + i * 15,
                                    (wires_pool.index(wires_pool[i].signal.args[0]) + 1) * _input_height),
                                   self._options['foreground'], 1)
            self._surface.line((_offset_x, _current_y, self._options['width'], _current_y),
                               self._options['foreground'], 1)
            text = str(wires_pool[i].signal)
            _text_dimension = self._font.getsize(text)
            _text_position = (_offset_x / 2 - _text_dimension[0] / 2,
                              _current_y - _text_dimension[1] / 2)
            self._surface.text(_text_position, text, self._options['foreground'], self._font)
        #from pprint import pprint
        #pprint(wires_pool)
        #_input_height = 15
        #_inputs = [_input for _input in self._device if _input.endswith('_signals') and _input != 'output_signals']
        #print self._device.input_signals
        #print _inputs
        #for _position_input in range(1, len(self._inputs)):
        #    _current_y = _position_input * _input_height
        #    self._surface.line((30, _current_y, self._options['width'], _current_y), self._options['foreground'], 1)
