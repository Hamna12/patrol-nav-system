"""Bounded synthetic W/A key test of the original graph, using NVIDIA input API."""
import asyncio
import builtins
import json
from pathlib import Path
import runpy
import carb.input
import omni.appwindow
import omni.kit.app
import omni.physx
import omni.timeline
import omni.graph.core as og
module = runpy.run_path(str(Path(__file__).with_name('run_navigation.py')), run_name='warehouse_manual_test')
NavigationSession, GRAPH_PATH = module['NavigationSession'], module['GRAPH_PATH']
from robot_pose import RobotPose
from isaacsim.core.prims import SingleArticulation
from isaacsim.core.utils.types import ArticulationAction
import numpy as np

async def run():
    session=NavigationSession()
    session.setup_ownership(manual=True)
    timeline=session.timeline
    provider=carb.input.acquire_input_provider()
    keyboard=omni.appwindow.get_default_app_window().get_keyboard()
    pose=RobotPose()
    rows=[]
    elapsed=0.
    sub=None
    pressed=None
    robot=None
    drive_state=None
    def key(k,down):
        provider.buffer_keyboard_key_event(keyboard, carb.input.KeyboardEventType.KEY_PRESS if down else carb.input.KeyboardEventType.KEY_RELEASE,k,0)
        provider.update_keyboard(keyboard)
    def step(dt):
        nonlocal elapsed
        elapsed+=dt
        rows.append({'t':elapsed,'pose':pose.get_pose(),
                     'body_velocity':robot.get_linear_velocity().tolist(),
                     'graph_wheels':str(og.Controller.get(og.Controller.attribute(GRAPH_PATH+'/DifferentialController.outputs:velocityCommand'))),
                     'joint_names':str(og.Controller.get(og.Controller.attribute(GRAPH_PATH+'/ArrayNames.outputs:array')))})
    error=None
    try:
        timeline.play()
        await omni.kit.app.get_app().next_update_async()
        robot=SingleArticulation('/World/IsaacBot/IsaacBot',reset_xform_properties=False)
        robot.initialize()
        controller=robot.get_articulation_controller()
        drive_state={'damping':controller.get_gains()[1].tolist(), 'max_efforts':controller.get_max_efforts().tolist()}
        sub=omni.physx.get_physx_interface().subscribe_physics_step_events(step)
        async def sequence():
            nonlocal pressed
            while elapsed<5.:
                wanted=carb.input.KeyboardInput.W if 1.<=elapsed<1.5 else carb.input.KeyboardInput.A if 2.5<=elapsed<3.5 else None
                if wanted != pressed:
                    if pressed is not None:
                        key(pressed,False)
                    if wanted is not None:
                        key(wanted,True)
                    pressed=wanted
                await omni.kit.app.get_app().next_update_async()
        await asyncio.wait_for(sequence(),timeout=240.)
    except BaseException as exc:
        error=repr(exc)
        raise
    finally:
        if pressed is not None:
            key(pressed,False)
        timeline.pause()
        sub=None
        robot=SingleArticulation('/World/IsaacBot/IsaacBot',reset_xform_properties=False)
        robot.initialize()
        robot.apply_action(ArticulationAction(joint_velocities=np.zeros(2),joint_indices=np.array([robot.get_dof_index(n) for n in ['Rear_Left_Joint','Rear_Right_Joint']])) )
        Path(__file__).with_name('diagnostics').joinpath('manual_test.json').write_text(json.dumps({'error':error,'drive_state':drive_state,'rows':rows},indent=2))
        print('Manual input test finished; paused')

n=getattr(builtins,'_warehouse_navigation',None)
if n and n.task and not n.task.done():
    raise RuntimeError('Wait for navigation to finish')
builtins._warehouse_manual_task=asyncio.ensure_future(run())
