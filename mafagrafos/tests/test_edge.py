import unittest
from mafagrafos.edge import *

class TestEdge(unittest.TestCase):

    def setUp(self):
        pass
    
    def tearDown(self):
        pass
        
    def test_it_implements_equality(self):
        edge1 = Edge(from_id=0, to_id=1, label="test edge 1")
        edge2 = Edge(from_id=1, to_id=2, label="test edge 2")
        edge3 = Edge(from_id=0, to_id=1, label="test edge 1")
        self.assertEqual(edge1, edge1)
        self.assertNotEqual(edge1, edge2)
        self.assertEqual(edge1, edge3)