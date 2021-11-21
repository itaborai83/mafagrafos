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
        
    def __init__(self, logger=None):
        self.logger         = logger
        self.labels         = {}
        self.current_time   = 0
    
    def info(self, *args):
        if self.logger:
            self.logger.error(*args)
    
    def error(self, *args):
        if self.logger:
            self.logger.error(*args)
            
    def tick(self):
        curr_time = self.current_time
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
        
    def handle_direct_loading(self, graph, entry):
        time = self.tick()
        dst_label = self.get_remapped_label(entry.dst)
        dst_node = graph.get_node_by_label(dst_label)
        dst_node.get_attr('ammount').update_at(time, entry.ammount)
        dst_node.get_attr('inputed_ammount').update_at(time, entry.ammount)
    
    def transfer_ammount_through_time(self, graph, orig_dst_label):
        # get the last two label remappings and their respective nodes
        remappings = self.get_label_remappings(orig_dst_label)
        assert len(remappings) >= 2
        current_label = remappings[-1]
        prev_label    = remappings[-2]
        current_node  = graph.get_node_by_label(current_label) 
        assert current_node
        prev_node     = graph.get_node_by_label(prev_label) 
        assert prev_node
        # extract the current balance from the older node and see if a balance time transfer really needs to be done
        prev_node_ammount = prev_node.get_attr('ammount').current_value
        curr_node_ammount = current_node.get_attr('ammount').current_value
        assert curr_node_ammount == 0.0
        if prev_node_ammount == 0.0:
            # do not create a time transfer when there is nothing to transfer
            return
            
        # create the edge
        edge = graph.get_edge(prev_label, current_label)
        assert edge is None        
        time = self.tick()
        edge = graph.add_edge(prev_label, current_label)
        edge_ammount = prev_node_ammount
        prev_node.get_attr('ammount').update_at(time, -prev_node_ammount)
        current_node.get_attr('ammount').update_at(time, prev_node_ammount)
        edge.set_attr('ammount', TimedValue())
        edge.get_attr('ammount').update_at(time, prev_node_ammount)
        edge.set_attr('time', [ times ])
        edge.set_attr('pct', 0.0)
        
    def handle_account_transfer(self, graph, entry):
        orig_src_label = entry.src
        orig_dst_label = entry.dst
        src_label = self.get_remapped_label(orig_src_label)
        dst_label = self.get_remapped_label(orig_dst_label)
        src_node = graph.get_node_by_label(src_label)
        dst_node = graph.get_node_by_label(dst_label)
        edge = graph.get_edge(src_label, dst_label)
        if edge is not None:
            # existing edge does not add a cycle
            time = self.tick()
            edge.get_attr('ammount').update_at(time, entry.ammount)
            edge.get_attr('time').append(time)
        else:
            # try to create the edge
            edge = graph.add_edge(src_label, dst_label)
            while edge is None:
                # a cycle would be created
                dst_label = self.add_remapped_label(orig_dst_label)
                dst_node = self.add_node_if_needed(graph, dst_label) # wll always create the node
                self.transfer_ammount_through_time(graph, orig_dst_label) # transfer the all the remaining balance to the new node
                edge = graph.add_edge(src_label, dst_label)
            time = self.tick()
            edge.set_attr('ammount', TimedValue())
            edge.get_attr('ammount').update_at(time, entry.ammount)
            edge.set_attr('time', [time])
        
        # update the balance of the source node
        src_node.get_attr('ammount').update_at(time, - entry.ammount)
        # update the total transferred ammount of the source node
        src_node.get_attr('transferred_ammount').update_at(time, entry.ammount)
        # update the balace of the destination node
        dst_node.get_attr('ammount').update_at(time, entry.ammount)
        # update the total received ammount of the destination node
        dst_node.get_attr('received_ammount').update_at(time, entry.ammount)
        
    def create_graph(self, graph_name, entries):
        self.info('creating graph')
        graph = Graph(graph_name, allow_cycles=False)

        for entry in entries:
            self.add_node_if_needed(graph, entry.src)
            self.add_node_if_needed(graph, entry.dst)
            if entry.src is None:
                self.handle_direct_loading(graph, entry)
            else:
                self.handle_account_transfer(graph, entry)
        return graph