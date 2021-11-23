import unittest
from mafagrafos.acc_entry import *
from mafagrafos.graph import *
from mafagrafos.cycle_remover import *


class TestCycleRemover(unittest.TestCase):

    def setUp(self):
        self.cycrem = CycleRemover()
    
    def tearDown(self):
        pass
        
    def test_it_retrieves_an_unmapped_label(self):
        label = self.cycrem.get_remapped_label('A')
        labels = self.cycrem.get_label_remappings('A')
        self.assertEqual(label, 'A')
        self.assertEqual(labels, ['A'])
        
    def test_it_remaps_a_label(self):
        self.cycrem.add_remapped_label('A')
        label = self.cycrem.get_remapped_label('A')
        labels = self.cycrem.get_label_remappings('A')
        self.assertEqual(label, 'A--1')
        self.assertEqual(labels, ['A', 'A--1'])

    def test_it_remaps_a_label_recursively(self):
        self.cycrem.add_remapped_label('A')
        self.cycrem.add_remapped_label('A')
        label = self.cycrem.get_remapped_label('A')
        labels = self.cycrem.get_label_remappings('A')
        self.assertEqual(label, 'A--2')
        self.assertEqual(labels, ['A', 'A--1', 'A--2'])
    
    def test_it_does_not_a_node_if_not_needed(self):
        graph = Graph('Test graph', allow_cycles=False)
        created_node = self.cycrem.add_node_if_needed(graph, label=None)
        self.assertEqual(created_node, None)
        
    def test_it_adds_a_node_if_needed(self):
        graph = Graph('Test graph', allow_cycles=False)
        created_node = self.cycrem.add_node_if_needed(graph, label='A')
        self.assertEqual(created_node.label, 'A')
        self.assertTrue('ammount'             in created_node.data)
        self.assertTrue('inputed_ammount'     in created_node.data)
        self.assertTrue('received_ammount'    in created_node.data)
        self.assertTrue('transferred_ammount' in created_node.data)
        self.assertEqual(len(created_node.data), 4)
    
    def test_it_handles_a_direct_loading(self):
        graph = Graph('Test graph', allow_cycles=False)
        entry = AccEntry('A', None, 100)
        created_node = self.cycrem.add_node_if_needed(graph, entry.dst)
        self.cycrem.handle_direct_loading(graph, entry)
        self.assertEqual(created_node.get_attr('ammount').current_value, entry.ammount)
        self.assertEqual(created_node.get_attr('inputed_ammount').current_value, entry.ammount)
        
    def test_it_handles_a_remapped_direct_loading(self):
        graph = Graph('Test graph', allow_cycles=False)
        entry = AccEntry('A', None, 100)
        self.cycrem.add_node_if_needed(graph, entry.dst)
        remapped_label = self.cycrem.add_remapped_label(entry.dst)
        self.cycrem.add_node_if_needed(graph, remapped_label)
        
        self.cycrem.handle_direct_loading(graph, entry)
        
        created_node = graph.get_node_by_label(remapped_label)
        self.assertEqual(created_node.get_attr('ammount').current_value, entry.ammount)
        self.assertEqual(created_node.get_attr('inputed_ammount').current_value, entry.ammount)
    
    def test_it_transfer_the_current_balance_from_a_node_to_its_remapped_node(self):
        graph = Graph('Test graph', allow_cycles=False)
        entry = AccEntry('A', None, 100)
        orig_node = self.cycrem.add_node_if_needed(graph, entry.dst)
        self.cycrem.handle_direct_loading(graph, entry)
        remapped_label = self.cycrem.add_remapped_label(entry.dst)
        new_node = self.cycrem.add_node_if_needed(graph, remapped_label)
                
        self.cycrem.transfer_ammount_through_time(graph, 'A')
        
        edge = graph.get_edge('A', 'A--1')
        self.assertEqual(edge.get_attr('ammount').current_value, 100.0)
        self.assertEqual(orig_node.get_attr('ammount').current_value, 0.0)
        self.assertEqual(orig_node.get_attr('transferred_ammount').current_value, 100.0)
        self.assertEqual(new_node.get_attr('ammount').current_value, 100.0)
        self.assertEqual(new_node.get_attr('received_ammount').current_value, 100.0)
    
    def test_it_handles_an_account_transfer(self):
        graph = Graph('Test graph', allow_cycles=False)
        entry_1 = AccEntry('B', None, 100.0)
        entry_2 = AccEntry('A', 'B', 100.0)
        src_node = self.cycrem.add_node_if_needed(graph, 'B')
        dst_node = self.cycrem.add_node_if_needed(graph, 'A')
        self.cycrem.handle_direct_loading(graph, entry_1)
        
        self.cycrem.handle_account_transfer(graph, entry_2)
        
        edge = graph.get_edge('B', 'A')
        self.assertEqual(edge.get_attr('ammount').current_value, 100.0)
        self.assertEqual(src_node.get_attr('ammount').current_value, 0.0)
        self.assertEqual(src_node.get_attr('transferred_ammount').current_value, 100.0)
        self.assertEqual(dst_node.get_attr('ammount').current_value, 100.0)
        self.assertEqual(dst_node.get_attr('received_ammount').current_value, 100.0)
    
    def test_it_handles_an_account_transfer_that_would_create_a_cycle(self):
        graph = Graph('Test graph', allow_cycles=False)
        entry_1 = AccEntry('B', None, 100.0)
        entry_2 = AccEntry('A', 'B', 100.0)
        entry_3 = AccEntry('B', 'A', 100.0)
        node_a = self.cycrem.add_node_if_needed(graph, 'A')
        node_b = self.cycrem.add_node_if_needed(graph, 'B')
        self.cycrem.handle_direct_loading(graph, entry_1)
        self.cycrem.handle_account_transfer(graph, entry_2)
        
        self.cycrem.handle_account_transfer(graph, entry_3)

        edge = graph.get_edge('B', 'A')
        node_b_prime = graph.get_node_by_label('B--1')
        
        self.assertEqual(edge.get_attr('ammount').current_value,                        100.0)
        
        self.assertEqual(node_b.get_attr('ammount').current_value,                        0.0)
        self.assertEqual(node_b.get_attr('transferred_ammount').current_value,          100.0)
        self.assertEqual(node_b.get_attr('received_ammount').current_value,               0.0)
        
        self.assertEqual(node_a.get_attr('ammount').current_value,                        0.0)
        self.assertEqual(node_a.get_attr('transferred_ammount').current_value,          100.0)
        self.assertEqual(node_a.get_attr('received_ammount').current_value,             100.0)
                
        edge = graph.get_edge('A', 'B--1')
        
        self.assertEqual(edge.get_attr('ammount').current_value, 100.0)        
        self.assertEqual(node_b_prime.get_attr('ammount').current_value,                100.0)
        self.assertEqual(node_b_prime.get_attr('transferred_ammount').current_value,      0.0)
        self.assertEqual(node_b_prime.get_attr('received_ammount').current_value,       100.0)
                        
    def test_it_handles_an_account_transfer_that_would_create_a_cycle_and_forwards_the_balance_to_the_remapped_node(self):
        graph = Graph('Test graph', allow_cycles=False)
        entry_1 = AccEntry('B', None, 100.0)
        entry_2 = AccEntry('A', 'B', 50.0)
        entry_3 = AccEntry('B', 'A', 25.0)
        node_a = self.cycrem.add_node_if_needed(graph, 'A')
        node_b = self.cycrem.add_node_if_needed(graph, 'B')
        self.cycrem.handle_direct_loading(graph, entry_1)
        self.cycrem.handle_account_transfer(graph, entry_2)
        
        self.cycrem.handle_account_transfer(graph, entry_3)

        edge = graph.get_edge('B', 'A')
        node_b_prime = graph.get_node_by_label('B--1')
        
        self.assertEqual(edge.get_attr('ammount').current_value,                         50.0)
        
        self.assertEqual(node_b.get_attr('ammount').current_value,                        0.0)
        self.assertEqual(node_b.get_attr('transferred_ammount').current_value,          100.0)
        self.assertEqual(node_b.get_attr('received_ammount').current_value,               0.0)
        
        self.assertEqual(node_a.get_attr('ammount').current_value,                       25.0)
        self.assertEqual(node_a.get_attr('transferred_ammount').current_value,           25.0)
        self.assertEqual(node_a.get_attr('received_ammount').current_value,              50.0)
                
        edge = graph.get_edge('A', 'B--1')
        
        self.assertEqual(edge.get_attr('ammount').current_value, 25.0)        
        self.assertEqual(node_b_prime.get_attr('ammount').current_value,                 75.0)
        self.assertEqual(node_b_prime.get_attr('transferred_ammount').current_value,      0.0)
        self.assertEqual(node_b_prime.get_attr('received_ammount').current_value,        75.0)
    
    def test_it_compute_the_edge_pct_of_a_root_edge(self):
        graph = Graph('Test graph', allow_cycles=False)
        entry_1 = AccEntry('C', None, 100.0)
        entry_2 = AccEntry('A', 'C', 25.0)
        entry_3 = AccEntry('B', 'C', 50.0)
        self.cycrem.handle_entry(graph, entry_1)
        self.cycrem.handle_entry(graph, entry_2)
        self.cycrem.handle_entry(graph, entry_3)
        node_a = graph.get_node_by_label('A')
        node_b = graph.get_node_by_label('B')
        node_c = graph.get_node_by_label('C')
        edge_ca = graph.get_edge('C', 'A')
        edge_cb = graph.get_edge('C', 'B')
        
        #print()
        #for i in range(self.cycrem.current_time + 1):
        #    for node in graph.nodes:
        #        node_ammount        = node.get_attr('ammount').value_at(i)
        #        inputed_ammount     = node.get_attr('inputed_ammount').value_at(i)
        #        transferred_ammount = node.get_attr('transferred_ammount').value_at(i)
        #        received_ammount    = node.get_attr('received_ammount').value_at(i)
        #        print(f"{node.label}@{i}")
        #        print(f"\tammount             = {node_ammount}")
        #        print(f"\tinputed_ammount     = {inputed_ammount}")
        #        print(f"\ttransferred_ammount = {transferred_ammount}")
        #        print(f"\treceived_ammount    = {received_ammount}")        
        #print()
        
        edge_ca_pct, max_time = self.cycrem.compute_edge_pct(node_c, edge_ca, node_a, None)
        self.assertEqual(edge_ca_pct, 25.0/100.0)
        self.assertEqual(max_time, 1)
        
        edge_cb_pct, max_time = self.cycrem.compute_edge_pct(node_c, edge_cb, node_b, None)
        self.assertEqual(edge_cb_pct, 50.0/(75.0 + 25.0))
        self.assertEqual(max_time, 2)

    
    def test_it_compute_the_edge_pct_of_a_non_root_edge(self):
        graph = Graph('Test graph', allow_cycles=False)
        entry_1 = AccEntry('C', None, 100.0)
        entry_2 = AccEntry('B', 'C', 50.0)
        entry_3 = AccEntry('A', 'B', 25.0)
        entry_4 = AccEntry('B', 'C', 50.0)
        self.cycrem.handle_entry(graph, entry_1)
        self.cycrem.handle_entry(graph, entry_2)
        self.cycrem.handle_entry(graph, entry_3)
        self.cycrem.handle_entry(graph, entry_4)
        node_a = graph.get_node_by_label('A')
        node_b = graph.get_node_by_label('B')
        node_c = graph.get_node_by_label('C')
        edge_cb = graph.get_edge('C', 'B')
        edge_ba = graph.get_edge('B', 'A')
        parent_max_time = edge_ba.get_attr('time')[-1]
        
        #print()
        #for i in range(self.cycrem.current_time):
        #    for node in graph.nodes:
        #        node_ammount        = node.get_attr('ammount').value_at(i)
        #        inputed_ammount     = node.get_attr('inputed_ammount').value_at(i)
        #        transferred_ammount = node.get_attr('transferred_ammount').value_at(i)
        #        received_ammount    = node.get_attr('received_ammount').value_at(i)
        #        print(f"{node.label}@{i}")
        #        print(f"\tammount             = {node_ammount}")
        #        print(f"\tinputed_ammount     = {inputed_ammount}")
        #        print(f"\ttransferred_ammount = {transferred_ammount}")
        #        print(f"\treceived_ammount    = {received_ammount}")        
        #print()
        
        edge_cb_pct, max_time = self.cycrem.compute_edge_pct(node_c, edge_cb, node_b, parent_max_time)
        self.assertEqual(edge_cb_pct, 50.0/100.0)
        self.assertEqual(max_time, 1)
        
        
    def test_it_compute_the_edge_pct_of_an_inconsistent_edge(self):    
        graph = Graph('Test graph', allow_cycles=False)
        entry_1 = AccEntry('B', None, 100.0)
        entry_2 = AccEntry('C', None, 100.0)
        entry_3 = AccEntry('A', 'B', 50.0)
        entry_4 = AccEntry('B', 'C', 50.0)
        self.cycrem.handle_entry(graph, entry_1)
        self.cycrem.handle_entry(graph, entry_2)
        self.cycrem.handle_entry(graph, entry_3)
        self.cycrem.handle_entry(graph, entry_4)
        node_a = graph.get_node_by_label('A')
        node_b = graph.get_node_by_label('B')
        node_c = graph.get_node_by_label('C')
        edge_cb = graph.get_edge('C', 'B')
        edge_ba = graph.get_edge('B', 'A')
        parent_max_time = edge_ba.get_attr('time')[-1]
    
        #print()
        #for i in range(self.cycrem.current_time):
        #    for node in graph.nodes:
        #        node_ammount        = node.get_attr('ammount').value_at(i)
        #        inputed_ammount     = node.get_attr('inputed_ammount').value_at(i)
        #        transferred_ammount = node.get_attr('transferred_ammount').value_at(i)
        #        received_ammount    = node.get_attr('received_ammount').value_at(i)
        #        print(f"{node.label}@{i}")
        #        print(f"\tammount             = {node_ammount}")
        #        print(f"\tinputed_ammount     = {inputed_ammount}")
        #        print(f"\ttransferred_ammount = {transferred_ammount}")
        #        print(f"\treceived_ammount    = {received_ammount}")        
        #print()
        
        edge_cb_pct, max_time = self.cycrem.compute_edge_pct(node_c, edge_cb, node_b, parent_max_time)
        self.assertEqual(edge_cb_pct, 0.0)
        self.assertEqual(max_time, None)
    