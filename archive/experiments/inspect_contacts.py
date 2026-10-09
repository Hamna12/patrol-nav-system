import omni.usd
from pxr import UsdGeom, Usd, Gf
stage=omni.usd.get_context().get_stage()
cache=UsdGeom.BBoxCache(Usd.TimeCode.Default(), ['default','render','proxy'])
robot=stage.GetPrimAtPath('/World/IsaacBot/IsaacBot/Chassis')
c=UsdGeom.XformCache().GetLocalToWorldTransform(robot).ExtractTranslation()
print('Chassis',c)
c = c + Gf.Vec3d(3,0,0)
print('Candidate test position', c)
for p in stage.Traverse():
    if '/IsaacBot' in str(p.GetPath()) or not p.HasAPI(__import__('pxr.UsdPhysics',fromlist=['CollisionAPI']).CollisionAPI):
        continue
    b=cache.ComputeWorldBound(p).ComputeAlignedRange()
    lo,hi=b.GetMin(),b.GetMax()
    if all(lo[i]-1.6 <= c[i] <= hi[i]+1.6 for i in (0,1)) and hi[2]>=0 and lo[2]<1.5:
        print(p.GetPath(),lo,hi)
