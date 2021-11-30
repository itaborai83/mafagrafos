from functools import reduce
from operator import mul

class Segment:
    
    __slots__ = ["from_label", "to_label", "pct", "min_t", "curr_t", "max_t"]
    
    def __init__(self, from_label, to_label, pct, min_t, curr_t, max_t):
        assert from_label
        assert to_label
        assert from_label != to_label
        assert min_t <= max_t
        self.from_label = from_label
        self.to_label   = to_label
        self.pct        = pct
        self.min_t      = min_t
        self.curr_t     = curr_t
        self.max_t      = max_t
    
    def __str__(self):
        return f"<Segment from_label='{self.from_label}', to_label='{self.to_label}', pct={self.pct}, curr_t={self.curr_t}>"
    
    def __repr__(self):
        return str(self)

    def show(self):
        return f" :: {self.from_label} - > {self.to_label} // pct={self.pct}, min_t={self.min_t}, curr_t={self.curr_t}, max_t={self.max_t}"
        
    def __eq__(self, other):
        if other is None:
            return False
        return self.from_label  == other.from_label and \
               self.to_label    == other.to_label   and \
               self.pct         == other.pct        and \
               self.min_t       == other.min_t      and \
               self.curr_t      == other.curr_t     and \
               self.max_t       == other.max_t
    
    def clone(self):
        return self # I think I can share segments between paths
    
class Path:
    
    __slots__ = ["from_label", "to_label", "segments", "segment_count", "ammount", "inputed_ammount", "received_ammount", "transferred_ammount" ]
    
    def __init__(self):
        self.from_label             = None
        self.to_label               = None
        self.segments               = []
        self.segment_count          = 0
        self.ammount                = 0.0
        self.inputed_ammount        = 0.0
        self.received_ammount       = 0.0
        self.transferred_ammount    = 0.0
        
    def __eq__(self, other):
        if other is None:
            return False
        return self.from_label          == other.from_label             and \
               self.to_label            == other.to_label               and \
               self.segment_count       == other.segment_count          and \
               self.segments            == other.segments               and \
               self.ammount             == other.ammount                and \
               self.inputed_ammount     == other.inputed_ammount        and \
               self.received_ammount    == other.received_ammount       and \
               self.transferred_ammount == other.transferred_ammount
    
    def show(self):
        parts = []
        parts.append(f"{self.from_label} -> {self.to_label} // min_t = {self.min_t}, max_t = {self.max_t}, segments={self.segment_count}")
        for i, segment in enumerate(self.segments):
            parts.append(f"\t, {i+1}" + segment.show())
        return "\n".join(parts)
        
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
        result.from_label          = self.from_label
        result.to_label            = self.to_label
        result.segments            = self.segments[:]
        result.segment_count       = self.segment_count
        result.ammount             = self.ammount
        result.inputed_ammount     = self.inputed_ammount
        result.received_ammount    = self.received_ammount   
        result.transferred_ammount = self.transferred_ammount
        return result
    
    def is_temporally_consistent(self):
        assert self.segment_count >= 0
        if self.segment_count <= 1:
            return True
        curr_t_head = self.segments[0].curr_t
        curr_t_tail = self.segments[1].curr_t
        return curr_t_head <= curr_t_tail

    @property
    def pct(self):
        return reduce(mul, [s.pct for s in self.segments ], 1.0)

    @property
    def min_t(self):
        assert self.segment_count > 0
        return self.segments[0].curr_t
    
    @property
    def max_t(self):
        assert self.segment_count > 0
        return self.segments[-1].curr_t
        
        
class Segment:
    
    __slots__ = ["from_label", "to_label", "pct", "min_t", "curr_t", "max_t"]
    
    def __init__(self, from_label, to_label, pct, min_t, curr_t, max_t):
        assert from_label
        assert to_label
        assert from_label != to_label
        assert min_t <= max_t
        self.from_label = from_label
        self.to_label   = to_label
        self.pct        = pct
        self.min_t      = min_t
        self.curr_t     = curr_t
        self.max_t      = max_t
    
    def __str__(self):
        return f"<Segment from_label='{self.from_label}', to_label='{self.to_label}', pct={self.pct}, curr_t={self.curr_t}>"
    
    def __repr__(self):
        return str(self)

    def show(self):
        return f" :: {self.from_label} - > {self.to_label} // pct={self.pct}, min_t={self.min_t}, curr_t={self.curr_t}, max_t={self.max_t}"
        
    def __eq__(self, other):
        if other is None:
            return False
        return self.from_label  == other.from_label and \
               self.to_label    == other.to_label   and \
               self.pct         == other.pct        and \
               self.min_t       == other.min_t      and \
               self.curr_t      == other.curr_t     and \
               self.max_t       == other.max_t
    
    def clone(self):
        return self # I think I can share segments between paths
    
class PathV2:
    
    CURRENT_PATH_ID = 0
    
    __slots__ = [
        "path_id",
        "from_label", 
        "to_label", 
        "root_path", 
        "parent_path", 
        "children", 
        "length", 
        "max_t",
        "pct",
        "ammount", 
        "inputed_ammount", 
        "received_ammount", 
        "transferred_ammount" 
    ]
    
    def __init__(self):
        self.path_id                = None
        self.root_path              = self
        self.from_label             = None
        self.to_label               = None
        self.parent_path            = None
        self.children               = []
        self.length                 = 0
        self.max_t                  = None
        self.pct                    = 1.0
        self.ammount                = 0.0
        self.inputed_ammount        = 0.0
        self.received_ammount       = 0.0
        self.transferred_ammount    = 0.0
    
    @classmethod
    def next_id(klass):
        klass.CURRENT_PATH_ID += 1
        return klass.CURRENT_PATH_ID
       
    def __eq__(self, other):
        if other is None:
            return False
        return self.path_id             == other.path_id                and \
               self.root_path           == other.root_path              and \
               self.from_label          == other.from_label             and \
               self.to_label            == other.to_label               and \
               self.parent_path         == other.parent_path            and \
               self.children            == other.children               and \
               self.length              == other.length                 and \
               self.max_t               == other.max_t                  and \
               self.pct                 == other.pct                    and \
               self.ammount             == other.ammount                and \
               self.inputed_ammount     == other.inputed_ammount        and \
               self.received_ammount    == other.received_ammount       and \
               self.transferred_ammount == other.transferred_ammount
    
    #def show(self):
    #    parts = []
    #    parts.append(f"{self.from_label} -> {self.to_label} // min_t = {self.min_t}, max_t = {self.max_t}, segments={self.segment_count}")
    #    for i, segment in enumerate(self.segments):
    #        parts.append(f"\t, {i+1}" + segment.show())
    #    return "\n".join(parts)
        
    #def push_segment(self, segment):
    #    assert self.segment_count == 0 or segment.to_label == self.from_label, (self.segment_count, segment.to_label, self.from_label)
    #    self.segments.insert(0, segment) # this might be slow - O(n)
    #    self.segment_count += 1
    #    self.from_label = segment.from_label
    #    if self.segment_count == 1:
    #        self.to_label = segment.to_label
        
    #def pop_segment(self):
    #    assert self.segment_count > 0
    #    self.segments.pop(0)
    #    self.segment_count -= 1
    #    if self.segment_count == 0:
    #        self.from_label = None
    #        self.to_label = None
    #    else:
    #        self.from_label = self.segments[0].from_label
        
    #def is_temporally_consistent(self):
    #    assert self.segment_count >= 0
    #    if self.segment_count <= 1:
    #        return True
    #    curr_t_head = self.segments[0].curr_t
    #    curr_t_tail = self.segments[1].curr_t
    #    return curr_t_head <= curr_t_tail

    #@property
    #def pct(self):
    #    path = self
    #    pct = 1.0
    #    while True:
    #        pct *= 
    #    return reduce(mul, [s.pct for s in self.segments ], 1.0)
    #
    #@property
    #def min_t(self):
    #    assert self.segment_count > 0
    #    return self.segments[0].curr_t
    #
    #@property
    #def max_t(self):
    #    assert self.segment_count > 0
    #    return self.segments[-1].curr_t        