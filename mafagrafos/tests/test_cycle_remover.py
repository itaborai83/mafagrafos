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
        entry = CoepEntry('A', None, 100)
        created_node = self.cycrem.add_node_if_needed(graph, entry.dst)
        self.cycrem.handle_direct_loading(graph, entry)
        self.assertEqual(created_node.get_attr('ammount').current_value, entry.ammount)
        self.assertEqual(created_node.get_attr('inputed_ammount').current_value, entry.ammount)
        
    def test_it_handles_a_remapped_direct_loading(self):
        graph = Graph('Test graph', allow_cycles=False)
        entry = CoepEntry('A', None, 100)
        self.cycrem.add_node_if_needed(graph, entry.dst)
        remapped_label = self.cycrem.add_remapped_label(entry.dst)
        self.cycrem.add_node_if_needed(graph, remapped_label)
        
        self.cycrem.handle_direct_loading(graph, entry)
        
        created_node = graph.get_node_by_label(remapped_label)
        self.assertEqual(created_node.get_attr('ammount').current_value, entry.ammount)
        self.assertEqual(created_node.get_attr('inputed_ammount').current_value, entry.ammount)
    
    def test_it_transfer_the_current_balance_from_a_node_to_its_remapped_node(self):
        graph = Graph('Test graph', allow_cycles=False)
        entry = CoepEntry('A', None, 100)
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
        entry_1 = CoepEntry('B', None, 100.0)
        entry_2 = CoepEntry('A', 'B', 100.0)
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
        entry_1 = CoepEntry('B', None, 100.0)
        entry_2 = CoepEntry('A', 'B', 100.0)
        entry_3 = CoepEntry('B', 'A', 100.0)
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
        entry_1 = CoepEntry('B', None, 100.0)
        entry_2 = CoepEntry('A', 'B', 50.0)
        entry_3 = CoepEntry('B', 'A', 25.0)
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
        entry_1 = CoepEntry('C', None, 100.0)
        entry_2 = CoepEntry('A', 'C', 25.0)
        entry_3 = CoepEntry('B', 'C', 50.0)
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
        entry_1 = CoepEntry('C', None, 100.0)
        entry_2 = CoepEntry('B', 'C', 50.0)
        entry_3 = CoepEntry('A', 'B', 25.0)
        entry_4 = CoepEntry('B', 'C', 50.0)
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
        entry_1 = CoepEntry('B', None, 100.0)
        entry_2 = CoepEntry('C', None, 100.0)
        entry_3 = CoepEntry('A', 'B', 50.0)
        entry_4 = CoepEntry('B', 'C', 50.0)
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
    
    def test_it_lists_all_single_segment_paths(self):
        graph = Graph('Test graph', allow_cycles=False)
        entry_1 = CoepEntry('B', None, 100.0)
        entry_2 = CoepEntry('C', None, 100.0)
        entry_3 = CoepEntry('D', None, 100.0)
        entry_4 = CoepEntry('A', 'B', 25.0)
        entry_5 = CoepEntry('A', 'C', 50.0)
        entry_6 = CoepEntry('A', 'D', 75.0)
        self.cycrem.handle_entry(graph, entry_1)
        self.cycrem.handle_entry(graph, entry_2)
        self.cycrem.handle_entry(graph, entry_3)
        self.cycrem.handle_entry(graph, entry_4)
        self.cycrem.handle_entry(graph, entry_5)
        self.cycrem.handle_entry(graph, entry_6)
                
        paths = self.cycrem.build_paths(graph, 'A')
        #print()
        #for path in paths:
        #    print(path.show())
        self.assertEqual(len(paths), 3)

        path_01 = paths[0]
        self.assertEqual(path_01.from_label, "B")
        self.assertEqual(path_01.to_label, "A")
        self.assertEqual(path_01.min_t, 3)
        self.assertEqual(path_01.max_t, 3)
        self.assertEqual(path_01.segment_count, 1)
        self.assertEqual(path_01.inputed_ammount, 100.0)
        self.assertEqual(path_01.received_ammount, 0)
        self.assertEqual(path_01.ammount, 75.0)
        self.assertEqual(path_01.transferred_ammount, 25.0)
        self.assertEqual(path_01.pct, 25.0 / (25.0 + 75.0))

        path_02 = paths[1]
        self.assertEqual(path_02.from_label, "C")
        self.assertEqual(path_02.to_label, "A")
        self.assertEqual(path_02.min_t, 4)
        self.assertEqual(path_02.max_t, 4)
        self.assertEqual(path_02.segment_count, 1)
        self.assertEqual(path_02.inputed_ammount, 100.0)
        self.assertEqual(path_02.received_ammount, 0)
        self.assertEqual(path_02.ammount, 50.0)
        self.assertEqual(path_02.transferred_ammount, 50.0)
        self.assertEqual(path_02.pct, 50.0 / (50.0 + 50.0))

        path_03 = paths[2]
        self.assertEqual(path_03.from_label, "D")
        self.assertEqual(path_03.to_label, "A")
        self.assertEqual(path_03.min_t, 5)
        self.assertEqual(path_03.max_t, 5)
        self.assertEqual(path_03.segment_count, 1)
        self.assertEqual(path_03.inputed_ammount, 100.0)
        self.assertEqual(path_03.received_ammount, 0)
        self.assertEqual(path_03.ammount, 25.0)
        self.assertEqual(path_03.transferred_ammount, 75.0)
        self.assertEqual(path_03.pct, 75.0 / (75.0 + 25.0))        
    
    def test_it_lists_all_double_segment_paths(self):
        graph = Graph('Test graph', allow_cycles=False)
        entry_1 = CoepEntry('D', None, 100.0)
        entry_2 = CoepEntry('B', 'D', 50.0)
        entry_3 = CoepEntry('C', 'D', 50.0)
        entry_4 = CoepEntry('A', 'B', 25.0)
        entry_5 = CoepEntry('A', 'C', 25.0)
        self.cycrem.handle_entry(graph, entry_1)
        self.cycrem.handle_entry(graph, entry_2)
        self.cycrem.handle_entry(graph, entry_3)
        self.cycrem.handle_entry(graph, entry_4)
        self.cycrem.handle_entry(graph, entry_5)
        
        paths = self.cycrem.build_paths(graph, 'A')
        #print()
        #for path in paths:
        #    print(path.show())
        
        self.assertEqual(len(paths), 4)
        
        path_01 = paths[0]
        self.assertEqual(path_01.from_label, "B")
        self.assertEqual(path_01.to_label, "A")
        self.assertEqual(path_01.min_t, 3)
        self.assertEqual(path_01.max_t, 3)
        self.assertEqual(path_01.segment_count, 1)
        self.assertEqual(path_01.inputed_ammount, 0.0)
        self.assertEqual(path_01.received_ammount, 50.0)
        self.assertEqual(path_01.ammount, 25.0)
        self.assertEqual(path_01.transferred_ammount, 25.0)
        self.assertEqual(path_01.pct, 25.0 / (25.0 + 25.0))
        
        path_02 = paths[1]
        self.assertEqual(path_02.from_label, "D")
        self.assertEqual(path_02.to_label, "A")
        self.assertEqual(path_02.min_t, 1)
        self.assertEqual(path_02.max_t, 3)
        self.assertEqual(path_02.segment_count, 2)
        self.assertEqual(path_02.inputed_ammount, 100.0)
        self.assertEqual(path_02.received_ammount, 0.0)
        self.assertEqual(path_02.ammount, 50.0)
        self.assertEqual(path_02.transferred_ammount, 50.0)
        self.assertEqual(path_02.pct, path_01.pct * (50.0 / (50.0 + 50.0)))

        path_03 = paths[2]
        self.assertEqual(path_03.from_label, "C")
        self.assertEqual(path_03.to_label, "A")
        self.assertEqual(path_03.min_t, 4)
        self.assertEqual(path_03.max_t, 4)
        self.assertEqual(path_03.segment_count, 1)
        self.assertEqual(path_03.inputed_ammount, 0.0)
        self.assertEqual(path_03.received_ammount, 50.0)
        self.assertEqual(path_03.ammount, 25.0)
        self.assertEqual(path_03.transferred_ammount, 25.0)
        self.assertEqual(path_03.pct, 25.0 / (25.0 + 25.0))

        path_04 = paths[3]
        self.assertEqual(path_04.from_label, "D")
        self.assertEqual(path_04.to_label, "A")
        self.assertEqual(path_04.min_t, 2)
        self.assertEqual(path_04.max_t, 4)
        self.assertEqual(path_04.segment_count, 2)
        self.assertEqual(path_04.inputed_ammount, 100.0)
        self.assertEqual(path_04.received_ammount, 0.0)
        self.assertEqual(path_04.ammount, 0.0)
        self.assertEqual(path_04.transferred_ammount, 100.0)
        self.assertEqual(path_04.pct, path_03.pct * (50.0 / (0.0 + 100.0)))
    
    @unittest.skip
    def test_it_lists_all_paths_ending_in_a_given_node__complex(self):
        graph = Graph('Test graph', allow_cycles=False)
        entry_1 = CoepEntry('D', None, 100.0)
        entry_2 = CoepEntry('E', None, 50.0)
        entry_3 = CoepEntry('C', 'D', 25.0)
        entry_4 = CoepEntry('A', 'D', 25.0)
        entry_5 = CoepEntry('A', 'C', 25.0)
        entry_6 = CoepEntry('B', 'D', 25.0)
        entry_7 = CoepEntry('D', 'E', 50.0)
        entry_8 = CoepEntry('A', 'B', 12.5)
        entry_9 = CoepEntry('B', 'D', 25.0)
        self.cycrem.handle_entry(graph, entry_1)
        self.cycrem.handle_entry(graph, entry_2)
        self.cycrem.handle_entry(graph, entry_3)
        self.cycrem.handle_entry(graph, entry_4)
        self.cycrem.handle_entry(graph, entry_5)
        self.cycrem.handle_entry(graph, entry_6)
        self.cycrem.handle_entry(graph, entry_7)
        self.cycrem.handle_entry(graph, entry_8)
        self.cycrem.handle_entry(graph, entry_9)
        self.cycrem.handle_entry(graph, entry_1)
        
        paths = self.cycrem.build_paths(graph, 'A')
        print()
        for path in paths:
            print(path.show())
        
        path_01 = paths[0]
        self.assertEqual(path_01.from_label, "D")
        self.assertEqual(path_01.to_label, "A")
        self.assertEqual(path_01.min_t, 2)
        self.assertEqual(path_01.max_t, 8)
        self.assertEqual(path_01.segment_count, 1)
        self.assertEqual(path_01.inputed_ammount, 100.0)
        self.assertEqual(path_01.received_ammount, 0)
        self.assertEqual(path_01.ammount, 50.0)
        self.assertEqual(path_01.transferred_ammount, 50.0)
        self.assertEqual(path_01.pct, 25.0 / (50.0 + 50.0))
        
        path_02 = paths[1]
        self.assertEqual(path_02.from_label, "C")
        self.assertEqual(path_02.to_label, "A")
        self.assertEqual(path_02.min_t, 4)
        self.assertEqual(path_02.max_t, 4)
        self.assertEqual(path_02.segment_count, 1)
        self.assertEqual(path_02.inputed_ammount, 0.0)
        self.assertEqual(path_02.received_ammount, 25.0)
        self.assertEqual(path_02.ammount, 0.0)
        self.assertEqual(path_02.transferred_ammount, 25.0)
        self.assertEqual(path_02.pct, 25.0 / 25.0)

        path_03 = paths[2]
        self.assertEqual(path_03.from_label, "D")
        self.assertEqual(path_03.to_label, "A")
        self.assertEqual(path_03.min_t, 2)
        self.assertEqual(path_03.max_t, 4)
        self.assertEqual(path_03.segment_count, 2)
        self.assertEqual(path_03.inputed_ammount, 100.0)
        self.assertEqual(path_03.received_ammount, 0.0)
        self.assertEqual(path_03.ammount, 75.0)
        self.assertEqual(path_03.transferred_ammount, 25.0)
        self.assertEqual(path_03.pct, 25.0 / (50.0 + 50.0))

        path_04 = paths[3]
        self.assertEqual(path_04.from_label, "B")
        self.assertEqual(path_04.to_label, "A")
        self.assertEqual(path_04.min_t, 7)
        self.assertEqual(path_04.max_t, 7)
        self.assertEqual(path_04.segment_count, 1)
        self.assertEqual(path_04.inputed_ammount, 0.0)
        self.assertEqual(path_04.received_ammount, 25.0)
        self.assertEqual(path_04.ammount, 12.5)
        self.assertEqual(path_04.transferred_ammount, 12.5)
        self.assertEqual(path_04.pct, 12.5 / (12.5 + 12.5))
        
        path_05 = paths[4]
        self.assertEqual(path_05.from_label, "D")
        self.assertEqual(path_05.to_label, "A")
        self.assertEqual(path_05.min_t, 2)
        self.assertEqual(path_05.max_t, 7) # should this be 4??
        self.assertEqual(path_05.segment_count, 2)
        self.assertEqual(path_05.inputed_ammount, 100.0)
        self.assertEqual(path_05.received_ammount, 0.0)
        self.assertEqual(path_05.ammount, 25.0)
        self.assertEqual(path_05.transferred_ammount, 75.0)
        self.assertEqual(path_05.pct, 12.5 / (25.0 + 75.0))        
        
        path_06 = paths[5]
        self.assertEqual(path_06.from_label, "E")
        self.assertEqual(path_06.to_label, "A")
        self.assertEqual(path_06.min_t, 6)
        self.assertEqual(path_06.max_t, 7)
        self.assertEqual(path_06.segment_count, 3)
        self.assertEqual(path_06.inputed_ammount, 50.0)
        self.assertEqual(path_06.received_ammount, 0.0)
        self.assertEqual(path_06.ammount, 0.0)
        self.assertEqual(path_06.transferred_ammount, 50.0)
        self.assertEqual(path_06.pct, 0.125)