class AccEntryList:
    
    def __init__(self):
        self.nodes = []
        self.seen_nodes = set() # to avoid linear scan of all nodes
        self.entries = []

    def __eq__(self, other):
        if other is None:
            return False
        return  self.nodes      == other.nodes      and \
                self.seen_nodes == other.seen_nodes and \
                self.entries    == other.entries
    
    def __str__(self):
        return f"<AccEntryList #{len(self.entries)} entries>"
        
    def _add_node(self, node_label):
        assert node_label
        if node_label not in self.seen_nodes:
            self.nodes.append(node_label)
            self.seen_nodes.add(node_label) 
        
    def add_entry(self, entry):
        self.entries.append(entry)
        self._add_node(entry.dst)
        if entry.src:
            self._add_node(entry.src)
    
    @classmethod
    def get_test_case_01(klass):
        result = klass()
        entries = AccEntry.get_test_case_01()
        for entry in entries:
            result.add_entry(entry)
        return result
        
class AccEntry:
    
    __slots__ = [ 'dst', 'src', 'ammount' ]
    
    def __init__(self, dst, src, ammount):
        self.dst = dst
        self.ammount = ammount
        self.src = src
    
    def __eq__(self, other):
        if other is None:
            return False
        return  self.dst        == other.dst and \
                self.ammount    == other.ammount and \
                self.src        == other.src
    
    def __str__(self):
        return f"<AccEntry dst='{self.dst}', src='{self.src}', ammount={self.ammount}>"
    