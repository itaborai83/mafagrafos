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

import mafagrafos.util as util

logger = util.get_logger('cycle_remover')

class App:
    
    VERSION = (0, 0, 0)
    ENTRIES_SHEET_COLUMNS = [ "dst", "src", "ammount" ]
    
    def __init__(self, entries_file, sink_label, dot_file, path_report):
        assert dot_file.endswith(".dot")
        self.entries_file   = entries_file
        self.sink_label     = sink_label
        self.dot_file       = dot_file
        self.path_report    = path_report
        self.labels         = {}
        
    def get_entries(self):
        logger.info('retrieving accounting entries from spreadsheet')
        parts = self.entries_file.split(":")
        assert len(parts) == 2
        entries_file = parts[0]
        sheet_name = parts[1]            
        df = pd.read_excel(entries_file, sheet_name, header=None, names=self.ENTRIES_SHEET_COLUMNS, skiprows=1).replace({np.nan: None})
        result = []
        for row in df.itertuples():
            entry = AccEntry(
                row.dst
            ,   row.src if row.src else None
            ,   row.ammount
            )
            result.append(entry)
        return result
    
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
            node.set_attr('inputed_ammount', 0.0)
        return node
        
    def handle_direct_loading(self, graph, entry):
        dst_label = self.get_remapped_label(entry.dst)
        dst_node = graph.get_node_by_label(dst_label)
        ammount = dst_node.get_attr('ammount')
        inputed_ammount = dst_node.get_attr('inputed_ammount')
        dst_node.set_attr('ammount', ammount + entry.ammount)
        dst_node.set_attr('inputed_ammount', inputed_ammount + entry.ammount)
        
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
    
    def generate_graph(self, graph):
        logger.info(f'generating dotfile')
        presenter = GraphPresenter(graph)
        with open(self.dot_file, "w") as fh:
            print(presenter.generate_dot(), file=fh)
            
    def report_entries(self, xlsx_writer, entries):
        logger.info('generating accounting entries sheet')
        columns = { 'DESTINO': [], 'ORIGEM': [], 'VALOR': [] }
        for entry in entries:
            columns['DESTINO'].append(entry.dst)
            columns['ORIGEM'].append(entry.src)
            columns['VALOR'].append(entry.ammount)
        df_entries = pd.DataFrame(columns)
        df_entries.to_excel(xlsx_writer, sheet_name='PARTIDAS')

    def report_balances(self, xlsx_writer, graph):
        logger.info('generating balance sheet')
        columns = {
            'ORIGEM'                : []
        ,   'ENTRADA_DIRETA'        : []
        ,   'SALDO'                 : []
        }
        for node in graph.nodes:
            columns['ORIGEM'        ].append(node.label)
            columns['ENTRADA_DIRETA'].append(node.get_attr('inputed_ammount'))
            columns['SALDO'         ].append(node.get_attr('ammount'))
        df_entries = pd.DataFrame(columns)
        df_entries.to_excel(xlsx_writer, sheet_name='SALDOS')
        
    def report_paths(self, xlsx_writer, paths):
        logger.info('generating paths sheet')
        columns = {
            'CAMINHO'               : []
        ,   'ORIGEM'                : []
        ,   'DESTINO'               : []
        ,   'PERCENTUAL'            : []
        ,   'ENTRADA_DIRETA_ORIGEM' : []
        ,   'REPASSE_RESULTANTE'    : []
        }
        for path_id, path in enumerate(paths):
            pct = path.pct 
            columns['CAMINHO'               ].append(path_id + 1)
            columns['ORIGEM'                ].append(path.from_label)
            columns['DESTINO'               ].append(path.to_label)
            columns['PERCENTUAL'            ].append(pct * 100)
            columns['ENTRADA_DIRETA_ORIGEM' ].append(path.inputed_ammount)
            columns['REPASSE_RESULTANTE'    ].append(path.inputed_ammount * pct)
        df_entries = pd.DataFrame(columns)
        df_entries.to_excel(xlsx_writer, sheet_name='CAMINHOS')

    def report_segments(self, xlsx_writer, paths):
        logger.info('generating segments sheet')
        columns = {
            'CAMINHO'               : []
        ,   'ORIGEM'                : []
        ,   'DESTINO'               : []
        ,   'PERCENTUAL'            : []
        ,   'ENTRADA_DIRETA_ORIGEM' : []
        ,   'REPASSE_RESULTANTE'    : []
        ,   'SEGMENTO'              : []
        ,   'SEG_ORIGEM'            : []
        ,   'SEG_DESTINO'           : []
        ,   'SEG_PERCENTUAL'        : []
        }
        for path_id, path in enumerate(paths):
            pct = path.pct 
            for segment_id, segment in enumerate(path.segments):
                pct = segment.pct
                columns['CAMINHO'               ].append(path_id + 1)
                columns['ORIGEM'                ].append(path.from_label)
                columns['DESTINO'               ].append(path.to_label)
                columns['PERCENTUAL'            ].append(pct * 100.0)
                columns['ENTRADA_DIRETA_ORIGEM' ].append(path.inputed_ammount)
                columns['REPASSE_RESULTANTE'    ].append(path.inputed_ammount * pct)
                columns['SEGMENTO'              ].append(segment_id+1)
                columns['SEG_ORIGEM'            ].append(segment.from_label)
                columns['SEG_DESTINO'           ].append(segment.to_label)
                columns['SEG_PERCENTUAL'        ].append(segment.pct * 100.0)
            
        df_entries = pd.DataFrame(columns)
        df_entries.to_excel(xlsx_writer, sheet_name='SEGMENTOS')
        
    def report_result(self, graph, sink_label, entries):
        logger.info('creating path report')
        paths = Path.build_paths(sink_label, graph)
        xlsx_writer = pd.ExcelWriter(self.path_report)
        # write accouting entries
        self.report_entries(xlsx_writer, entries)
        self.report_balances(xlsx_writer, graph)
        self.report_paths(xlsx_writer, paths)
        self.report_segments(xlsx_writer, paths)
        xlsx_writer.save()
    
    def run(self):
        logger.info('starting loader - version %d.%d.%d', *self.VERSION)    
        entries = self.get_entries()
        graph = self.create_graph(entries)
        self.generate_graph(graph)
        self.report_result(graph, sink_label=self.sink_label, entries=entries)
        logger.info('finished')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('entries_file',  type=str, help='spread sheet of accouting entries')
    parser.add_argument('sink_label',  type=str, help='sink node label')
    parser.add_argument('dot_file',  type=str, help='dot file name')
    parser.add_argument('path_report',  type=str, help='path report file name')
    args = parser.parse_args()
    app = App(args.entries_file, args.sink_label, args.dot_file, args.path_report)
    app.run()