import unittest
from mafagrafos.graph import *
from mafagrafos.presenter import *
from mafagrafos.acc_entry import *

class TestGraphPresenter(unittest.TestCase):
    
    SHOW_DOT = False

    def setUp(self):
        self.graph = self.get_test_graph_01()
        self.presenter = GraphPresenter(self.graph)
        
    def get_test_graph_01(self):
        graph = Graph('Test graph', allow_cycles=True)
        entries_list = AccEntryList.get_test_case_01()
        # add nodes
        for node_label in entries_list.nodes:
            node = graph.add_node(node_label)
            node.set_attr('ammount', 0.0)
        
        # add edges
        graph.start_topo_sorting()
        for i, entry in enumerate(entries_list.entries):
            dst_label = entry.dst
            dst_node = graph.get_node_by_label(dst_label)
            if entry.src is None:
               ammount = dst_node.get_attr('ammount')
               dst_node.set_attr('ammount', ammount + entry.ammount)
            else:
                src_label = entry.src
                src_node = graph.get_node_by_label(src_label)
                dst_ammount = dst_node.get_attr('ammount')
                dst_node.set_attr('ammount', dst_ammount + entry.ammount)
                src_ammount = src_node.get_attr('ammount')
                src_node.set_attr('ammount', src_ammount - entry.ammount)
                edge = graph.get_edge(src_label, dst_label)
                time = "T"+str(i)
                if edge is None:
                    edge = graph.add_edge(src_label, dst_label)
                    edge.set_attr('ammount', entry.ammount)
                    edge.set_attr('time', time)
                else:
                    edge_ammount = edge.get_attr('ammount')
                    edge.set_attr('ammount', edge_ammount + entry.ammount)
                    old_time = edge.get_attr('time')
                    edge.set_attr('time', old_time + ", " + time)
                    
        return graph
    
    def tearDown(self):
        pass
        
    def test_it_generates_a_dot_graph(self):
        if self.SHOW_DOT:
            print()
            print("////////////////////////////////////////////////////////////////")
            print("// BEGIN DOT ///////////////////////////////////////////////////")
            print("////////////////////////////////////////////////////////////////")
            print(self.presenter.generate_dot())
            print("////////////////////////////////////////////////////////////////")
            print("// END DOT /////////////////////////////////////////////////////")
            print("////////////////////////////////////////////////////////////////")