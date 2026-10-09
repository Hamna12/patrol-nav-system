import omni.usd
from pxr import Usd
from isaacsim.core.prims import SingleArticulation
stage = omni.usd.get_context().get_stage()
robot = SingleArticulation('/World/IsaacBot/IsaacBot', reset_xform_properties=False)
robot.initialize()
print('DOF names', robot.dof_names)
print('Rear indices', [robot.get_dof_index(n) for n in ['Rear_Left_Joint','Rear_Right_Joint']])
print('gains', robot.get_articulation_controller().get_gains())
print('max efforts', robot.get_articulation_controller().get_max_efforts())
print('actual', robot.get_joint_velocities())
for path in ['/World/IsaacBot/IsaacBot', '/World/IsaacBot/IsaacBot/Graphs/differential_controller']:
    p = stage.GetPrimAtPath(path)
    print(path, 'valid', bool(p), 'active', p.IsActive() if p else None)
    if p:
        for q in Usd.PrimRange(p, Usd.PrimAllPrimsPredicate):
            if 'Graphs' in str(q.GetPath()):
                print(q.GetPath(), [(a.GetName(), str(a.Get())) for a in q.GetAttributes() if a.GetName() in ['inputs:input0','inputs:input1','inputs:enabled']])
