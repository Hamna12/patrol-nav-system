"""Reversible runtime-gain comparison. Original gains restored in finally."""
import asyncio
import builtins
import json
from pathlib import Path
import numpy as np
import omni.kit.app
import omni.physx
from isaacsim.core.prims import SingleArticulation
from isaacsim.core.utils.types import ArticulationAction
from run_navigation import NavigationSession
from robot_pose import RobotPose

async def test():
    session=NavigationSession()
    session.setup_ownership()
    robot=None
    gains=None
    efforts=None
    sub=None
    elapsed=0.
    rows=[]
    error=None
    try:
        session.timeline.play()
        await omni.kit.app.get_app().next_update_async()
        robot=SingleArticulation('/World/IsaacBot/IsaacBot',reset_xform_properties=False)
        robot.initialize()
        ctrl=robot.get_articulation_controller()
        kp,kd=ctrl.get_gains();gains=(kp.copy(),kd.copy())
        efforts=ctrl.get_max_efforts().copy()
        names=['Rear_Left_Joint','Rear_Right_Joint','Front_Right_Joint','Front_Left_Joint']
        indices=np.array([robot.get_dof_index(n) for n in names])
        kd[indices[2:]]=kd[indices[0]]
        ctrl.set_gains(kps=kp,kds=kd,save_to_usd=False)
        enabled_efforts=efforts.copy()
        enabled_efforts[indices[2:]]=efforts[indices[0]]
        ctrl.set_max_efforts(enabled_efforts)
        pose=RobotPose()
        def command(v):
            robot.apply_action(ArticulationAction(joint_velocities=np.asarray(v),joint_indices=indices))
        def step(dt):
            nonlocal elapsed
            elapsed+=dt
            wheels=[-1.2,1.2,1.2,-1.2] if 0.5<=elapsed<2.5 else [0.,0.,0.,0.]
            command(wheels)
            rows.append({'t':elapsed,'pose':pose.get_pose(),'wheels':wheels,'actual':robot.get_joint_velocities().tolist(),'body_velocity':robot.get_linear_velocity().tolist()})
            if elapsed>=4.:
                session.timeline.pause()
        command([0.,0.,0.,0.])
        sub=omni.physx.get_physx_interface().subscribe_physics_step_events(step)
        async def wait():
            while elapsed<4. and session.timeline.is_playing():
                await omni.kit.app.get_app().next_update_async()
        await asyncio.wait_for(wait(),timeout=180.)
    except BaseException as exc:
        error=repr(exc)
        raise
    finally:
        session.timeline.pause()
        sub=None
        if robot is not None and gains is not None:
            command([0.,0.,0.,0.])
            ctrl.set_gains(kps=gains[0],kds=gains[1],save_to_usd=False)
            ctrl.set_max_efforts(efforts)
        Path(__file__).with_name('diagnostics').joinpath('four_wheel_comparison.json').write_text(json.dumps({'error':error,'original_gains':[x.tolist() for x in gains] if gains else None,'rows':rows},indent=2))

builtins._warehouse_fourwheel_task=asyncio.ensure_future(test())
