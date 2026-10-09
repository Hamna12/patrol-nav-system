import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'navigation'))
import math
import unittest
from navigation_controller import NavigationController
from waypoint_manager import WaypointManager


class ControllerTests(unittest.TestCase):
    def test_corner_finishes_alignment_before_forward_motion(self):
        c = NavigationController()
        c.turning = True
        v, _, _ = c.compute_command(0,0,-0.15,2,0)
        self.assertEqual(v,0.)
        v, _, _ = c.compute_command(0,0,-0.05,2,0)
        self.assertGreater(v,0.)
        v, _, _ = c.compute_command(0,0,-0.15,2,0)
        self.assertGreater(v,0.)
        v, _, _ = c.compute_command(0,0,-0.25,2,0)
        self.assertEqual(v,0.)

    def test_acceleration_and_stop_are_bounded(self):
        c = NavigationController()
        previous = (0., 0.)
        for _ in range(120):
            current = c.smooth_command(c.max_linear_speed, 0.6, 1/60)
            self.assertLessEqual(abs(current[0]-previous[0]), 0.6/60+1e-9)
            self.assertLessEqual(abs(current[1]-previous[1]), 1.2/60+1e-9)
            previous = current
        self.assertAlmostEqual(current[0], c.max_linear_speed)
        for _ in range(90):
            current = c.smooth_command(0., 0., 1/60)
            self.assertLessEqual(abs(current[0]-previous[0]), 0.9/60+1e-9)
            previous = current
        self.assertEqual(current, (0., 0.))

    def test_braking_before_arrival(self):
        c = NavigationController()
        v, _, _ = c.compute_command(0, 0, 0, c.position_tolerance+0.001, 0)
        self.assertLessEqual(v*v/(2*c.linear_deceleration), 0.001+1e-9)

    def test_arrival_and_heading_wrap(self):
        c = NavigationController()
        self.assertEqual(c.compute_command(0,0,0,0.01,0), (0.,0.,True))
        v,w,done = c.compute_command(0,0,math.pi-0.01,-1,-0.01)
        self.assertGreater(v,0)
        self.assertLess(abs(w),0.1)
        self.assertFalse(done)

    def test_turn_and_four_wheel_order(self):
        c = NavigationController()
        v,w,_ = c.compute_command(0,0,0,0,1)
        self.assertEqual(v,0)
        self.assertEqual(w,0.6)
        self.assertEqual(c.wheel_velocities(0.375,0),(1.,1.,1.,1.))
        self.assertEqual(c.wheel_velocities(0,0.5),(-1.,1.,1.,-1.))

    def test_invalid_target_and_completion(self):
        m = WaypointManager()
        with self.assertRaises(ValueError):
            m.set_waypoints([(float('nan'),0)])
        m.set_waypoints([(1,2),(3,4)])
        m.advance()
        self.assertEqual(m.get_current_waypoint(),(3,4))
        m.advance()
        self.assertTrue(m.completed())
        self.assertIsNone(m.get_current_waypoint())

    def test_nonfinite_pose_rejected(self):
        with self.assertRaises(ValueError):
            NavigationController().compute_command(0,0,float('nan'),1,0)

    def test_approach_slows_down(self):
        c=NavigationController()
        fast=c.compute_command(0,0,0,2,0)[0]
        slow=c.compute_command(0,0,0,0.2,0)[0]
        self.assertLess(slow,fast)
        self.assertLessEqual(fast,c.max_linear_speed)

if __name__ == '__main__':
    unittest.main()
