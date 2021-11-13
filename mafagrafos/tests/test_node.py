import unittest
from mafagrafos.node import *

class TestNode(unittest.TestCase):

    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_it_implements_equality(self):
        a = Node(0, "A")
        b = Node(0, "B")
        another_a = Node(0, "A")
        wrong_a = Node(2, "A")
        self.assertEqual(a, a)
        self.assertEqual(a, another_a)
        self.assertNotEqual(a, b)
        self.assertNotEqual(a, wrong_a)
    
    def test_it_converts_to_string(self):
        a = Node(0, "A")
        self.assertEqual(str(a), "<Node node_id=0, label='A'>")
    
    def test_it_adds_an_out_edge(self):
        node_a = Node(0, "A")
        node_b = Node(1, "B")
        self.assertFalse(node_a.has_out_edge(node_b.node_id))
        node_a.add_out_edge(node_b.node_id)
        self.assertTrue(node_a.has_out_edge(node_b.node_id))

    def test_it_adds_an_in_edge(self):
        node_a = Node(0, "A")
        node_b = Node(1, "B")
        self.assertFalse(node_a.has_out_edge(node_b.node_id))
        node_a.add_out_edge(node_b.node_id)
        self.assertTrue(node_a.has_out_edge(node_b.node_id))
    
    def test_it_removes_an_out_edge(self):
        node_a = Node(0, "A")
        node_b = Node(1, "B")
        node_a.add_out_edge(node_b.node_id)
        self.assertTrue(node_a.has_out_edge(node_b.node_id))
        node_a.del_out_edge(node_b.node_id)
        self.assertFalse(node_a.has_out_edge(node_b.node_id))
        
    def test_it_removes_an_in_edge(self):
        node_a = Node(0, "A")
        node_b = Node(1, "B")
        node_a.add_in_edge(node_b.node_id)
        self.assertTrue(node_a.has_in_edge(node_b.node_id))
        node_a.del_in_edge(node_b.node_id)
        self.assertFalse(node_a.has_in_edge(node_b.node_id))
        