 # -*- coding: utf-8 -*-
import os
import sys
import argparse
import logging
from mafagrafos.acc_entry import *
from mafagrafos.graph import *
from mafagrafos.presenter import *
from mafagrafos.paths import *

import mafagrafos.util as util

logger = util.get_logger('cycle_remover')

class App:
    
    VERSION = (0, 0, 0)
    
    def __init__(self):
        self.labels = {}
        
    def get_entries(self):
        logger.info('retrieving accounting entries')
        return AccEntry.get_test_case_02()
        
    
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
                logger.info(f"adding label remapping '{old_label}' -> '{new_label}'")
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
            logger.info(f"adding node '{label}'")
            node = graph.add_node(label)
            node.set_attr('ammount', 0.0)
        return node
        
    def handle_direct_loading(self, graph, entry):
        dst_label = self.get_remapped_label(entry.dst)
        dst_node = graph.get_node_by_label(dst_label)
        ammount = dst_node.get_attr('ammount')
        dst_node.set_attr('ammount', ammount + entry.ammount)

    def handle_account_transfer(self, graph, entry, time):
        orig_src_label = entry.src
        orig_dst_label = entry.dst
        src_label = self.get_remapped_label(orig_src_label)
        dst_label = self.get_remapped_label(orig_dst_label)
        src_node = graph.get_node_by_label(src_label)
        dst_node = graph.get_node_by_label(dst_label)
        edge = graph.get_edge(src_label, dst_label)
        if edge is not None:
            # existing edge does not add a cycle
            edge_ammount = edge.get_attr('ammount') + entry.ammount
            edge.set_attr('ammount', edge_ammount)
            time = edge.get_attr('time') + ", " + time
            edge.set_attr('time', time)
        else:
            # try to create the edge
            edge = graph.add_edge(src_label, dst_label)
            while edge is None:
                # a cycle would be created
                dst_label = self.add_remapped_label(orig_dst_label)
                dst_node = self.add_node_if_needed(graph, dst_label)
                edge = graph.add_edge(src_label, dst_label)
            edge.set_attr('ammount', entry.ammount)
            edge.set_attr('time', time)            
        
        src_ammount = src_node.get_attr('ammount') - entry.ammount
        src_node.set_attr('ammount', src_ammount)        
        dst_ammount = dst_node.get_attr('ammount') + entry.ammount
        dst_node.set_attr('ammount', dst_ammount)
        
    def create_graph(self, entries):
        logger.info('creating graph')
        label_remappings = {}
        graph = Graph('Test graph', allow_cycles=False)

        for i, entry in enumerate(entries):
            time = "T"+str(i)
            self.add_node_if_needed(graph, entry.src)
            self.add_node_if_needed(graph, entry.dst)
            if entry.src is None:
                self.handle_direct_loading(graph, entry)
            else:
                self.handle_account_transfer(graph, entry, time)
        return graph
    
    def show_graph(self, graph):
        logger.info('displaying graph')
        presenter = GraphPresenter(graph)
        print(presenter.generate_dot())
    
    def report_paths(self, graph, sink_label):
        paths = Path.build_paths(sink_label, graph)
        print(
            "path_id"
        ,   "path.from_label"
        ,   "path.to_label"
        ,   "path.pct"
        ,   "segment_id"
        ,   "segment.from_label"
        ,   "segment.to_label"
        ,   "segment.pct"
        ,   sep="\t"
        )        
        for path_id, path in enumerate(paths):
            path_pct = str(path.pct*100.0).replace(".", ",")
            for segment_id, segment in enumerate(path.segments):
                segment_pct = str(segment.pct*100.0).replace(".", ",")
                print(
                    path_id
                ,   path.from_label
                ,   path.to_label
                ,   path_pct
                ,   segment_id
                ,   segment.from_label
                ,   segment.to_label
                ,   segment_pct
                ,   sep="\t"
                )
    def run(self):
        logger.info('starting loader - version %d.%d.%d', *self.VERSION)    
        entries = self.get_entries()
        graph = self.create_graph(entries)
        self.show_graph(graph)
        self.report_paths(graph, sink_label="CJ14")
        logger.info('finished')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    #parser.add_argument('--fakeseq',    required=False, action='store_true', help='usa gerador de sequences fake')
    #parser.add_argument('--user',       required=True, type=str, help='usuário do banco de dados oracle')
    #parser.add_argument('--passwd',     required=True, type=str, help='senha do usuário de banco')
    #parser.add_argument('--dsn',        required=True, type=str, help='string de conexão formato [host]:[port]/[service_name]",')
    #parser.add_argument('spreadsheet',  type=str, help='planilha com dados de imóveis')
    args = parser.parse_args()
    app = App()
    app.run()