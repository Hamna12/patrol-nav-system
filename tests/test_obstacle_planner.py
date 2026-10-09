import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'navigation'))
import unittest
from obstacle_planner import WarehousePlanner

class PlannerTests(unittest.TestCase):
    def setUp(self):
        self.planner=WarehousePlanner({'floor_min':[-10,-10,0], 'floor_max':[10,10,0],
            'obstacles':[{'min':[-1,-1,0], 'max':[1,1,2]}]},clearance=.5)

    def test_detour_has_clear_segments(self):
        p=self.planner; start=(-5,0); goal=(5,0)
        self.assertFalse(p.segment_free(start,goal))
        route=p.plan(start,goal)
        self.assertGreater(len(route),1)
        for end in route:
            self.assertTrue(p.segment_free(start,end)); start=end
        self.assertEqual(route[-1],goal)

    def test_blocked_goal_rejected(self):
        with self.assertRaises(ValueError):self.planner.plan((-5,0),(0,0))

    def test_narrow_gap_rejected(self):
        p=WarehousePlanner({'floor_min':[-5,-5,0],'floor_max':[5,5,0],
            'obstacles':[{'min':[-.1,-5,0],'max':[.1,-.2,2]},
                         {'min':[-.1,.2,0],'max':[.1,5,2]}]},clearance=.5)
        with self.assertRaises(ValueError):p.plan((-3,0),(3,0))

    def test_segment_cannot_clip_corner(self):
        self.assertFalse(self.planner.segment_free((-2,1.4),(2,1.4)))
        self.assertTrue(self.planner.segment_free((-2,1.6),(2,1.6)))

if __name__=='__main__':unittest.main()
