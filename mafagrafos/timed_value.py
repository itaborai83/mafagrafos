class TimedValueEntry:
    
    __slots__ = ['time', 'value']
    
    def __init__(self, time, value=0.0):
        self.time = time
        self.value = value
    
    def __str__(self):
        return f"<TimedValueEntry {self.value}@{self.time}>"
    
    def __repr__(self):
        return f"<TimedValueEntry {self.value}@{self.time}>"
        
    def update(self, value):
        self.value += value
    
class TimedValue:
    
    __slots__ = ['entries', 'last_time', 'first_time']
    
    def __init__(self):
        self.entries = []
        self.last_time = None
        self.first_time = None

    def __str__(self):
        return f"<TimedValue last_time={self.last_time}, entries={self.entries}>"
    
    def __repr__(self):
        return f"<TimedValue last_time={self.last_time}, entries={self.entries}>"
        
    def update_at(self, time, value):
        if self.last_time is None:
            self.last_time = time
            self.first_time = time
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
        if self.last_time is None or time < self.first_time:
            return 0.0
        
        elif self.last_time <= time:
            return self.entries[-1].value
        
        result = self.entries[-1].value
        for entry in reversed(self.entries):
            if entry.time < time:
                return result
            else:
                result = entry.value
        return result
    
    @property
    def current_value(self):
        if self.last_time is None:
            return 0.0
        else:
            return self.entries[-1].value