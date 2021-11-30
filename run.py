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
from mafagrafos.cycle_remover import *

import mafagrafos.util as util

logger = util.get_logger('cycle_remover')

class App:
    
    VERSION = (0, 0, 0)
    ENTRIES_SHEET_COLUMNS = [ "dst", "src", "ammount", "date", "time", "type" ]
    
    def __init__(self, entries_file, sink_label, dot_file, path_report, reclimit):
        assert dot_file.endswith(".dot")
        self.entries_file   = entries_file
        self.sink_label     = sink_label
        self.dot_file       = dot_file
        self.path_report    = path_report
        self.reclimit       = reclimit
        
    def get_entries(self):
        logger.info('retrieving accounting entries from spreadsheet')
        parts = self.entries_file.split(":")
        assert len(parts) == 2
        entries_file = parts[0]
        sheet_name = parts[1]            
        df = pd.read_excel(entries_file, sheet_name, header=None, names=self.ENTRIES_SHEET_COLUMNS, skiprows=1).replace({np.nan: None})
        result = []
        for row in df.itertuples():
            entry = CoepEntry(
                row.dst
            ,   row.src if row.src else None
            ,   row.ammount
            ,   row.date
            ,   row.time
            ,   row.type
            )
            result.append(entry)
        return result
                        
    def create_graph(self, entries):
        logger.info('creating graph')
        cycle_remover = CycleRemover(logger)
        graph = cycle_remover.create_graph('Test graph', entries)
        logger.info('building paths')
        paths = cycle_remover.build_paths(graph, self.sink_label)
        return graph, paths
                            
    def report_entries(self, xlsx_writer, entries):
        # TODO: move to presenter
        logger.info('generating accounting entries sheet')
        columns = { 'DESTINO': [], 'ORIGEM': [], 'VALOR': [] }
        for entry in entries:
            columns['DESTINO'].append(entry.dst)
            columns['ORIGEM'].append(entry.src)
            columns['VALOR'].append(entry.ammount)
        df_entries = pd.DataFrame(columns)
        df_entries.to_excel(xlsx_writer, sheet_name='PARTIDAS')

    def report_balances(self, xlsx_writer, graph):
        # TODO: move to presenter
        logger.info('generating balance sheet')
        columns = {
            'ORIGEM'                : []
        ,   'ENTRADA_DIRETA'        : []
        ,   'SAIDA_DIRETA'          : []
        ,   'SALDO'                 : []
        }

        for node in graph.nodes:
            columns['ORIGEM'        ].append(node.label)
            columns['ENTRADA_DIRETA'].append(node.get_attr('inputed_ammount').current_value)
            columns['SAIDA_DIRETA'].append(node.get_attr('transferred_ammount').current_value)
            columns['SALDO'         ].append(node.get_attr('ammount').current_value)                
        df_balances = pd.DataFrame(columns)
        df_balances.to_excel(xlsx_writer, sheet_name='SALDOS')
        
    def report_paths(self, xlsx_writer, paths):
        # TODO: move to presenter
        logger.info('generating paths sheet')
        columns = {
            'CAMINHO'                   : []
        ,   'CAMINHO_PAI'               : []
        ,   'ORIGEM'                    : []
        ,   'DESTINO'                   : []
        ,   'TAMANHO'                   : []
        ,   'PERCENTUAL'                : []
        ,   'ENTRADA_DIRETA_ORIGEM'     : []
        ,   'SAIDA_DIRETA_ORIGEM'       : []
        ,   'SALDO_ORIGEM'              : []
        ,   'REPASSE_RESULTANTE'        : []
        ,   'MAX_T'                     : []
        }
        for path_id, path in enumerate(paths):
            columns['CAMINHO'                 ].append(path.path_id)
            columns['CAMINHO_PAI'             ].append(path.parent_path.path_id if path.parent_path else None )
            columns['ORIGEM'                  ].append(path.from_label)
            columns['DESTINO'                 ].append(path.to_label)
            columns['TAMANHO'                 ].append(path.length)
            columns['PERCENTUAL'              ].append(path.pct * 100)
            columns['ENTRADA_DIRETA_ORIGEM'   ].append(path.inputed_ammount)
            columns['SAIDA_DIRETA_ORIGEM'     ].append(path.transferred_ammount)
            columns['SALDO_ORIGEM'            ].append(path.ammount)
            columns['REPASSE_RESULTANTE'      ].append(path.inputed_ammount * path.pct)
            columns['MAX_T'                   ].append(path.max_t)
            
        df_paths = pd.DataFrame(columns)
        df_paths.to_excel(xlsx_writer, sheet_name='CAMINHOS')

    def report_result(self, graph, sink_label, entries, paths):
        # TODO: move to presenter
        presenter = GraphPresenter(graph)

        logger.info(f'generating dotfile')
        with open(self.dot_file, "w") as fh:
            print(presenter.generate_dot(show_times=False), file=fh)
        
        logger.info('creating path report')
        xlsx_writer = pd.ExcelWriter(self.path_report)
        # write accouting entries
        self.report_entries(xlsx_writer, entries)
        del entries
        self.report_balances(xlsx_writer, graph)
        del graph
        self.report_paths(xlsx_writer, paths)
        del paths
        xlsx_writer.save()
    
    #def get_node_times(self, node):
    #    times = set()
    #    for node_id in node.out_edges:
    #        out_node = node.graph.get_node_by_id(node_id)
    #        edge = node.graph.get_edge(node.label, out_node.label)
    #        assert edge
    #        edge_times = edge.get_attr('time')
    #        for time in edge_times:
    #            times.add(time)
    #    for node_id in node.in_edges:
    #        in_node = node.graph.get_node_by_id(node_id)
    #        edge = node.graph.get_edge(in_node.label, node.label)
    #        assert edge
    #        edge_times = edge.get_attr('time')
    #        for time in edge_times:
    #            times.add(time)
    #    return sorted(times)
        
    def run(self):
        logger.info('starting loader - version %d.%d.%d', *self.VERSION)    
        logger.info(f'setting recursion limit to {self.reclimit}')
        sys.setrecursionlimit(self.reclimit)
        entries = self.get_entries()
        graph, paths = self.create_graph(entries)
        self.report_result(graph, sink_label=self.sink_label, entries=entries, paths=paths)
        logger.info('finished')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--reclimit',   type=int, help='sys.setrecursionlimit(reclimit)', default=10000)
    parser.add_argument('entries_file', type=str, help='spread sheet of accouting entries')
    parser.add_argument('sink_label',   type=str, help='sink node label')
    parser.add_argument('dot_file',     type=str, help='dot file name')
    parser.add_argument('path_report',  type=str, help='path report file name')
    args = parser.parse_args()
    app = App(args.entries_file, args.sink_label, args.dot_file, args.path_report, args.reclimit)
    app.run()