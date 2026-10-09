import asyncio
import numpy as np

from isaacsim.core.prims import SingleArticulation
from isaacsim.core.utils.types import ArticulationAction

ROBOT_PATH = "/World/IsaacBot/IsaacBot"


async def main():
    robot = SingleArticulation(
        prim_path=ROBOT_PATH,
        name="warehouse_navigation_robot"
    )

    robot.initialize()

    print("\n========== WHEEL DIAGNOSTIC ==========")
    print("DOF names:", robot.dof_names)

    wheel_indices = np.array([0, 1], dtype=np.int32)

    try:
        for step in range(30):
            robot.apply_action(
                ArticulationAction(
                    joint_velocities=np.array([1.0, 1.0]),
                    joint_indices=wheel_indices
                )
            )

            await asyncio.sleep(0.1)

            if step % 5 == 0:
                velocities = robot.get_joint_velocities()
                print(
                    f"Step {step}: "
                    f"Left={velocities[0]:.3f}, "
                    f"Right={velocities[1]:.3f}"
                )

    finally:
        robot.apply_action(
            ArticulationAction(
                joint_velocities=np.array([0.0, 0.0]),
                joint_indices=wheel_indices
            )
        )

        print("Stop command sent.")
        print("======================================")


asyncio.ensure_future(main())