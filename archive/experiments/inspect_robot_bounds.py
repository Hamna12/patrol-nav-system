import omni.usd
from pxr import Usd, UsdGeom, UsdPhysics
stage=omni.usd.get_context().get_stage()
cache=UsdGeom.BBoxCache(Usd.TimeCode.Default(), ['default','render','proxy'])
for p in Usd.PrimRange(stage.GetPrimAtPath('/World/IsaacBot/IsaacBot')):
    if p.HasAPI(UsdPhysics.CollisionAPI):
        b=cache.ComputeWorldBound(p).ComputeAlignedRange()
        print(p.GetPath(), 'bounds',b.GetMin(),b.GetMax(),'mass',p.GetAttribute('physics:mass').Get(),'material',p.GetRelationship('material:binding:physics').GetTargets())
        print('collision enabled',p.GetAttribute('physics:collisionEnabled').Get(),'approximation',p.GetAttribute('physics:approximation').Get())
        if p.GetTypeName() == 'Mesh':
            points=p.GetAttribute('points').Get()
            print('actual mesh local min/max', [(min(v[i] for v in points),max(v[i] for v in points)) for i in range(3)])
            from pxr import Gf
            m=UsdGeom.XformCache().GetLocalToWorldTransform(p)
            print('world vertex z min',min(m.Transform(Gf.Vec3d(v))[2] for v in points),'axle',m.TransformDir(Gf.Vec3d(0,0,1)))
