import math

from isaacsim.core.prims import SingleXFormPrim


class RobotPose:

    def __init__(self):
        self.chassis_path = (
            "/World/IsaacBot/IsaacBot/Chassis"
        )

        self.chassis = SingleXFormPrim(
            prim_path=self.chassis_path,
            name="navigation_chassis",
            reset_xform_properties=False
        )

    def get_pose(self):

        position, quaternion = (
            self.chassis.get_world_pose()
        )

        x = float(position[0])
        y = float(position[1])

        # Isaac Sim quaternion: W, X, Y, Z
        w, qx, qy, qz = quaternion

        yaw = math.atan2(
            2.0 * (w * qz + qx * qy),
            1.0 - 2.0 * (qy * qy + qz * qz)
        )

        return x, y, yaw
