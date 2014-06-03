#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'
__email__ = 'S.Sobko@profitware.ru'
__copyright__ = 'Copyright 2013, The Profitware Group'

from tempfile import mkstemp

from networkx import DiGraph, random_layout, draw_networkx_nodes, draw_networkx_edges, draw_networkx_labels
from matplotlib import pyplot

from circuitry.adapters import AbstractAdapter
from circuitry.devices.simple import create_simple_device_by_function, create_simple_device_by_func_and_number_of_inputs


class GraphAdapter(AbstractAdapter):
    public_properties = ('graph', 'max_distance')
    default_content_type = 'image/png'
    _dnum = 0
    _graph = None
    _max_distance = 0
    _temp_counter = 0
    _global_device_number = 0

    def default_method(self):
        graph = self.graph
        labels_dict = dict()
        for graph_node in graph.nodes_iter():
            graph_type = graph.node[graph_node]['type']
            if graph_type == 'input':
                labels_dict[graph_node] = graph_node
            elif graph_type == 'output':
                labels_dict[graph_node] = 'output'
        pyplot.figure(figsize=(6, 4), dpi=100)
        graph_pos = random_layout(graph)
        draw_networkx_nodes(graph, pos=graph_pos, node_size=640)
        draw_networkx_edges(graph, pos=graph_pos, width=0.5, alpha=0.3)
        draw_networkx_labels(graph, pos=graph_pos, font_size=8, labels=labels_dict)

        pyplot.xlim(-0.05, 1.05)
        pyplot.ylim(-0.05, 1.05)
        pyplot.axis('off')
        _, tmpfile = mkstemp(suffix='.png')
        pyplot.savefig(tmpfile)
        return tmpfile

    @property
    def graph(self):
        # Populate graph
        if self._graph is None:
            # Create directed graph
            self._graph = DiGraph()
            for function in self._device.functions:
                self._walk_through_device_function(function)
            #self._process_graph()
            #for node in self._graph.nodes():
            #    print node, self._graph.node[node]
        return self._graph

    @property
    def max_distance(self):
        _ = self.graph
        return self._max_distance

    def _walk_through_device_function(self, device_function, is_start=True, distance=0):
        self._max_distance = distance
        function_identifier = str(device_function)
        device_type, _device = create_simple_device_by_function(device_function, is_start)
        if not function_identifier in self.graph.nodes():
            if _device is not None:
                self.graph.add_node(function_identifier, device=_device, type=device_type,
                                    distance=distance, global_device_number=self._global_device_number)
                self._global_device_number += 1
                for subfunction in device_function.args:
                    self._walk_through_device_function(subfunction, is_start=False, distance=distance+1)
                    self.graph.add_edge(str(subfunction), function_identifier)
            else:
                self.graph.add_node(function_identifier, type='input', distance=distance,
                                    global_device_number=self._global_device_number)
                self._global_device_number += 1

    def _split_device_by_number_of_inputs(self, device, predecessors, successors, distance, number_of_inputs):
        function = device.functions[0]
        graph = self.graph

        _orig_predecessors = predecessors

        #print len(predecessors), number_of_inputs

        if len(predecessors) <= number_of_inputs:
            for predecessor in predecessors:
                graph.add_edge(predecessor, str(function))
                #print '!!!', predecessor
            for successor in successors:
                graph.add_edge(str(function), successor)
                #print '!!!', successor

            return False

        #print function.args
        function_args = sorted(list(function.args),
                               key=lambda rec: int(
                                   ''.join([i for i in str(rec) if ord(i) in range(ord('0'), ord('9') + 1)])
                               ))
        #from pprint import pprint

        #for predecessor in predecessors:
        #    print predecessor,
        #    pprint(graph.node[predecessor])

        #pprint(function_args)
        pred_and_arg = zip(predecessors, function_args)
        #print pred_and_arg
        #pprint(pred_and_arg)
        _addition_boolean = 0
        _new_predecessors = list()
        pred_and_arg_list = [pred_and_arg[x:x + number_of_inputs] for x in
                             xrange(0, len(pred_and_arg), number_of_inputs)]
        #
        #pprint(pred_and_arg_list)
        #x = False
        for xargs in pred_and_arg_list:
            predecessors, args = zip(*xargs)
            #print 'args', function.func, args, predecessors
            if len(args) == 1:
                #print 'args', function.func, args, predecessors
                #_new_predecessors.append(predecessors[0])
                #x = True
                continue
            _device_type, _device = create_simple_device_by_function(function.func(*args), save_signal_names=True)
            _device_name = str(_device.functions[0])
            #print _device_name, _device_type, _device.functions[0]
            graph.add_node(_device_name, type=_device_type, device=_device, distance=distance)
            #for predecessor in predecessors:
            #    graph.add_edge(predecessor, _device_name)
            #    #print 'edge', predecessor, _device_name
            _new_predecessors.append(_device_name)
            #print 'device_pred', _device_name, _device_type
        #print len(_new_predecessors)
        #pprint(_new_predecessors)
        _device_type, _device = create_simple_device_by_func_and_number_of_inputs(function.func, len(_new_predecessors),
                                                                                  self._dnum)
        self._dnum += 1
        _device_name = str(_device.functions[0])
        #if x:
        #    #pprint(_device)
        #    #print _device_name, _device_type
        graph.add_node(_device_name, type=_device_type, device=_device, distance=distance)
        _predpredecessors_count = 0
        for predecessor in _new_predecessors:
            #print '@', predecessor
            graph.add_edge(predecessor, _device_name)
            for in_signal in graph.node[predecessor]['device']['data_signals']:
                if predecessor in _orig_predecessors:
                    continue
                graph.add_edge(_orig_predecessors[_predpredecessors_count], predecessor)
                _predpredecessors_count += 1
                #pprint(in_signal)
            #print 'edge', predecessor, _device_name
        #print 'device_succ', _device_name, _device_type
        for successor in successors:
            graph.add_edge(_device_name, successor)
            #print 'edge', _device_name, successor
            #new_devices.append(self._split_device_by_number_of_inputs(_device, number_of_inputs))

        if len(_new_predecessors) > number_of_inputs:
            self._replace_graph_node(_device_name)

        return True

    def _replace_graph_node(self, current_node):
        #print current_node
        graph = self.graph
        predecessors = graph.predecessors(current_node)
        successors = graph.successors(current_node)
        if 'device' in graph.node[current_node]:
            _device = graph.node[current_node]['device']
            if str(_device.functions[0].func).lower() in ['or']:
                for predecessor in predecessors:
                    graph.remove_edge(predecessor, current_node)
                for successor in successors:
                    graph.remove_edge(current_node, successor)
                    #print _device.functions[0], _device.input_signals, len(predecessors)
                _distance = graph.node[current_node]['distance']
                if self._split_device_by_number_of_inputs(_device, predecessors, successors, _distance, 4):
                    graph.remove_node(current_node)
            #disconnected_nodes = list()
        #for predecessor in :
        #    pass
        #print graph.node[current_node]
        #print '#1', predecessors
        predecessors = filter(lambda rec: graph.node[rec]['type'] == 'common', predecessors)
        #print '#2', predecessors
        return predecessors

    def _process_graph(self, current_node=None):
        graph = self.graph
        if current_node is None:
            for graph_node in graph.nodes_iter():
                if graph.node[graph_node]['type'] == 'output':
                    current_node = graph_node
        #print graph.node[current_node], current_node
        self._temp_counter += 1

        predecessors = self._replace_graph_node(current_node)
        for predecessor in predecessors:
            self._process_graph(predecessor)
        pass
