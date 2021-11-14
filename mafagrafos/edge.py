import copy

class Edge:
    
    __slots__ = ['from_id', 'to_id', 'label', 'data', 'graph']
    
    def __init__(self, from_id, to_id, label, data=None):
        assert from_id >= 0
        assert to_id >= 0
        self.from_id    = from_id
        self.to_id      = to_id
        self.label      = label if label else None
        self.data       = data if data else {}
        self.graph      = None
    
    def __eq__(self, other):
        if other is None:
            return False
        return  self.from_id == other.from_id and \
                self.to_id   == other.to_id   and \
                self.label   == other.label   and \
                self.data    == other.data    and \
                self.graph   == other.graph
    
    def __str__(self):
        return f"<Edge from_id={self.from_id}, node_id={self.to_id}, label='{self.label}'>"
    
    def __repr__(self):
        return str(self)
    
    def get_data(self):
        return self.data
    
    def edge_key(self):
        return (self.from_id, self.to_id)