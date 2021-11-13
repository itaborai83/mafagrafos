import unittest
from mafagrafos.graph import *

class TestNode(unittest.TestCase):

    def setUp(self):
        pass
    
    def tearDown(self):
        pass
        
    def test_it_adds_a_node(self):
        g = Graph("Test Graph")
        
        created_node = g.add_node("CJ10")
        self.assertEqual(g, created_node.graph)
        
        self.assertEqual(created_node.node_id, 0)
        self.assertEqual(created_node.label, "CJ10")
        self.assertEqual(g.next_node_id, 1)
        cj10_node = g.get_node_by_label("CJ10")
        self.assertEqual(created_node, cj10_node)
        cj10_node = g.get_node_by_id(0)
        self.assertEqual(created_node, cj10_node)
        
        created_node = g.add_node("CJ11")
        self.assertEqual(g, created_node.graph)
        
        self.assertEqual(created_node.node_id, 1)
        self.assertEqual(created_node.label, "CJ11")
        self.assertEqual(g.next_node_id, 2)
        cj11_node = g.get_node_by_label("CJ11")
        self.assertEqual(created_node, cj11_node)
        cj11_node = g.get_node_by_id(1)
        self.assertEqual(created_node, cj11_node)
    