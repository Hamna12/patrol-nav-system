import math


class WaypointManager:

    def __init__(self):
        self.waypoints = []
        self.current_index = 0

    def set_waypoints(self, waypoints):
        self.waypoints = list(waypoints)
        self.current_index = 0

    def get_current_waypoint(self):

        if self.current_index >= len(self.waypoints):
            return None

        return self.waypoints[self.current_index]

    def advance(self):
        self.current_index += 1

    def completed(self):
        return self.current_index >= len(self.waypoints)

    def distance_to_waypoint(self, x, y):

        waypoint = self.get_current_waypoint()

        if waypoint is None:
            return 0.0

        target_x, target_y = waypoint

        return math.hypot(
            target_x - x,
            target_y - y
        )