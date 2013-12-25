#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2013, The Profitware Group'

from networkx import DiGraph

from circuitry.adapters import AbstractAdapter
from circuitry.devices.simple import create_simple_device_by_function, create_simple_device_by_func_and_number_of_inputs


class GraphAdapter(AbstractAdapter):
    public_properties = ('graph',)
    _dnum = 0
    _graph = None

    @property
    def graph(self):
        # Populate graph
        if self._graph is None:
            # Create directed graph
            self._graph = DiGraph()
            self._walk_through_device_function(self._device.function)
            self._process_graph()
        return self._graph

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

    def _split_device_by_number_of_inputs(self, device, predecessors, successors, number_of_inputs):
        function = device.function
        graph = self._graph

        if len(predecessors) <= number_of_inputs:
            for predecessor in predecessors:
                graph.add_edge(predecessor, str(function))
            for successor in successors:
                graph.add_edge(str(function), successor)

            return False

        pred_and_arg = zip(predecessors, function.args)
        #pprint(pred_and_arg)
        _addition_boolean = 0
        _new_predecessors = list()
        pred_and_arg_list = [pred_and_arg[x:x + number_of_inputs] for x in
                             xrange(0, len(pred_and_arg), number_of_inputs)]
        #pprint(pred_and_arg_list)
        for xargs in pred_and_arg_list:
            predecessors, args = zip(*xargs)
            #print 'args', args
            _device_type, _device = create_simple_device_by_function(function.func(*args), save_signal_names=True)
            _device_name = str(_device.function)
            graph.add_node(_device_name, type=_device_type, device=_device)
            for predecessor in predecessors:
                graph.add_edge(predecessor, _device_name)
                #print 'edge', predecessor, _device_name
            _new_predecessors.append(_device_name)
            #print 'device_pred', _device_name, _device_type
        #print len(_new_predecessors)
        _device_type, _device = create_simple_device_by_func_and_number_of_inputs(function.func, len(_new_predecessors),
                                                                                  self._dnum)
        self._dnum += 1
        _device_name = str(_device.function)
        graph.add_node(_device_name, type=_device_type, device=_device)
        for predecessor in _new_predecessors:
            graph.add_edge(predecessor, _device_name)
            #print 'edge', predecessor, _device_name
        #print 'device_succ', _device_name, _device_type
        for successor in successors:
            graph.add_edge(_device_name, successor)
            #print 'edge', _device_name, successor
            #new_devices.append(self._split_device_by_number_of_inputs(_device, number_of_inputs))
        return True

    def _replace_graph_node(self, current_node):
        graph = self._graph
        predecessors = graph.predecessors(current_node)
        successors = graph.successors(current_node)
        if 'device' in graph.node[current_node]:
            _device = graph.node[current_node]['device']
            if str(_device.function.func).lower() in ['or']:
                for predecessor in predecessors:
                    graph.remove_edge(predecessor, current_node)
                for successor in successors:
                    graph.remove_edge(current_node, successor)
                    #print _device.function, _device.input_signals, len(predecessors)
                if self._split_device_by_number_of_inputs(_device, predecessors, successors, 4):
                    graph.remove_node(current_node)
            #disconnected_nodes = list()
        #for predecessor in :
        #    pass
        #print graph.node[current_node]
        return predecessors

    def _process_graph(self, current_node=None):
        graph = self._graph
        if current_node is None:
            for graph_node in graph.nodes_iter():
                if graph.node[graph_node]['type'] == 'output':
                    current_node = graph_node
        predecessors = self._replace_graph_node(current_node)
        for predecessor in predecessors:
            self._process_graph(predecessor)
        pass
