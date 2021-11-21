import unittest
from mafagrafos.timed_value import *

class TestTimedValue(unittest.TestCase):

    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_it_returns_zero_if_nothing_is_given(self):
        tm = TimedValue()
        value = tm.value_at(10)
        self.assertEqual(0.0, value)
    
    def test_it_returns_a_given_value(self):
        tm = TimedValue()
        tm.update_at(10, 100.0)
        value = tm.value_at(10)
        self.assertEqual(100.0, value)
        
    def test_it_sums_values_at_the_same_instant(self):
        tm = TimedValue()
        tm.update_at(10, 100.0)
        tm.update_at(10, 100.0)
        value = tm.value_at(10)
        self.assertEqual(200.0, value)
    
    def test_it_sums_older_values(self):
        tm = TimedValue()
        tm.update_at(9, 100.0)
        tm.update_at(10, 100.0)
        value = tm.value_at(10)
        self.assertEqual(200.0, value)

    def test_it_retrieves_an_older_value(self):
        tm = TimedValue()
        tm.update_at(8, 100.0)
        tm.update_at(9, 100.0)
        tm.update_at(10, 100.0)
        value = tm.value_at(9)
        self.assertEqual(200.0, value)
        
    def test_it_retrieves_zero_for_an_instant_older_than_the_oldest_entry(self):
        tm = TimedValue()
        tm.update_at(8, 100.0)
        tm.update_at(9, 100.0)
        tm.update_at(10, 100.0)
        value = tm.value_at(7)
        self.assertEqual(0.0, value)

    def test_it_retrieves_the_newest_value_for_an_instant_newer_than_the_newest_entry(self):
        tm = TimedValue()
        tm.update_at(8, 100.0)
        tm.update_at(9, 100.0)
        tm.update_at(10, 100.0)
        value = tm.value_at(11)
        self.assertEqual(300.0, value)
        