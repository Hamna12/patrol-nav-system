"""Read-only export of scene collision bounds for the known-map prototype."""
import json
from pathlib import Path
import omni.usd
from pxr import Usd, UsdGeom, UsdPhysics
stage=omni.usd.get_context().get_stage()
cache=UsdGeom.BBoxCache(Usd.TimeCode.Default(), ['default','render','proxy'])
obstacles=[]
robot=[]
for p in Usd.PrimRange.Stage(stage, Usd.TraverseInstanceProxies()):
    if not p.HasAPI(UsdPhysics.CollisionAPI):
        continue
    if p.GetAttribute('physics:collisionEnabled').Get() is False:
        continue
    b=cache.ComputeWorldBound(p).ComputeAlignedRange()
    if b.IsEmpty():
        continue
    lo,hi=list(b.GetMin()),list(b.GetMax())
    row={'path':str(p.GetPath()),'min':lo,'max':hi}
    if str(p.GetPath()).startswith('/World/IsaacBot'):
        robot.append(row)
    elif hi[2]>0.08 and lo[2]<1.8:
        obstacles.append(row)
p=stage.GetPrimAtPath('/World/IsaacBot/IsaacBot/Chassis')
pose=list(UsdGeom.XformCache().GetLocalToWorldTransform(p).ExtractTranslation())
f=cache.ComputeWorldBound(stage.GetPrimAtPath('/World/Structure/FloorCollider_2')).ComputeAlignedRange()
data={'pose':pose,'floor_min':list(f.GetMin()),'floor_max':list(f.GetMax()),'robot':robot,'obstacles':obstacles}
(Path(__file__).resolve().parents[1]/'diagnostics').joinpath('demo_map.json').write_text(json.dumps(data,indent=2))
print('Pose',pose,'robot bounds',robot,'obstacles',len(obstacles))
print('Nearby obstacles:',[o for o in obstacles if all(o['min'][i]-5<pose[i]<o['max'][i]+5 for i in (0,1))])
