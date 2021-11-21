class TimedValueEntry:
    
    __slots__ = ['time', 'value']
    
    def __init__(self, time, value=0.0):
        self.time = time
        self.value = value
    
    def update(self, value):
        self.value += value
    
class TimedValue:
    
    __slots__ = ['entries', 'last_time']
    
    def __init__(self):
        self.entries = []
        self.last_time = None
    
    def update_at(self, time, value):
        if self.last_time is None:
            self.last_time = time
            new_entry = TimedValueEntry(time, value)
            self.entries.append(new_entry)
            return
        
        assert self.last_time <= time
        if self.last_time == time:
            self.entries[-1].update(value)
        else:
            self.last_time = time
            current_value = self.entries[-1].value
            new_entry = TimedValueEntry(time, value + current_value)
            self.entries.append(new_entry)
    
    def value_at(self, time):
        if self.last_time is None:
            return 0.0
        
        elif self.last_time <= time:
            return self.entries[-1].value
        
        result = self.entries[-1].value
        for entry in reversed(self.entries):
            if entry.time < time:
                return result
            else:
                result = entry.value
        return 0.0
    
    @property
    def current_value(self):
        if self.last_time is None:
            return 0.0
        else:
            return self.entries[-1].value