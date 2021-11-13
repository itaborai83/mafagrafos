from mafagrafos.node import Node

class Graph:
    
    __slots__ = ["name", "next_node_id", "nodes", "labels", "topo_sort_started", "node_to_index", "index_to_node", "edges"]
    
    def __init__(self, name):
        assert name
        self.name               = name
        self.next_node_id       = 0
        self.nodes              = []
        self.labels             = {}
        self.topo_sort_started  = False
        self.node_to_index      = []
        self.index_to_node      = []
        self.edges              = set()
    
    def __str__(self):
        return f"<Graph name='{self.name}>'"
    
    def __repr__(self):
        return f"<Graph name='{self.name}>'"
        
    def get_node_class(self):
        return Node

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
        
    def add_node(self, label):
        assert label
        assert self.topo_sort_started is False # can only add nodes while not mantaining the topological ordering of the graph
        assert self.get_node_by_label(label) is None
        klass = self.get_node_class()
        node = klass(self.next_node_id, label)
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
        node.graph = self
        return node
    
    def has_edge(self, from_label, to_label):
        assert from_label
        assert to_label
        from_node = self.get_node_by_label(from_label)
        assert from_node is not None
        to_node = self.get_node_by_label(to_label)
        assert to_node is not None
        return self._has_edge(from_node.node_id, to_node.node_id)
