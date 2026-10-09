"""Read-only final handoff evidence from the live simulator."""
import json
from pathlib import Path
import numpy as np
import omni.timeline
import omni.usd
from isaacsim.core.prims import SingleArticulation
from pxr import UsdPhysics

stage = omni.usd.get_context().get_stage()
root = '/World/IsaacBot/IsaacBot'
robot = SingleArticulation(root, reset_xform_properties=False)
robot.initialize()
controller = robot.get_articulation_controller()
result = {
    'playing': omni.timeline.get_timeline_interface().is_playing(),
    'graph_active': stage.GetPrimAtPath(root+'/Graphs/differential_controller').IsActive(),
    'dof_names': robot.dof_names,
    'damping': controller.get_gains()[1].tolist(),
    'max_efforts': controller.get_max_efforts().tolist(),
    'front_drive_apis': [stage.GetPrimAtPath(root+f'/Front_{s}_Wheel/Front_{s}_Joint').HasAPI(UsdPhysics.DriveAPI, 'angular') for s in ('Right','Left')],
    'applied_targets': robot.get_applied_action().joint_velocities.tolist(),
    'horizontal_speed': float(np.linalg.norm(robot.get_linear_velocity()[:2])),
}
Path(__file__).with_name('diagnostics').joinpath('final_handoff.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
