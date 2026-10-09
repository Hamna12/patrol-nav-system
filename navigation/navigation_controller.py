"""Bounded differential-drive waypoint control for four powered wheels."""
import math


class NavigationController:
    def __init__(self):
        self.linear_gain = 1.5
        self.angular_gain = 1.5
        self.max_linear_speed = 0.65
        self.max_angular_speed = 0.6
        self.position_tolerance = 0.15
        self.heading_offset = 0.0
        self.turning = False
        self.linear_acceleration = 0.6
        self.linear_deceleration = 0.9
        self.angular_acceleration = 1.2
        self.last_linear = 0.0
        self.last_angular = 0.0

    def smooth_command(self, linear, angular, dt):
        """Limit command changes per simulation second, including normal stops."""
        if not all(math.isfinite(v) for v in (linear, angular, dt)) or dt <= 0:
            raise ValueError('Commands must be finite and dt positive')
        rate = self.linear_acceleration if abs(linear) > abs(self.last_linear) else self.linear_deceleration
        self.last_linear += max(-rate*dt, min(rate*dt, linear-self.last_linear))
        rate = self.angular_acceleration
        self.last_angular += max(-rate*dt, min(rate*dt, angular-self.last_angular))
        return self.last_linear, self.last_angular

    @staticmethod
    def normalize_angle(angle):
        return math.atan2(math.sin(angle), math.cos(angle))

    def wheel_velocities(self, linear, angular):
        """Rear-left, rear-right, front-right, front-left targets in rad/s."""
        left = (linear - 0.75 * angular) / 0.375
        right = (linear + 0.75 * angular) / 0.375
        return left, right, right, left

    def compute_command(self, current_x, current_y, current_yaw, target_x, target_y):
        if not all(math.isfinite(v) for v in (current_x,current_y,current_yaw,target_x,target_y)):
            raise ValueError('Pose and waypoint must be finite')
        dx,dy = target_x-current_x,target_y-current_y
        distance = math.hypot(dx,dy)
        if distance <= self.position_tolerance:
            self.turning = False
            return 0.,0.,True
        error = self.normalize_angle(math.atan2(dy,dx)-current_yaw-self.heading_offset)
        angular = max(-self.max_angular_speed,min(self.max_angular_speed,self.angular_gain*error))
        # Finish aligning before translating. Separate entry/exit thresholds
        # avoid repeatedly switching between driving and turning near a corner.
        self.turning = abs(error) > (0.08 if self.turning else 0.20)
        if self.turning:
            angular = math.copysign(max(abs(angular), min(0.35, self.max_angular_speed)), error)
        remaining = max(0., distance-self.position_tolerance)
        braking_speed = math.sqrt(2*self.linear_deceleration*remaining)
        approach_speed = self.linear_gain * max(0., distance - 0.08)
        if distance < 0.5:
            approach_speed = min(approach_speed, 0.2)
        linear = 0. if self.turning else min(self.max_linear_speed,approach_speed,braking_speed)
        return linear,angular,False
