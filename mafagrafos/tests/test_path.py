import unittest
from mafagrafos.paths import *

class TestPath(unittest.TestCase):

    def setUp(self):
        self.path = Path()
    
    def tearDown(self):
        pass
    
    def test_it_computes_the_path_percentual_as_100_for_an_empty_path(self):
        self.assertEqual(self.path.pct, 1.0)
    
    def test_it_fails_to_compute_min_t_for_an_empty_path(self):
        with self.assertRaises(AssertionError):
            min_t = self.path.min_t

    def test_it_fails_to_compute_max_t_for_an_empty_path(self):
        with self.assertRaises(AssertionError):
            max_t = self.path.max_t
            
    def test_it_prepends_a_segment_to_an_empty_path(self):
        segment = Segment(from_label='B', to_label='A', pct=0.5, min_t=1, curr_t=10, max_t=10)
        expected = Segment(from_label='B', to_label='A', pct=0.5, min_t=1, curr_t=10, max_t=10)
        self.path.push_segment(segment)
        self.assertEqual(self.path.segment_count, 1)
        self.assertEqual(self.path.from_label, 'B')
        self.assertEqual(self.path.to_label, 'A')
        self.assertEqual(self.path.segments[0], expected)
    
    def test_it_prepends_a_segment_to_an_non_empty_path(self):
        segment = Segment(from_label='B', to_label='A', pct=0.5, min_t=1, curr_t=10, max_t=10)
        self.path.push_segment(segment)
        segment = Segment(from_label='C', to_label='B', pct=0.25, min_t=1, curr_t=10, max_t=10)
        expected = Segment(from_label='C', to_label='B', pct=0.25, min_t=1, curr_t=10, max_t=10)
        self.path.push_segment(segment)
        
        self.assertEqual(self.path.segment_count, 2)
        self.assertEqual(self.path.from_label, 'C')
        self.assertEqual(self.path.to_label, 'A')
        self.assertEqual(self.path.segments[0], expected)

    def test_it_pops_a_segment(self):
        segment = Segment(from_label='B', to_label='A', pct=0.5, min_t=1, curr_t=10, max_t=10)
        self.path.push_segment(segment)
        
        segment = Segment(from_label='C', to_label='B', pct=0.25, min_t=1, curr_t=10, max_t=10)
        self.path.push_segment(segment)
        #expected = self.path.clone()
        
        segment = Segment(from_label='D', to_label='C', pct=0.125, min_t=1, curr_t=10, max_t=10)
        self.path.push_segment(segment)
        
        self.path.pop_segment()
        self.assertEqual(self.path.segment_count, 2)
        self.assertEqual(self.path.from_label, 'C')
        self.assertEqual(self.path.to_label, 'A')
                
    def test_it_fails_to_push_a_disconnected_segment(self):
        segment = Segment(from_label='B', to_label='A', pct=0.5, min_t=1, curr_t=10, max_t=10)
        self.path.push_segment(segment)
        segment = Segment(from_label='D', to_label='C', pct=0.25, min_t=1, curr_t=10, max_t=10)
        with self.assertRaises(AssertionError):
            self.path.push_segment(segment)
    
    def test_it_clones_a_path(self):
        segment = Segment(from_label='B', to_label='A', pct=0.5, min_t=1, curr_t=10, max_t=10)
        self.path.push_segment(segment)
        segment = Segment(from_label='C', to_label='B', pct=0.25, min_t=1, curr_t=10, max_t=10)
        self.path.push_segment(segment)
        segment = Segment(from_label='D', to_label='C', pct=0.125, min_t=1, curr_t=10, max_t=10)
        self.path.push_segment(segment)
        
        clone = self.path.clone()
        self.assertEqual(self.path.from_label,      clone.from_label)
        self.assertEqual(self.path.to_label,        clone.to_label)
        self.assertEqual(self.path.segment_count,   clone.segment_count)
        self.assertEqual(self.path.segments,        clone.segments)
        self.assertEqual(self.path, clone)

    def test_it_computes_a_path_percentual(self):
        segment = Segment(from_label='B', to_label='A', pct=0.5, min_t=1, curr_t=10, max_t=10)
        self.path.push_segment(segment)
        segment = Segment(from_label='C', to_label='B', pct=0.25, min_t=1, curr_t=10, max_t=10)
        self.path.push_segment(segment)
        segment = Segment(from_label='D', to_label='C', pct=0.125, min_t=1, curr_t=10, max_t=10)
        self.path.push_segment(segment)
        self.assertEqual(self.path.pct, 0.5*0.25*0.125)
    