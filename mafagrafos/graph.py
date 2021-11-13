from mafagrafos.node import Node
from mafagrafos.edge import Edge

class NodeVisitor:
    
    def __init__(self):
        self.visited_set = set()
        
    def visit(self, node_id):
        assert node_id not in self.visited_set
        self.visited_set.add(node_id)
        
    def unvisit(self, node_id):
        assert node_id in self.visited_set
        self.visited_set.remove(node_id)
    
    def has_visited(self, node_id):
        return node_id in self.visited_set
        
    def clear_visited(self):
        self.visited_set.clear()

class Graph:
    
    __slots__ = ["name", "next_node_id", "nodes", "labels", "topo_sort_started", "node_to_index", "index_to_node", "edges", "visitor"]
    
    def __init__(self, name):
        assert name
        self.name               = name
        self.next_node_id       = 0
        self.nodes              = []
        self.labels             = {}
        self.topo_sort_started  = False
        self.node_to_index      = []
        self.index_to_node      = []
        self.edges              = {}
        self.visitor            = NodeVisitor()
    
    def __str__(self):
        return f"<Graph name='{self.name}>'"
    
    def __repr__(self):
        return f"<Graph name='{self.name}>'"
        
    def _create_node(self, node_id, label, data=None):
        node = Node(node_id, label, data=data)
        node.graph = self
        return node

    def _create_edge(self, from_node, to_node, edge_label=None, data=None):
        edge = Edge(from_node.node_id, to_node.node_id, label=edge_label, data=data)
        edge.graph = self
        return edge
        
    def get_node_by_label(self, label):
        # can return None
        return self.labels.get(label, None)

    def get_node_by_id(self, node_id):
        # can not return None. if you have the node_id it *must* exist
        assert 0 <= node_id < self.next_node_id
        return self.nodes[node_id]
    
    def start_topo_sorting(self):
        assert self.topo_sort_started == False
        self.topo_sort_started = True
        
    def add_node(self, label, data=None):
        assert label
        assert self.topo_sort_started is False # can only add nodes while not mantaining the topological ordering of the graph
        assert self.get_node_by_label(label) is None
        node = self._create_node(self.next_node_id, label, data)
        self.nodes.append(node)
        self.labels[node.label] = node
        # update the trivial topological sorting of a graph without edges
        # node to index mapping - indicates the topological index of node n
        self.node_to_index.append(node.node_id)
        # index to node mapping - indicates the node which occupies the nth topological index
        self.index_to_node.append(node.node_id)
        self.next_node_id += 1
        assert len(self.nodes)          == self.next_node_id
        assert len(self.node_to_index)  == self.next_node_id
        assert len(self.index_to_node)  == self.next_node_id
        return node
    
    def get_edge(self, from_label, to_label):
        assert from_label
        assert to_label
        from_node = self.get_node_by_label(from_label)
        assert from_node is not None
        to_node = self.get_node_by_label(to_label)
        assert to_node is not None
        edge_key = (from_node.node_id, to_node.node_id)
        return self.edges.get(edge_key, None)
    
    def has_edge(self, from_label, to_label):
        assert from_label
        assert to_label
        from_node = self.get_node_by_label(from_label)
        assert from_node is not None
        to_node = self.get_node_by_label(to_label)
        assert to_node is not None
        return (from_node.node_id, to_node.node_id) in self.edges
            
    def add_edge(self, from_label, to_label, edge_label=None, data=None):
        assert from_label
        assert to_label
        assert self.topo_sort_started is True
        from_node = self.get_node_by_label(from_label)
        assert from_node is not None
        to_node = self.get_node_by_label(to_label)
        assert to_node is not None
        edge = self._create_edge(from_node, to_node, edge_label=edge_label, data=data)
        from_node.add_out_edge(to_node.node_id)
        to_node.add_in_edge(from_node.node_id)
        self.edges[ (from_node.node_id, to_node.node_id) ] = edge
        return edge

