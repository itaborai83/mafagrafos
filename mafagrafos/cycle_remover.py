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

    def add_edge_if_needed(self, graph, src_node, dst_node):
        edge = graph.get_edge(src_node.label, dst_node.label)
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
            while edge is None: # I don't think this needs to be a loop
                # a cycle would be created
                dst_label = self.add_remapped_label(orig_dst_label)
                dst_node = self.add_node_if_needed(graph, dst_label) # wll always create the node
                self.transfer_ammount_through_time(graph, orig_dst_label) # transfer the all the remaining balance to the new node
                edge = self.add_edge_if_needed(graph, src_node, dst_node)
            time = self.tick()
            edge.get_attr('ammount').update_at(time, entry.ammount)
            edge.get_attr('time').append(time)
        
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