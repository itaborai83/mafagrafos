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

    @classmethod
    def get_test_case_01(klass):
        return [
            klass("CJ20", None,   1_000_000.00)
        ,   klass("CJ10", "CJ20",   850_000.00)
        ,   klass("CJ12", "CJ20",   150_000.00)
        ,   klass("CJ10", None,     400_000.00)
        ,   klass("CJ11", "CJ10",   500_000.00)
        ,   klass("CJ13", "CJ10",   750_000.00)
        ,   klass("CJ13", None,     100_000.00)
        ,   klass("CJ14", "CJ13",   600_800.00)
        ,   klass("CJ11", "CJ13",   150_200.00)
        ,   klass("CJ11", None,     200_000.00)
        ,   klass("CJ14", "CJ11",   595_140.00)
        ,   klass("CJ20", "CJ11",   255_060.00)
        ,   klass("CJ12", "CJ20",   255_060.00)
        ,   klass("CJ14", None,     200_000.00)
        ,   klass("CJ14", "CJ12",   202_530.00)
        ,   klass("CJ13", "CJ11",   100_000.00)
        ,   klass("CJ14", "CJ11",   100_000.00)
        ,   klass("CJ20", "CJ13",    50_000.00)
        ,   klass("CJ10", "CJ20",    50_000.00)
        ,   klass("CJ14", "CJ10",    25_000.00)
        ]