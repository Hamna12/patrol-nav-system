"""Prepare the inspected original start, in the session layer, without Play/save."""
from pathlib import Path
import builtins
import runpy
import omni.timeline
import omni.usd
from pxr import Usd, UsdGeom, UsdPhysics, Gf

timeline = omni.timeline.get_timeline_interface()
if timeline.is_playing():
    raise RuntimeError('Pause Isaac Sim before running preparation')
previous = getattr(builtins, '_warehouse_navigation', None)
if previous and previous.task and not previous.task.done():
    raise RuntimeError('Run Isaac Sim: stop and pause before preparation')
stage = omni.usd.get_context().get_stage()
if stage is None:
    raise RuntimeError('Open the warehouse scene before preparation')
root = stage.GetPrimAtPath('/World/IsaacBot')
chassis = stage.GetPrimAtPath('/World/IsaacBot/IsaacBot/Chassis')
floor = stage.GetPrimAtPath('/World/Structure/FloorCollider_2')
if not root or not chassis or not floor:
    raise RuntimeError('The inspected warehouse robot or floor is missing')
position = UsdGeom.XformCache().GetLocalToWorldTransform(chassis).ExtractTranslation()
bounds = UsdGeom.BBoxCache(Usd.TimeCode.Default(), ['default']).ComputeWorldBound(floor).ComputeAlignedRange()
original_start = abs(position[0] + 31.93499) < 0.05 and abs(position[1] + 13.82238) < 0.05
move_start = timeline.is_stopped() and original_start
prepared_position = position + Gf.Vec3d(3., 0., 0.) if move_start else position
if not all(bounds.GetMin()[i] + 1.5 < prepared_position[i] < bounds.GetMax()[i] - 1.5 for i in (0, 1)):
    raise RuntimeError('Robot is too close to the floor edge. Reopen the original warehouse scene, then run preparation before Play.')
with Usd.EditContext(stage, stage.GetSessionLayer()):
    if move_start:
        translation = root.GetAttribute('xformOp:translate')
        translation.Set(translation.Get() + Gf.Vec3d(3., 0., 0.))
        print('Moved original start 3 m inward onto the inspected clear floor')
    if timeline.is_stopped():
        for prim in Usd.PrimRange(root):
            if prim.HasAPI(UsdPhysics.RigidBodyAPI):
                body = UsdPhysics.RigidBodyAPI(prim)
                body.CreateVelocityAttr().Set(Gf.Vec3f(0.))
                body.CreateAngularVelocityAttr().Set(Gf.Vec3f(0.))
module = runpy.run_path(str(Path(__file__).with_name('run_navigation.py')), run_name='warehouse_prepare')
module['NavigationSession']().setup_ownership(manual=True)
state = 'stopped' if timeline.is_stopped() else 'paused'
print(f'Manual mode prepared; timeline remains {state}. Original USD was not saved.')
