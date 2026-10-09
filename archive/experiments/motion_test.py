"""Bounded live physics test; stores measurements beside the project."""
import asyncio
import builtins
import json
from pathlib import Path
import numpy as np
import omni.kit.app
import omni.physx
import omni.timeline
import omni.usd
from pxr import Usd
from isaacsim.core.prims import SingleArticulation
from isaacsim.core.utils.types import ArticulationAction
from robot_pose import RobotPose

ROOT = '/World/IsaacBot/IsaacBot'

async def test():
    stage = omni.usd.get_context().get_stage()
    timeline = omni.timeline.get_timeline_interface()
    app = omni.kit.app.get_app()
    if timeline.is_playing():
        raise RuntimeError('Test requires a stopped or paused simulation')
    graph = stage.GetPrimAtPath(ROOT + '/Graphs/differential_controller')
    if graph.IsActive():
        raise RuntimeError('First isolated test requires keyboard graph inactive')
    session = stage.GetSessionLayer()
    original = session.ExportToString()
    robot = None
    subscription = None
    rows = []
    elapsed = 0.0
    error = None
    try:
        with Usd.EditContext(stage, session):
            for side in ['Left', 'Right']:
                stage.GetPrimAtPath(f'{ROOT}/Rear_{side}_Wheel/Rear_{side}_Joint').GetAttribute('drive:angular:physics:targetVelocity').Set(0.0)
        timeline.play()
        await app.next_update_async()
        robot = SingleArticulation(ROOT, name='warehouse_motion_test', reset_xform_properties=False)
        robot.initialize()
        pose = RobotPose()
        indices = np.array([robot.get_dof_index(n) for n in ['Rear_Left_Joint', 'Rear_Right_Joint']], dtype=np.int32)
        def command(v):
            robot.apply_action(ArticulationAction(joint_velocities=np.array(v), joint_indices=indices))
        def step(dt):
            nonlocal elapsed, error
            try:
                elapsed += dt
                v = [0., 0.] if elapsed < 1. or elapsed >= 3. else [0.5, 0.5]
                command(v)
                rows.append({'t': elapsed, 'pose': pose.get_pose(), 'command': v,
                             'actual': robot.get_joint_velocities().tolist(),
                             'linear': robot.get_linear_velocity().tolist()})
                if elapsed >= 5.:
                    timeline.pause()
            except Exception as exc:
                error = str(exc)
                timeline.pause()
        command([0., 0.])
        subscription = omni.physx.get_physx_interface().subscribe_physics_step_events(step)
        async def wait_finished():
            while elapsed < 5. and error is None and timeline.is_playing():
                await app.next_update_async()
        await asyncio.wait_for(wait_finished(), timeout=180.)
        command([0., 0.])
    except Exception as exc:
        error = repr(exc)
        if robot is not None:
            robot.apply_action(ArticulationAction(joint_velocities=np.zeros(2), joint_indices=indices))
        raise
    finally:
        timeline.pause()
        subscription = None
        # Keep zero targets while paused; restoring authored -100 targets here
        # would make an accidental resume unsafe with the keyboard graph off.
        Path(__file__).with_name('diagnostics').joinpath('motion_test.json').write_text(json.dumps({'error':error, 'elapsed':elapsed, 'rows':rows}, indent=2))
        print('Motion test finished; simulation paused. Measurements: diagnostics/motion_test.json')

if getattr(builtins, '_warehouse_test_task', None) and not builtins._warehouse_test_task.done():
    raise RuntimeError('A test is already running')
builtins._warehouse_test_task = asyncio.ensure_future(test())
