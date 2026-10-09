"""Move the live articulation onto the inspected clear floor; never save USD."""
import json
from pathlib import Path
import numpy as np
import omni.timeline
from isaacsim.core.prims import SingleArticulation
if omni.timeline.get_timeline_interface().is_playing():
    raise RuntimeError('Wait until the test is paused')
robot=SingleArticulation('/World/IsaacBot/IsaacBot', reset_xform_properties=False)
robot.initialize()
position, orientation=robot.get_world_pose()
Path(__file__).with_name('diagnostics').joinpath('pose_before_relocation.json').write_text(json.dumps({'position':position.tolist(),'orientation':orientation.tolist()}))
position=position+np.array([3.,0.,0.15])
robot.set_world_pose(position=position,orientation=orientation)
robot.set_linear_velocity(np.zeros(3))
robot.set_angular_velocity(np.zeros(3))
print('Live articulation repositioned to',position)
