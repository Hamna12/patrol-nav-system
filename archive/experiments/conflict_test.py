"""Compare the original wall-clock command pattern with graph on/off."""
import asyncio
import builtins
import json
from pathlib import Path
import runpy
import numpy as np
import omni.kit.app
import omni.physx
import omni.timeline
from isaacsim.core.prims import SingleArticulation
from isaacsim.core.utils.types import ArticulationAction
from pxr import Usd
import omni.usd
NavigationSession = runpy.run_path(str(Path(__file__).with_name('run_navigation.py')), run_name='warehouse_conflict_module')['NavigationSession']
from robot_pose import RobotPose

async def compare():
    results=[]
    session=NavigationSession()
    try:
        for active in (True,False):
            session.setup_ownership(manual=True)
            with Usd.EditContext(session.stage,session.stage.GetSessionLayer()):
                session.stage.GetPrimAtPath('/World/IsaacBot/IsaacBot/Graphs/differential_controller').SetActive(active)
            rows=[]
            elapsed=0.
            sub=None
            robot=None
            try:
                session.timeline.play()
                await omni.kit.app.get_app().next_update_async()
                robot=SingleArticulation('/World/IsaacBot/IsaacBot',reset_xform_properties=False)
                robot.initialize()
                indices=np.array([robot.get_dof_index(n) for n in ['Rear_Left_Joint','Rear_Right_Joint']])
                pose=RobotPose()
                def command(v):
                    robot.apply_action(ArticulationAction(joint_velocities=np.array([v,v]),joint_indices=indices))
                def step(dt):
                    nonlocal elapsed
                    elapsed+=dt
                    rows.append({'t':elapsed,'pose':pose.get_pose(),'actual':robot.get_joint_velocities().tolist(),
                                 'applied':robot.get_applied_action().joint_velocities.tolist()})
                sub=omni.physx.get_physx_interface().subscribe_physics_step_events(step)
                async def sequence():
                    while elapsed<3.:
                        command(0.5 if 0.5<=elapsed<1.5 else 0.)
                        await asyncio.sleep(0.1)
                await asyncio.wait_for(sequence(),timeout=180.)
            finally:
                session.timeline.pause()
                sub=None
                if robot is not None:
                    command(0.)
                results.append({'graph_active':active,'rows':rows})
                await omni.kit.app.get_app().next_update_async()
    finally:
        session.timeline.pause()
        await omni.kit.app.get_app().next_update_async()
        session.setup_ownership(manual=True)
        Path(__file__).with_name('diagnostics').joinpath('controller_conflict.json').write_text(json.dumps(results,indent=2))

n=getattr(builtins,'_warehouse_navigation',None)
if n and n.task and not n.task.done():
    raise RuntimeError('Navigation still running')
builtins._warehouse_conflict_task=asyncio.ensure_future(compare())
