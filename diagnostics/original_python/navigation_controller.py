import math


class NavigationController:

    def __init__(self):

        self.linear_gain = 0.5
        self.angular_gain = 1.5

        self.max_linear_speed = 0.25
        self.max_angular_speed = 0.6

        self.position_tolerance = 0.15

        # Adjust if chassis heading differs
        # from the robot's forward direction.
        self.heading_offset = 0.0

    @staticmethod
    def normalize_angle(angle):

        return math.atan2(
            math.sin(angle),
            math.cos(angle)
        )

    def compute_command(
        self,
        current_x,
        current_y,
        current_yaw,
        target_x,
        target_y
    ):

        dx = target_x - current_x
        dy = target_y - current_y

        distance = math.hypot(dx, dy)

        if distance <= self.position_tolerance:
            return 0.0, 0.0, True

        target_heading = math.atan2(dy, dx)

        robot_heading = (
            current_yaw + self.heading_offset
        )

        heading_error = self.normalize_angle(
            target_heading - robot_heading
        )

        angular_velocity = (
            self.angular_gain * heading_error
        )

        angular_velocity = max(
            -self.max_angular_speed,
            min(
                self.max_angular_speed,
                angular_velocity
            )
        )

        # Rotate in place when facing
        # significantly away from target.
        if abs(heading_error) > 0.35:
            linear_velocity = 0.0
        else:
            linear_velocity = min(
                self.max_linear_speed,
                self.linear_gain * distance
            )

        return (
            linear_velocity,
            angular_velocity,
            False
        )