from functools import reduce
from operator import mul

class Segment:
    
    __slots__ = ["from_label", "to_label", "pct", "min_t", "max_t"]
    
    def __init__(self, from_label, to_label, pct, min_t, max_t):
        assert from_label
        assert to_label
        assert from_label != to_label
        assert min_t <= max_t
        self.from_label = from_label
        self.to_label   = to_label
        self.pct        = pct
        self.min_t      = min_t
        self.max_t      = max_t
    
    def __str__(self):
        return f"<Segment from_label='{self.from_label}', to_label='{self.to_label}', pct={self.pct}, max_t={self.max_t}>"
    
    def __repr__(self):
        return str(self)
        
    def __eq__(self, other):
        if other is None:
            return False
        return self.from_label  == other.from_label and \
               self.to_label    == other.to_label   and \
               self.pct         == other.pct        and \
               self.min_t       == other.min_t      and \
               self.max_t       == other.max_t
    
    def clone(self):
        return self # I think I can share segments between paths
    
class Path:
    
    __slots__ = ["from_label", "to_label", "segments", "segment_count", "inputed_ammount", "received_ammount"]
    """
    def __init__(self, from_label, to_label):
        self.from_label         = from_label
        self.to_label           = to_label
        self.segments           = []
        self.segment_count      = 0
        self.inputed_ammount    = 0.0
        self.received_ammount   = 0.0

    def __eq__(self, other):
        if other is None:
            return False
        return self.from_label  == other.from_label and \
               self.to_label    == other.to_label   and \
               self.segments    == other.segments
    
    def push_segment(self, from_label, to_label, pct, min_t, max_t):
        segment = Segment(from_label, to_label, pct, min_t, max_t)
        self.segments.insert(0, segment) # this might be slow - O(n)
        self.segment_count += 1
    
    def pop_segment(self):
        assert self.segment_count > 0
        self.segments.pop(0)
        self.segment_count -= 1
    
    def clone(self):
        result = Path()
        result.segment_count = self.segment_count
        result.segments = self.segments[:]
        return result
    
    def is_temporally_consistent(self):
        # a temporally consistent path is one in which max(T(head_node)) <= max(T(tail_node))
        assert self.segment_count >= 0
        if self.segment_count < 2:
            return True
        max_t_head = self.segments[0].max_t
        max_t_tail = self.segments[1].max_t
        return max_t_head <= max_t_tail

        
    @property
    def pct(self):
        # TODO: add caching
        return reduce(mul, [s.pct for s in self.segments ], 1.0)

    @property
    def min_t(self):
        # TODO: add caching
        return self.segments[0].min_t
    
    @property
    def max_t(self):
        # TODO: add caching
        return self.segments[-1].max_t
        
    @classmethod
    def build_paths(klass, sink_label, graph):
        # graph is a DAG, so no cycles
        assert not graph.allow_cycles
        head_node = graph.get_node_by_label(sink_label)
        assert head_node
        curr_path = klass(sink_label, sink_label) # do not store the starting self loop into the accumulator
        acc = []
        klass._build_path(head_node, None, None, curr_path, graph, acc)
        return acc
        
    @classmethod
    def _build_path(klass, head_node, edge, tail_node, curr_path, graph, acc):
        #print(head_node)
        #print(edge)
        #print(tail_node)
        #for segment in curr_path.segments:
        #    print("\t", segment)
        #print()
        
        if curr_path.segment_count > 0 and not curr_path.is_temporally_consistent():
            # if the head node is the head of a temporally inconsistent path.
            # recompute the edge percentual taking into account the received_ammount of the tail_node
            # and then pop off the head node from the path
            
            curr_path = None # throw away the current path and adjust the last added path
            curr_path = acc[-1]
            head_node = tail_node # previous head node
            tail_node_label = curr_path.segments[0].to_label
            tail_node = graph.get_node_by_label(tail_node_label) # previous tail node
            edge = graph.get_edge(head_node.label, tail_node.label) # previous edge linking previous head node to tail node
            assert edge
            
            # compute the edge pct of a temporally inconsistent node
            edge_ammount        = edge.get_attr('ammount')
            node_ammount        = head_node.get_attr('ammount')
            received_ammount    = head_node.get_attr('received_ammount') # get inputed_ammount from all descending nodes
            inputed_ammount     = head_node.get_attr('inputed_ammount')
            transferred_ammount = head_node.get_attr('transferred_ammount')
            #edge_pct            = edge_ammount / (node_ammount + received_ammount)
            edges_sum           = transferred_ammount + inputed_ammount
            # discount the received_ammount because it is has not happened yet
            edges_sum          -= received_ammount 
            edge_pct            = edge_ammount / edges_sum
            
            # the pct stored within the graph needs to be updated            
            # TODO: put this in a saner place
            edge_pct_txt = '{:.2f}%'.format(edge_pct*100.0) 
            edge.set_attr('pct', edge_pct)
            edge.set_attr('pct_txt', edge_pct_txt)
            
            curr_path.inputed_ammount   = inputed_ammount
            curr_path.received_ammount  = received_ammount
            curr_path.segments[0].pct   = edge_pct
            # since the head not is not temporally consistent, stop building this path
            # do not read the path to the accumulator
            return
        
        elif curr_path.segment_count > 0 and curr_path.is_temporally_consistent():
            # if the head node is the head of a temporally consistent path.
            # use the precomputed edge percentual. DO NOT take into account the received_ammount of the tail_node
            curr_path.received_ammount  = 0.0
            curr_path.inputed_ammount   = head_node.get_attr('inputed_ammount')            
            acc.append(curr_path)

        # continue processing a temporally consistent path with 1 or more nodes in the path
        old_path = curr_path
        new_tail_node = head_node
        for from_id in new_tail_node.in_edges:
            # retrieve the start node of the edge
            new_head_node = graph.get_node_by_id(from_id)
            assert new_head_node
            # use the node label to retrieve the edge itself
            edge = graph.get_edge(new_head_node.label, new_tail_node.label)
            assert edge
            # retrieve the edge_pct
            edge_pct = edge.get_attr('pct') / 100.0
            assert edge_pct
            # retrieve the fista and last transfer time from the edge
            min_t = edge.get_attr('time')[0]
            max_t = edge.get_attr('time')[-1]
            assert min_t <= max_t
            # create a new path cloning the old path 
            curr_path = old_path.clone()
            # set the starting node to be the start node of the edge
            curr_path.from_label = new_head_node.label
            # push a new segment onto the first position of the current path
            curr_path.push_segment(new_head_node.label, new_tail_node.label, edge_pct, min_t, max_t)
            klass._build_path(new_head_node, edge, new_tail_node, curr_path, graph, acc)
    """
    
class PathV2:
    
    __slots__ = ["from_label", "to_label", "segments", "segment_count", "inputed_ammount", "received_ammount" ]
    
    def __init__(self):
        self.from_label         = None
        self.to_label           = None
        self.segments           = []
        self.segment_count      = 0
        self.inputed_ammount    = 0.0
        self.received_ammount   = 0.0
        
    def __eq__(self, other):
        if other is None:
            return False
        return self.from_label          == other.from_label         and \
               self.to_label            == other.to_label           and \
               self.segment_count       == other.segment_count      and \
               self.segments            == other.segments           and \
               self.inputed_ammount     == other.inputed_ammount    and \
               self.received_ammount    == other.received_ammount
    
    #def push_segment(self, from_label, to_label, pct, min_t, max_t):
    #    segment = Segment(from_label, to_label, pct, min_t, max_t)
    #    self.segments.insert(0, segment) # this might be slow - O(n)
    #    self.segment_count += 1
    
    def push_segment(self, segment):
        assert self.segment_count == 0 or segment.to_label == self.from_label, (self.segment_count, segment.to_label, self.from_label)
        self.segments.insert(0, segment) # this might be slow - O(n)
        self.segment_count += 1
        self.from_label = segment.from_label
        if self.segment_count == 1:
            self.to_label = segment.to_label
        
    def pop_segment(self):
        assert self.segment_count > 0
        self.segments.pop(0)
        self.segment_count -= 1
        if self.segment_count == 0:
            self.from_label = None
            self.to_label = None
        else:
            self.from_label = self.segments[0].from_label
    
    def clone(self):
        result = Path()
        result.from_label    = self.from_label
        result.to_label      = self.to_label
        result.segment_count = self.segment_count
        result.segments      = self.segments[:]
        return result
    
    def is_temporally_consistent(self):
        # a temporally consistent path is one in which max(T(head_node)) <= max(T(tail_node))
        assert self.segment_count >= 0
        if self.segment_count < 2:
            return True
        max_t_head = self.segments[0].max_t
        max_t_tail = self.segments[1].max_t
        return max_t_head <= max_t_tail

    @property
    def pct(self):
        return reduce(mul, [s.pct for s in self.segments ], 1.0)

    @property
    def min_t(self):
        assert self.segment_count > 0
        return self.segments[0].min_t
    
    @property
    def max_t(self):
        assert self.segment_count > 0
        return self.segments[-1].max_t
        
Path = PathV2        