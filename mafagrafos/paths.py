from functools import reduce
from operator import mul

class Segment:
    
    __slots__ = ["from_label", "to_label", "pct"]
    
    def __init__(self, from_label, to_label, pct):
        assert from_label
        assert to_label
        assert from_label != to_label
        self.from_label = from_label
        self.to_label   = to_label
        self.pct        = pct
    
    def __eq__(self, other):
        if other is None:
            return False
        return self.from_label  == other.from_label and \
               self.to_label    == other.to_label   and \
               self.pct         == other.pct
    
    def clone(self):
        return self # I think I can share segments between paths
    
class Path:
    
    __slots__ = ["from_label", "to_label", "segments", "segment_count", "inputed_ammount"]
    
    def __init__(self, from_label, to_label):
        self.from_label      = from_label
        self.to_label        = to_label
        self.segments        = []
        self.segment_count   = 0
        self.inputed_ammount = 0.0

    def __eq__(self, other):
        if other is None:
            return False
        return self.from_label  == other.from_label and \
               self.to_label    == other.to_label   and \
               self.segments    == other.segments
    
    def push_segment(self, from_label, to_label, pct):
        segment = Segment(from_label, to_label, pct)
        self.segments.insert(0, segment) # this might be slow - O(n)
        self.segment_count += 1
    
    def pop_segment(self):
        assert self.segment_count > 0
        self.segments.pop(-1)
        self.segment_count -= 1
    
    def clone(self):
        result = Path(self.from_label, self.to_label)
        result.segment_count = self.segment_count
        result.segments = self.segments[:]
        return result
    
    @property
    def pct(self):
        return reduce(mul, [s.pct for s in self.segments ], 1.0)
        
    @classmethod
    def build_paths(klass, sink_label, graph):
        curr_node = graph.get_node_by_label(sink_label)
        assert curr_node
        curr_path = klass(sink_label, sink_label) # do not store the starting self loop into the accumulator
        acc = []
        klass._build_path(curr_node, curr_path, graph, acc)
        #acc.reverse()
        return acc
        
    @classmethod
    def _build_path(klass, curr_node, curr_path, graph, acc):
        # graph is a DAG, so no cycles
        old_path = curr_path
        for from_id in curr_node.in_edges:
            from_node = graph.get_node_by_id(from_id)
            assert from_node
            edge = graph.get_edge(from_node.label, curr_node.label)
            assert edge
            edge_pct = edge.get_attr('pct') / 100.0
            assert edge_pct
            curr_path = old_path.clone()
            curr_path.from_label = from_node.label
            curr_path.push_segment(from_node.label, curr_node.label, edge_pct)
            curr_path.inputed_ammount = from_node.get_attr('inputed_ammount')
            acc.append(curr_path)
            klass._build_path(from_node, curr_path, graph, acc)
