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
    
class CoepEntry:
    
    __slots__ = [ 'dst', 'src', 'ammount', 'date', 'time', 'type' ]
    
    def __init__(self, dst, src, ammount, date=None, time=None, type='D'):        
        if src is None:
            self.dst        = dst
            self.ammount    = ammount
            self.src        = src
            self.type       = type
        elif type == 'D':
            self.dst        = dst
            self.ammount    = ammount
            self.src        = src
            self.type       = type
        else:
            self.dst        = src
            self.ammount    = 0.0 * -1.0 * ammount
            self.src        = dst
            self.type       = type
        self.date       = date
        self.time       = time
                
    def __eq__(self, other):
        if other is None:
            return False
        return  self.dst        == other.dst        and \
                self.src        == other.src        and \
                self.ammount    == other.ammount    and \
                self.date       == other.date       and \
                self.time       == other.time       and \
                self.type       == other.type
    
    def __str__(self):
        return f"<CoepEntry dst={repr(self.dst)}, src={repr(self.src)}, ammount={repr(self.ammount)}, date={repr(date)}, time={repr(time)}>"
    
    def __repr__(self):
        return str(self)
