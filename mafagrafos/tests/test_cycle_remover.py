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
    
    #def test_it_transfer_the_current_balance_from_a_node_to_its_remapped_node(self):
    #    graph = Graph('Test graph', allow_cycles=False)
    #    entry = AccEntry('A', None, 100)
    #    self.cycrem.add_node_if_needed(graph, entry.dst)
    #    remapped_label = self.cycrem.add_remapped_label(entry.dst)
    #    self.cycrem.add_node_if_needed(graph, remapped_label)
    #    
    #    self.cycrem.transfer_ammount_through_time(graph, 'A')
    