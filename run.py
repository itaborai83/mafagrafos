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
    ENTRIES_SHEET_COLUMNS = [ "dst", "src", "ammount" ]
    
    def __init__(self, entries_file, sink_label, dot_file, path_report):
        assert dot_file.endswith(".dot")
        self.entries_file   = entries_file
        self.sink_label     = sink_label
        self.dot_file       = dot_file
        self.path_report    = path_report
        
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
                        
    def create_graph(self, entries):
        logger.info('creating graph')
        cycle_remover = CycleRemover(logger)
        graph = cycle_remover.create_graph('Test graph', entries)
        return graph
                            
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
        ,   'SALDO'                 : []
        }
        for node in graph.nodes:
            columns['ORIGEM'        ].append(node.label)
            columns['ENTRADA_DIRETA'].append(node.get_attr('inputed_ammount').current_value)
            columns['SALDO'         ].append(node.get_attr('ammount').current_value)
        df_entries = pd.DataFrame(columns)
        df_entries.to_excel(xlsx_writer, sheet_name='SALDOS')
        
    def report_paths(self, xlsx_writer, paths):
        # TODO: move to presenter
        logger.info('generating paths sheet')
        columns = {
            'CAMINHO'                   : []
        ,   'ORIGEM'                    : []
        ,   'DESTINO'                   : []
        ,   'PERCENTUAL'                : []
        ,   'ENTRADA_DIRETA_ORIGEM'     : []
        ,   'ENTRADA_INDIRETA_ORIGEM'   : []
        ,   'REPASSE_RESULTANTE'        : []
        ,   'MIN_T'                     : []
        ,   'MAX_T'                     : []
        }
        for path_id, path in enumerate(paths):
            pct = path.pct 
            columns['CAMINHO'                 ].append(path_id + 1)
            columns['ORIGEM'                  ].append(path.from_label)
            columns['DESTINO'                 ].append(path.to_label)
            columns['PERCENTUAL'              ].append(pct * 100)
            columns['ENTRADA_DIRETA_ORIGEM'   ].append(path.inputed_ammount)
            columns['ENTRADA_INDIRETA_ORIGEM' ].append(path.received_ammount)
            columns['REPASSE_RESULTANTE'      ].append((path.received_ammount + path.inputed_ammount * pct))
            columns['MIN_T'                   ].append(path.min_t)
            columns['MAX_T'                   ].append(path.max_t)
            
        df_entries = pd.DataFrame(columns)
        df_entries.to_excel(xlsx_writer, sheet_name='CAMINHOS')

    def report_segments(self, xlsx_writer, paths):
        # TODO: move to presenter
        logger.info('generating segments sheet')
        columns = {
            'CAMINHO'               : []
        ,   'ORIGEM'                : []
        ,   'DESTINO'               : []
        ,   'PERCENTUAL'            : []
        ,   'ENTRADA_DIRETA_ORIGEM' : []
        ,   'REPASSE_RESULTANTE'    : []
        ,   'MIN_T'                 : []
        ,   'MAX_T'                 : []
        ,   'SEGMENTO'              : []
        ,   'SEG_ORIGEM'            : []
        ,   'SEG_DESTINO'           : []
        ,   'SEG_PERCENTUAL'        : []
        ,   'SEG_MIN_T'             : []
        ,   'SEG_MAX_T'             : []
        }
        for path_id, path in enumerate(paths):
            pct = path.pct 
            for segment_id, segment in enumerate(path.segments):
                pct = segment.pct
                columns['CAMINHO'               ].append(path_id + 1)
                columns['ORIGEM'                ].append(path.from_label)
                columns['DESTINO'               ].append(path.to_label)
                columns['PERCENTUAL'            ].append(path.pct * 100.0)
                columns['ENTRADA_DIRETA_ORIGEM' ].append(path.inputed_ammount)
                columns['REPASSE_RESULTANTE'    ].append(path.inputed_ammount * path.pct)
                columns['MIN_T'                 ].append(path.segments[0].min_t)
                columns['MAX_T'                 ].append(path.segments[-1].max_t)
                columns['SEGMENTO'              ].append(segment_id + 1)
                columns['SEG_ORIGEM'            ].append(segment.from_label)
                columns['SEG_DESTINO'           ].append(segment.to_label)
                columns['SEG_PERCENTUAL'        ].append(segment.pct * 100.0)
                columns['SEG_MIN_T'             ].append(segment.min_t)
                columns['SEG_MAX_T'             ].append(segment.max_t)
            
        df_entries = pd.DataFrame(columns)
        df_entries.to_excel(xlsx_writer, sheet_name='SEGMENTOS')
        
    def report_result(self, graph, sink_label, entries):
        # TODO: move to presenter
        presenter = GraphPresenter(graph)
        presenter.compute_pcts()
        
        logger.info('creating path report')
        paths = graph.build_paths(sink_label)
        xlsx_writer = pd.ExcelWriter(self.path_report)
        # write accouting entries
        self.report_entries(xlsx_writer, entries)
        self.report_balances(xlsx_writer, graph)
        self.report_paths(xlsx_writer, paths)
        self.report_segments(xlsx_writer, paths)
        xlsx_writer.save()

        logger.info(f'generating dotfile')
        with open(self.dot_file, "w") as fh:
            print(presenter.generate_dot(), file=fh)
        
    
    def run(self):
        logger.info('starting loader - version %d.%d.%d', *self.VERSION)    
        entries = self.get_entries()
        graph = self.create_graph(entries)
        self.report_result(graph, sink_label=self.sink_label, entries=entries)
        logger.info('finished')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('entries_file', type=str, help='spread sheet of accouting entries')
    parser.add_argument('sink_label',   type=str, help='sink node label')
    parser.add_argument('dot_file',     type=str, help='dot file name')
    parser.add_argument('path_report',  type=str, help='path report file name')
    args = parser.parse_args()
    app = App(args.entries_file, args.sink_label, args.dot_file, args.path_report)
    app.run()