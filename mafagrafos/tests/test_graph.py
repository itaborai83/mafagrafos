import unittest
from mafagrafos.graph import *

class TestNodeVisitor(unittest.TestCase):
    
    def setUp(self):
        self.graph = Graph('Test graph')
        self.visitor = NodeVisitor(self.graph)
    
    def tearDown(self):
        pass
    
    def test_it_visits_a_node(self):
        self.visitor.visit(node_id=100)
        self.assertTrue(self.visitor.has_visited(node_id=100))
    
    def test_it_unvisits_a_node(self):
        self.visitor.visit(node_id=100)
        self.assertTrue(self.visitor.has_visited(node_id=100))
        self.visitor.unvisit(node_id=100)
        self.assertFalse(self.visitor.has_visited(node_id=100))

    def test_it_unvisits_a_node(self):
        self.visitor.visit(node_id=100)
        self.assertTrue(self.visitor.has_visited(node_id=100))
        self.visitor.unvisit(node_id=100)
        self.assertFalse(self.visitor.has_visited(node_id=100))
    
    def test_it_clears_visited_nodes(self):
        self.visitor.visit(node_id=100)
        self.visitor.visit(node_id=200)
        self.assertTrue(self.visitor.has_visited(node_id=100))
        self.assertTrue(self.visitor.has_visited(node_id=200))
        self.visitor.clear_visited()
        self.assertFalse(self.visitor.has_visited(node_id=100))
        self.assertFalse(self.visitor.has_visited(node_id=200))
        
class TestGraph(unittest.TestCase):

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
    
    def test_it_adds_an_edge(self):
        g = Graph("Test Graph")
        node_cj10 = g.add_node("CJ10")
        node_cj11 = g.add_node("CJ11")
        edge = g.add_edge(node_cj10.label, node_cj11.label, "T0")
        self.assertEqual(g, edge.graph)
        self.assertTrue(g.has_edge("CJ10", "CJ11"))
        self.assertFalse(g.has_edge("CJ11", "CJ10"))
        self.assertEqual(edge, g.get_edge("CJ10", "CJ11"))

class TestGraphCycles(unittest.TestCase):

    def setUp(self):
        self.graph = Graph('Test graph')
        # level 1
        self.graph.add_node("A") # node_id = 0 
        # level 2
        self.graph.add_node("B") # node_id = 1
        self.graph.add_node("C") # node_id = 2
        # level 3
        self.graph.add_node("D") # node_id = 3
        self.graph.add_node("E") # node_id = 4
        # level 4
        self.graph.add_node("F") # node_id = 5
    
    def tearDown(self):
        pass
    
    def test_it_adds_an_edge(self):
        edge = self.graph.add_edge("A", "B")
        self.assertEqual(edge.edge_key(), (0, 1))

    def test_it_adds_an_edge_incrementally(self):
        graph = Graph("Test graph")
        graph.add_node("A")
        graph.add_node("B")
        edge = graph.add_edge("A", "B")
        self.assertEqual(edge.edge_key(), (0, 1))
        
    def test_it_creates_a_line_graph(self):
        edge = self.graph.add_edge("A", "B")
        self.assertEqual(edge.edge_key(), (0, 1))
        edge = self.graph.add_edge("B", "D")
        self.assertEqual(edge.edge_key(), (1, 3))
        edge = self.graph.add_edge("D", "F")
        self.assertEqual(edge.edge_key(), (3, 5))

    def test_it_creates_a_line_graph_incrementally(self):
        graph = Graph("Test graph")
        graph.add_node("A")
        graph.add_node("B")
        edge = graph.add_edge("A", "B")
        self.assertEqual(edge.edge_key(), (0, 1))
        graph.add_node("D")
        edge = graph.add_edge("B", "D")
        self.assertEqual(edge.edge_key(), (1, 2))
        graph.add_node("F")
        edge = graph.add_edge("D", "F")
        self.assertEqual(edge.edge_key(), (2, 3))
        
    def test_it_adds_an_edge_affecting_the_topo_sort(self):
        edge = self.graph.add_edge("B", "A")
        self.assertEqual(edge.edge_key(), (1, 0))

    def test_it_adds_an_edge_affecting_the_topo_sort_incrementally(self):
        graph = Graph("Test graph")
        graph.add_node("A")
        graph.add_node("B")
        edge = graph.add_edge("B", "A")
        self.assertEqual(edge.edge_key(), (1, 0))
        
    def test_it_creates_a_dag(self):
        edge = self.graph.add_edge("A", "B")
        self.assertEqual(edge.edge_key(), (0, 1))
        edge = self.graph.add_edge("A", "C")
        self.assertEqual(edge.edge_key(), (0, 2))

        edge = self.graph.add_edge("B", "D")
        self.assertEqual(edge.edge_key(), (1, 3))
        edge = self.graph.add_edge("B", "E")
        self.assertEqual(edge.edge_key(), (1, 4))
        
        edge = self.graph.add_edge("C", "E")
        self.assertEqual(edge.edge_key(), (2, 4))
        edge = self.graph.add_edge("C", "D")
        self.assertEqual(edge.edge_key(), (2, 3))

        edge = self.graph.add_edge("D", "F")
        self.assertEqual(edge.edge_key(), (3, 5))
        edge = self.graph.add_edge("E", "F")
        self.assertEqual(edge.edge_key(), (4, 5))

    def test_it_creates_a_dag_incrementally(self):
        graph =  Graph('Test graph')
        graph.add_node("A")
        graph.add_node("B")
        edge = graph.add_edge("A", "B")
        self.assertEqual(edge.edge_key(), (0, 1))
        graph.add_node("C")
        edge = graph.add_edge("A", "C")
        self.assertEqual(edge.edge_key(), (0, 2))
        
        graph.add_node("D")
        edge = graph.add_edge("B", "D")
        self.assertEqual(edge.edge_key(), (1, 3))
        graph.add_node("E")
        edge = graph.add_edge("B", "E")
        self.assertEqual(edge.edge_key(), (1, 4))
        
        edge = graph.add_edge("C", "E")
        self.assertEqual(edge.edge_key(), (2, 4))
        edge = graph.add_edge("C", "D")
        self.assertEqual(edge.edge_key(), (2, 3))
        
        graph.add_node("F")
        edge = graph.add_edge("D", "F")
        self.assertEqual(edge.edge_key(), (3, 5))
        edge = graph.add_edge("E", "F")
        self.assertEqual(edge.edge_key(), (4, 5))
    
    def test_it_creates_a_dag_with_skip_lanes(self):
        edge = self.graph.add_edge("A", "B")
        self.assertEqual(edge.edge_key(), (0, 1))
        edge = self.graph.add_edge("B", "C")
        self.assertEqual(edge.edge_key(), (1, 2))
        edge = self.graph.add_edge("C", "D")
        self.assertEqual(edge.edge_key(), (2, 3))
        edge = self.graph.add_edge("D", "E")
        self.assertEqual(edge.edge_key(), (3, 4))
        edge = self.graph.add_edge("E", "F")
        self.assertEqual(edge.edge_key(), (4, 5))

        edge = self.graph.add_edge("A", "F")
        self.assertEqual(edge.edge_key(), (0, 5))
        edge = self.graph.add_edge("B", "F")
        self.assertEqual(edge.edge_key(), (1, 5))
        edge = self.graph.add_edge("C", "F")
        self.assertEqual(edge.edge_key(), (2, 5))
        edge = self.graph.add_edge("D", "F")
        self.assertEqual(edge.edge_key(), (3, 5))

    def test_it_creates_a_dag_with_skip_lanes_incrementally(self):
        graph = Graph("Test graph")
        graph.add_node("A")
        graph.add_node("B")
        edge = graph.add_edge("A", "B")
        self.assertEqual(edge.edge_key(), (0, 1))
        graph.add_node("C")
        edge = graph.add_edge("B", "C")
        self.assertEqual(edge.edge_key(), (1, 2))
        graph.add_node("D")
        edge = graph.add_edge("C", "D")
        self.assertEqual(edge.edge_key(), (2, 3))
        graph.add_node("E")
        edge = graph.add_edge("D", "E")
        self.assertEqual(edge.edge_key(), (3, 4))
        graph.add_node("F")
        edge = graph.add_edge("E", "F")
        self.assertEqual(edge.edge_key(), (4, 5))
        
        edge = graph.add_edge("A", "F")
        self.assertEqual(edge.edge_key(), (0, 5))
        edge = graph.add_edge("B", "F")
        self.assertEqual(edge.edge_key(), (1, 5))
        edge = graph.add_edge("C", "F")
        self.assertEqual(edge.edge_key(), (2, 5))
        edge = graph.add_edge("D", "F")
        self.assertEqual(edge.edge_key(), (3, 5))

    def test_it_fails_to_create_self_loop(self):
        edge = self.graph.add_edge("A", "A")
        self.assertEqual(edge, None)

    def test_it_fails_to_create_self_loop_incrementally(self):
        graph = Graph('Test graph')
        graph.add_node("A")
        edge = graph.add_edge("A", "A")
        self.assertEqual(edge, None)
        
    def test_it_fails_to_create_a_two_node_loop(self):
        edge = self.graph.add_edge("A", "B")
        self.assertEqual(edge.edge_key(), (0, 1))
        edge = self.graph.add_edge("B", "A")
        self.assertEqual(edge, None)

    def test_it_fails_to_create_a_two_node_loop_incrementally(self):
        graph = Graph('Test graph')
        graph.add_node("B")
        graph.add_node("A")
        edge = graph.add_edge("A", "B")
        self.assertEqual(edge.edge_key(), (1, 0))
        edge = graph.add_edge("B", "A")
        self.assertEqual(edge, None)
        
    def test_it_fails_to_create_a_three_node_loop(self):
        edge = self.graph.add_edge("A", "B")
        self.assertEqual(edge.edge_key(), (0, 1))
        edge = self.graph.add_edge("B", "C")
        self.assertEqual(edge.edge_key(), (1, 2))
        edge = self.graph.add_edge("C", "A")
        self.assertEqual(edge, None)
        
    def test_it_fails_to_create_a_three_node_loop_incrementaly(self):
        graph = Graph('Test graph')
        graph.add_node("A")
        graph.add_node("B")
        edge = graph.add_edge("A", "B")
        self.assertEqual(edge.edge_key(), (0, 1))
        graph.add_node("C")
        edge = graph.add_edge("B", "C")
        self.assertEqual(edge.edge_key(), (1, 2))
        edge = graph.add_edge("C", "A")
        self.assertEqual(edge, None)
        
    def test_it_fails_to_create_a_loop_in_a_dag(self):
        edge = self.graph.add_edge("A", "B")
        self.assertEqual(edge.edge_key(), (0, 1))
        edge = self.graph.add_edge("A", "C")
        self.assertEqual(edge.edge_key(), (0, 2))

        edge = self.graph.add_edge("B", "D")
        self.assertEqual(edge.edge_key(), (1, 3))
        
        edge = self.graph.add_edge("C", "E")
        self.assertEqual(edge.edge_key(), (2, 4))

        edge = self.graph.add_edge("D", "F")
        self.assertEqual(edge.edge_key(), (3, 5))
        edge = self.graph.add_edge("E", "F")
        self.assertEqual(edge.edge_key(), (4, 5))
        
        edge = self.graph.add_edge("D", "C")
        self.assertEqual(edge.edge_key(), (3, 2))

    def test_it_fails_to_create_a_loop_in_a_dag_incrementally(self):
        graph = Graph('Test graph')
        graph.add_node("A")
        graph.add_node("B")
        edge = graph.add_edge("A", "B")
        self.assertEqual(edge.edge_key(), (0, 1))
        graph.add_node("C")
        edge = graph.add_edge("A", "C")
        self.assertEqual(edge.edge_key(), (0, 2))
        
        graph.add_node("D")
        edge = graph.add_edge("B", "D")
        self.assertEqual(edge.edge_key(), (1, 3))
        
        graph.add_node("E")
        edge = graph.add_edge("C", "E")
        self.assertEqual(edge.edge_key(), (2, 4))
        
        graph.add_node("F")
        edge = graph.add_edge("D", "F")
        self.assertEqual(edge.edge_key(), (3, 5))
        edge = graph.add_edge("E", "F")
        self.assertEqual(edge.edge_key(), (4, 5))
        
        edge = graph.add_edge("D", "C")
        self.assertEqual(edge.edge_key(), (3, 2))