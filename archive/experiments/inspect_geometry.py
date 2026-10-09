import omni.usd
from pxr import Usd, UsdGeom, Gf
stage = omni.usd.get_context().get_stage()
root = stage.GetPrimAtPath('/World/IsaacBot/IsaacBot')
cache = UsdGeom.XformCache()
for p in Usd.PrimRange(root):
    if p.GetName() in ('Chassis','Rear_Left_Wheel','Rear_Right_Wheel','Front_Left_Wheel','Front_Right_Wheel'):
        m = cache.GetLocalToWorldTransform(p)
        print(p.GetPath(), 'position',m.ExtractTranslation(),'scale',Gf.Transform(m).GetScale())
        print('angular',p.GetAttribute('physics:angularVelocity').Get())
    if p.GetTypeName() == 'PhysicsRevoluteJoint':
        print(p.GetName(),[(a.GetName(),str(a.Get())) for a in p.GetAttributes() if a.GetName().startswith(('physics:local','physics:axis','drive:'))])
