 # -*- coding: utf-8 -*-
import os
import sys
import argparse
import logging
import pandas as pd
import numpy as np

from mafagrafos.acc_entry import *
from mafagrafos.graph import *
from mafagrafos.presenter import *
from mafagrafos.paths import *
from mafagrafos.timed_value import *

import mafagrafos.util as util

logger = util.get_logger('cycle_remover')

class CycleRemover:
    
    SHOW_PATH_BUILDING = False
    
    def __init__(self, logger=None):
        self.logger         = logger
        self.labels         = {}
        self.current_time   = 0
        self.clock_running  = True
    
    def info(self, *args):
        if self.logger:
            self.logger.info(*args)
    
    def error(self, *args):
        if self.logger:
            self.logger.error(*args)
    
    def stop_clock(self):
        assert self.clock_running
        self.clock_running = False
    
    def start_clock(self):
        assert not self.clock_running
        self.clock_running = True
        
    def tick(self):
        curr_time = self.current_time
        if self.clock_running:
            self.current_time += 1
        return curr_time
    
    def get_label_remappings(self, label):
        result = [label]
        while True:
            if label not in self.labels:
                return result
            label = self.labels[label]
            result.append(label)
            
    def get_remapped_label(self, label):
        while True:
            if label not in self.labels:
                return label
            label = self.labels[label]
    
    def add_remapped_label(self, label):
        orig_label = label
        counter = 1
        old_label = label
        new_label = f"{orig_label}--{counter}"
        while True:
            if old_label not in self.labels:
                self.info(f"adding label remapping '{old_label}' -> '{new_label}'")
                self.labels[old_label] = new_label
                return new_label
            else:
                counter += 1
                old_label = new_label
                new_label = f"{orig_label}--{counter}"
    
    def add_node_if_needed(self, graph, label):
        if label is None:
            return 
        label = self.get_remapped_label(label)
        node = graph.get_node_by_label(label)
        if node is None:
            self.info(f"adding node '{label}'")
            node = graph.add_node(label)
            node.set_attr('ammount', TimedValue())
            node.set_attr('inputed_ammount', TimedValue())
            node.set_attr('received_ammount', TimedValue())
            node.set_attr('transferred_ammount', TimedValue())
        return node

    def add_edge_if_needed(self, graph, src_node, dst_node, ensure_creation=False):
        edge = graph.get_edge(src_node.label, dst_node.label)
        if ensure_creation:
            assert edge
        if edge:
            # edge exists
            return edge
        if edge is None:
            # edge does not exist. Try to create a new one
            edge = graph.add_edge(src_node.label, dst_node.label)
            if edge is None:
                return None # edge would introduce a cycle
            edge.set_attr('ammount', TimedValue())
            edge.set_attr('time', [])
            return edge
        
    def handle_direct_loading(self, graph, entry):
        time = self.tick()
        dst_label = self.get_remapped_label(entry.dst)
        dst_node = graph.get_node_by_label(dst_label)
        dst_node.get_attr('ammount').update_at(time, entry.ammount)
        dst_node.get_attr('inputed_ammount').update_at(time, entry.ammount)
    
    def transfer_ammount_through_time(self, graph, orig_dst_label):
        # remapped node needs to already exist
        # get the last two label remappings and their respective nodes
        remappings = self.get_label_remappings(orig_dst_label)
        assert len(remappings) >= 2
        dst_label = remappings[-1]
        src_label = remappings[-2]
        dst_node  = graph.get_node_by_label(dst_label) 
        assert dst_node
        src_node     = graph.get_node_by_label(src_label) 
        assert src_node
        # extract the current balance from the older node and see if a balance time transfer really needs to be done
        src_node_ammount = src_node.get_attr('ammount').current_value
        dst_node_ammount = dst_node.get_attr('ammount').current_value
        assert dst_node_ammount == 0.0
        
        if src_node_ammount == 0.0:
            # do not create a time transfer when there is nothing to transfer
            return
            
        # create the edge
        edge = graph.get_edge(src_label, dst_label)
        assert edge is None        
        edge = self.add_edge_if_needed(graph, src_node, dst_node)
        assert edge
        time = self.tick()
        edge.get_attr('ammount').update_at(time, src_node_ammount)
        edge.get_attr('time').append(time)
        
        # update the balance of both source and destination nodes
        src_node.get_attr('ammount').update_at(time, -src_node_ammount)
        dst_node.get_attr('ammount').update_at(time, src_node_ammount)
        # update the transferred_ammount of the source node
        src_node.get_attr('transferred_ammount').update_at(time, src_node_ammount)
        # update the total received ammount of the destination node
        dst_node.get_attr('received_ammount').update_at(time, src_node_ammount)
    
    def handle_account_transfer(self, graph, entry):
        orig_src_label = entry.src
        orig_dst_label = entry.dst
        src_label = self.get_remapped_label(orig_src_label)
        dst_label = self.get_remapped_label(orig_dst_label)
        src_node = graph.get_node_by_label(src_label)
        dst_node = graph.get_node_by_label(dst_label)
        edge = self.add_edge_if_needed(graph, src_node, dst_node)
        if edge is not None:
            # edge either existed or was just created
            time = self.tick()
            edge.get_attr('ammount').update_at(time, entry.ammount)
            edge.get_attr('time').append(time)
        else:
            # edge would create a cycle
            #while edge is None: # I don't think this needs to be a loop
            # a cycle would be created
            dst_label = self.add_remapped_label(orig_dst_label)
            dst_node = self.add_node_if_needed(graph, dst_label) # wll always create the node
            self.transfer_ammount_through_time(graph, orig_dst_label) # transfer the all the remaining balance to the new node
            edge = self.add_edge_if_needed(graph, src_node, dst_node)
            assert edge
            time = self.tick()
            edge.get_attr('ammount').update_at(time, entry.ammount)
            edge.get_attr('time').append(time)
        # update the balance of the source node
        src_node.get_attr('ammount').update_at(time, - entry.ammount)
        # update the total transferred ammount of the source node
        src_node.get_attr('transferred_ammount').update_at(time, entry.ammount)
        # update the balance of the destination node
        dst_node.get_attr('ammount').update_at(time, entry.ammount)
        # update the total received ammount of the destination node
        dst_node.get_attr('received_ammount').update_at(time, entry.ammount)
    
    """
    def compute_edge_pct(self, src_node, edge, dst_node, parent_curr_t=None):
        assert dst_node.node_id == edge.to_id
        assert edge.from_id == src_node.node_id
        times = edge.get_attr('time')
        assert len(times) > 0
        if parent_curr_t is None:
            max_time = edge.get_attr('time')[-1]
        else:
            max_time = parent_curr_t
            #max_time = None
            #for time in reversed(edge.get_attr('time')):
            #    if time <= parent_curr_t:
            #        max_time = time
            #if max_time is None:
            #    # the edge is temporally inconsistent
            #    return 0.0, None            
            #max_time = min(parent_curr_t, max_time)
            
        # compute the edge pct at max_time
        edge_ammount        = edge.get_attr('ammount').value_at(max_time)
        #if edge_ammount == 0.0:
        #    # the edge is temporally inconsistent                
        #        return 0.0, None
        node_ammount        = src_node.get_attr('ammount').value_at(max_time)
        inputed_ammount     = src_node.get_attr('inputed_ammount').value_at(max_time)
        transferred_ammount = src_node.get_attr('transferred_ammount').value_at(max_time)
        received_ammount    = src_node.get_attr('received_ammount').value_at(max_time)
        #edges_sum           = node_ammount + edge_ammount + transferred_ammount
        edges_sum           = node_ammount + transferred_ammount
        if edges_sum == 0.0:
            #return 0.0, None
            return 1.0, max_time
        edge_pct            = edge_ammount / edges_sum        
        
        #print()
        #print(f'edge_times          = {edge.get_attr("time")}')
        #print(f'max_time            = {max_time}')
        #print(f'edge_ammount        = {edge_ammount}/{edge.get_attr("ammount")}')
        #print(f'node_ammount        = {src_node.get_attr("ammount")}')
        #print(f'inputed_ammount     = {src_node.get_attr("inputed_ammount")}')
        #print(f'transferred_ammount = {src_node.get_attr("transferred_ammount")}')
        #print(f'edges_sum           = {edges_sum}')
        #print(f'edge_pct            = {edge_pct}')
                
        return edge_pct, max_time
    
    
    def build_paths(self, graph, sink_label):
        #import pdb; pdb.set_trace()
        # graph is a DAG, so no cycles
        assert not graph.allow_cycles
        labels = self.get_label_remappings(sink_label)
        acc = []
        for label in labels:
            head_node = graph.get_node_by_label(label)
            assert head_node
            curr_path = Path()
            self._build_path(graph, head_node, None, None, None, curr_path, acc)
        return acc
    
    def _build_path(self, graph, head_node, edge, tail_node, parent_edge, curr_path, acc):
        if self.SHOW_PATH_BUILDING:
            print(head_node)
            print(edge)
            print(tail_node)
            for segment in curr_path.segments:
                print("\t", segment)
            print()
        
        old_path = curr_path
        new_tail_node = head_node
        parent_edge = edge
        for from_id in new_tail_node.in_edges:
            # retrieve the start node of the edge
            new_head_node = graph.get_node_by_id(from_id)
            assert new_head_node
            # make sure the edge is not a virtual edge used to transfer funds through time
            orig_head_label = new_head_node.label.split("--")[0]
            orig_tail_label = new_tail_node.label.split("--")[0]
            if orig_head_label == orig_tail_label:
                # not a valid path
                continue
            # use the node label to retrieve the edge itself
            edge = graph.get_edge(new_head_node.label, new_tail_node.label)
            assert edge
            # create a new path cloning the old path 
            curr_path = old_path.clone()
            # compute this edges min and max times
            times = edge.get_attr('time')
            min_t = times[0]
            max_t = times[-1]                        
            assert min_t <= max_t
            # if the current edge has a parent edge, check its max time
            if parent_edge is None:
                parent_curr_t = None
            else:
                #times = parent_edge.get_attr('time')
                #parent_max_t = times[-1]
                #parent_curr_t = curr_path.segments[-1].curr_t
                parent_curr_t = curr_path.segments[0].curr_t
                    
            # compute the edge percent taking into account the parent edge's max time
            pct, curr_t = self.compute_edge_pct(new_head_node, edge, new_tail_node, parent_curr_t)
            if pct == 0.0 or curr_t is None:
                # the edge is temporally inconsistent.
                # stop processing this path
                return                

            #if parent_curr_t is not None: 
            #    # check if the whole path is temporally consistent
            #    # note: I thought this would work checking only the next segment, but it didn't
            #    # so I am accepting the O(n) cost of this operation
            #    for segment in curr_path.segments:
            #        if segment.curr_t < min_t:
            #            # the edge is temporally inconsistent.
            #            # stop processing this path
            #            return
                        
            # push a new segment onto the first position of the current path
            segment = Segment(
                from_label  = new_head_node.label
            ,   to_label    = new_tail_node.label
            ,   pct         = pct
            ,   min_t       = min_t
            ,   curr_t      = curr_t
            ,   max_t       = max_t
            )
            curr_path.push_segment(segment)
            curr_path.ammount             = new_head_node.get_attr('ammount').value_at(curr_t)
            curr_path.inputed_ammount     = new_head_node.get_attr('inputed_ammount').value_at(curr_t)
            curr_path.received_ammount    = new_head_node.get_attr('received_ammount').value_at(curr_t)
            curr_path.transferred_ammount = new_head_node.get_attr('transferred_ammount').value_at(curr_t)
            acc.append(curr_path)
            # continue exploring this path
            self._build_path(graph, new_head_node, edge, new_tail_node, parent_edge, curr_path, acc)
    """

    def compute_edge_pct(self, src_node, edge, dst_node, max_time):
        assert dst_node.node_id == edge.to_id
        assert edge.from_id == src_node.node_id
        times = edge.get_attr('time')
        assert len(times) > 0
            
        # compute the edge pct at max_time
        edge_ammount        = edge.get_attr('ammount').value_at(max_time)
        if edge_ammount == 0.0:
            # the edge is temporally inconsistent                
            return 0.0
        node_ammount        = src_node.get_attr('ammount').value_at(max_time)
        inputed_ammount     = src_node.get_attr('inputed_ammount').value_at(max_time)
        transferred_ammount = src_node.get_attr('transferred_ammount').value_at(max_time)
        received_ammount    = src_node.get_attr('received_ammount').value_at(max_time)

        edges_sum           = node_ammount + transferred_ammount
        if edges_sum == 0.0:
            #return 0.0
            return 1.0 # is this right???
        
        edge_pct = edge_ammount / edges_sum        
                        
        return edge_pct    
    
    def build_paths(self, graph, sink_label):
        #import pdb; pdb.set_trace()
        # graph is a DAG, so no cycles
        assert not graph.allow_cycles
        labels = self.get_label_remappings(sink_label)
        acc = []
        for label in labels:
            head_node = graph.get_node_by_label(label)
            assert head_node
            curr_path = None
            self._build_path(graph, head_node, None, None, None, curr_path, acc)
        return acc
    
    def _build_path(self, graph, head_node, edge, tail_node, parent_edge, curr_path, acc):
        
        old_path = curr_path
        new_tail_node = head_node
        parent_edge = edge
        for from_id in new_tail_node.in_edges:
            # retrieve the start node of the edge
            new_head_node = graph.get_node_by_id(from_id)
            assert new_head_node
            #orig_head_label = new_head_node.label.split("--")[0]
            #orig_tail_label = new_tail_node.label.split("--")[0]
            #if orig_head_label == orig_tail_label:
            #    # not a valid path
            #    continue            
            # make sure the edge is not a virtual edge used to transfer funds through time
            # use the node label to retrieve the edge itself
            edge = graph.get_edge(new_head_node.label, new_tail_node.label)
            assert edge
            # compute this edges min and max times
            times = edge.get_attr('time')
            max_t = times[-1]
            
            if old_path is None:
                # create a root path
                curr_path = PathV2()
                curr_path.root_path     = self
                curr_path.from_label    = new_head_node.label
                curr_path.to_label      = new_tail_node.label
                curr_path.parent_path   = None
                curr_path.children      = []
                curr_path.length        = 1
                curr_path.max_t         = max_t
                curr_path.pct           = self.compute_edge_pct(new_head_node, edge, new_tail_node, max_t)
                if curr_path.pct == 0.0:
                    # edge is a dead end
                    # stop processing this path
                    del curr_path
                    return
            else:
                # create a new path pointing the old one as its parent
                curr_path = PathV2()
                curr_path.root_path              = old_path.root_path
                curr_path.from_label             = new_head_node.label
                curr_path.to_label               = old_path.to_label # stays the same
                curr_path.parent_path            = old_path
                curr_path.children               = []
                curr_path.length                 = old_path.length + 1
                curr_path.max_t                  = min(max_t, old_path.max_t)
                curr_path.pct                    = self.compute_edge_pct(new_head_node, edge, new_tail_node, max_t)
                if curr_path.pct == 0.0:
                    # edge is a dead end
                    # stop processing this path
                    del curr_path
                    return                    
                old_path.children.append(curr_path)
            
            curr_path.path_id             = PathV2.next_id()
            curr_path.ammount             = new_head_node.get_attr('ammount').value_at(curr_path.max_t)
            curr_path.inputed_ammount     = new_head_node.get_attr('inputed_ammount').value_at(curr_path.max_t)
            curr_path.received_ammount    = new_head_node.get_attr('received_ammount').value_at(curr_path.max_t)
            curr_path.transferred_ammount = new_head_node.get_attr('transferred_ammount').value_at(curr_path.max_t)
            acc.append(curr_path)
            # continue exploring this path
            self._build_path(graph, new_head_node, edge, new_tail_node, parent_edge, curr_path, acc)
            
    def handle_entry(self, graph, entry):
        self.add_node_if_needed(graph, entry.src)
        self.add_node_if_needed(graph, entry.dst)
        if entry.src is None:
            self.handle_direct_loading(graph, entry)
        else:
            self.handle_account_transfer(graph, entry)
    
    def handle_batched_timed_entries(self, graph, entries):
        # time advances
        self.tick() 
        self.stop_clock()
        # handle first inputed ammounts
        for entry in entries:
            if entry.src is None:
                self.handle_entry(graph, entry)
        self.start_clock()
                
        # time advances
        self.tick() 
        self.stop_clock()
        # now handle transfers
        entries.sort(key=lambda e: (e.dst, e.src))
        for entry in entries:
            if entry.src is None:
                continue
            self.handle_entry(graph, entry)
        self.start_clock()
        
    def create_graph(self, graph_name, entries):
        graph = Graph(graph_name, allow_cycles=False)
        has_date_time = entries[0].date
        
        if not has_date_time:
            self.info('creating graph not using time stamp information')
            for entry in entries:
                assert entry.date is None
                assert entry.time is None
                self.handle_entry(graph, entry)
        else:
            self.info('creating graph using time stamp information')
            last_date = entries[0].date
            last_time = entries[0].time
            acc_entries = []
            for entry in entries:
                if last_date == entry.date and last_time == entry.time:
                    acc_entries.append(entry)
                else:
                    assert last_date < entry.date or last_date == entry.date and last_time < entry.time, (last_date, entry.date, entry.date, entry.time)
                    self.handle_batched_timed_entries(graph, acc_entries)
                    acc_entries.clear()
                    acc_entries.append(entry)
            last_date = entry.date
            last_time = entry.time
        
        if len(acc_entries) > 0:
            self.handle_batched_timed_entries(graph, acc_entries)
            acc_entries.clear()            
        
        return graph
