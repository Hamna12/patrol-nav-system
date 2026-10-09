"""Stage a repeatable static-map demo; session-only teleport, no driving/save."""
import builtins
import types
import json
import math
import runpy
from pathlib import Path
import numpy as np
import omni.timeline
import omni.usd
from pxr import Usd, UsdGeom, Gf
from isaacsim.core.prims import SingleArticulation
from isaacsim.core.utils.types import ArticulationAction
SOURCE=Path(__file__).resolve().parent
PROJECT=SOURCE.parent
previous=getattr(builtins,'_warehouse_navigation',None)
if previous and previous.task and not previous.task.done():
    raise RuntimeError('Stop navigation before preparing the demo')
timeline=omni.timeline.get_timeline_interface()
if timeline.is_playing():
    raise RuntimeError('Run Isaac Sim: stop and pause first')
planner_module=types.ModuleType('obstacle_planner')
exec(compile((SOURCE/'obstacle_planner.py').read_text(),str(SOURCE/'obstacle_planner.py'),'exec'),planner_module.__dict__)
stage=omni.usd.get_context().get_stage()
data=planner_module.scene_map(stage)
planner=planner_module.WarehousePlanner(data)
start=(-28.,-28.); goal=(-21.,-32.)
route=planner.plan(start,goal)
module=runpy.run_path(str(SOURCE/'run_navigation.py'),run_name='warehouse_demo_prepare')
session=module['NavigationSession']()
session.setup_ownership()
if timeline.is_stopped():
    root=stage.GetPrimAtPath('/World/IsaacBot')
    chassis=stage.GetPrimAtPath('/World/IsaacBot/IsaacBot/Chassis')
    pos=UsdGeom.XformCache().GetLocalToWorldTransform(chassis).ExtractTranslation()
    with Usd.EditContext(stage,stage.GetSessionLayer()):
        attr=root.GetAttribute('xformOp:translate')
        attr.Set(attr.Get()+Gf.Vec3d(start[0]-pos[0],start[1]-pos[1],0.))
else:
    robot=SingleArticulation('/World/IsaacBot/IsaacBot',reset_xform_properties=False)
    robot.initialize()
    if not robot.handles_initialized:
        raise RuntimeError('Physics handles unavailable; reopen scene before preparing demo')
    pose=module['RobotPose']().get_pose()
    position,orientation=robot.get_world_pose()
    position+=np.array([start[0]-pose[0],start[1]-pose[1],0.])
    # Repeat the tested starting heading, regardless of the previous finish.
    c=math.cos((-0.42-pose[2])/2); s=math.sin((-0.42-pose[2])/2)
    w,x,y,z=orientation
    orientation=np.array([c*w-s*z,c*x-s*y,c*y+s*x,c*z+s*w])
    robot.set_world_pose(position=position,orientation=orientation)
    robot.set_linear_velocity(np.zeros(3)); robot.set_angular_velocity(np.zeros(3))
    robot.apply_action(ArticulationAction(joint_velocities=np.zeros(robot.num_dof)))
with Usd.EditContext(stage,stage.GetSessionLayer()):
    curve=UsdGeom.BasisCurves.Define(stage,'/World/NavigationDemo/PlannedRoute')
    curve.CreateTypeAttr('linear')
    curve.CreateCurveVertexCountsAttr([len(route)+1])
    curve.CreatePointsAttr([Gf.Vec3f(x,y,0.08) for x,y in [start]+route])
    curve.CreateWidthsAttr([0.07]); curve.SetWidthsInterpolation('constant')
    curve.CreateDisplayColorAttr([Gf.Vec3f(0.05,1.,0.1)])
    marker=UsdGeom.Sphere.Define(stage,'/World/NavigationDemo/Goal')
    marker.CreateRadiusAttr(0.22)
    UsdGeom.XformCommonAPI(marker).SetTranslate(Gf.Vec3d(*goal,0.25))
    marker.CreateDisplayColorAttr([Gf.Vec3f(0.05,1.,0.1)])
(PROJECT/'diagnostics/demo_plan.json').write_text(json.dumps({'start':start,'goal':goal,'route':route,'clearance':planner.clearance,'map':data},indent=2))
(PROJECT/'config/navigation_request.json').write_text(json.dumps({'operation':'demo','goal':list(goal)},indent=2)+'\n')
session.state='demo_ready'; builtins._warehouse_navigation=session
runpy.run_path(str(SOURCE/'demo_camera.py'),run_name='warehouse_demo_camera')
print('DEMO READY: robot staged at',start,'goal',goal,'planned route',route)
print('Session-only staging; original USD unchanged. Run navigation request to drive.')
