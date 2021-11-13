import copy

class Node:
    
    def __init__(self, node_id, label, in_edges=None, out_edges=None, data=None, graph=None):
        assert label
        assert node_id >= 0
        self.node_id    = node_id # node_id is only
        self.label      = label
        self.in_edges   = in_edges  if in_edges     else set()
        self.out_edges  = out_edges if out_edges    else set()
        self.data       = data      if data         else {}
        self.graph      = graph     if graph        else None
        
    def __eq__(self, other):
        return  self.label      == other.label      and \
                self.node_id    == other.node_id    and \
                self.in_edges   == other.in_edges   and \
                self.out_edges  == other.out_edges  and \
                self.data       == other.data       and \
                self.graph      == other.graph
    
    def __str__(self):
        return f"<Node node_id={self.node_id}, label='{self.label}'>"
    
    def __repr__(self):
        return str(self)
    
    def get_data(self):
        return self.data

    def has_out_edge(self, node_id):
        assert node_id >= 0
        return node_id in self.out_edges

    def has_in_edge(self, node_id):
        assert node_id >= 0
        return node_id in self.in_edges
        
    def add_out_edge(self, node_id):
        assert node_id >= 0
        assert node_id not in self.out_edges
        self.out_edges.add(node_id)
        # graph has the responsability to add the in edget

    def add_in_edge(self, node_id):
        assert node_id >= 0
        assert node_id not in self.in_edges
        self.in_edges.add(node_id)
        # graph has the responsability to add the out edget
        
    def del_out_edge(self, node_id):
        assert node_id in self.out_edges
        self.out_edges.remove(node_id)
        
    def del_in_edge(self, node_id):
        assert node_id in self.in_edges
        self.in_edges.remove(node_id)