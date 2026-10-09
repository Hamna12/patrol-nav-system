import builtins
import omni.timeline
t = getattr(builtins, '_warehouse_test_task', None)
print('playing', omni.timeline.get_timeline_interface().is_playing())
print('task', t)
if t and t.done():
    print('exception', repr(t.exception()))
n = getattr(builtins, '_warehouse_navigation', None)
if n:
    print('navigation', n.state, n.elapsed, n.reason)
    if n.robot and n.robot.handles_initialized:
        print('gains',n.robot.get_articulation_controller().get_gains())
        print('effort limits',n.robot.get_articulation_controller().get_max_efforts())
    if n.rows:
        print('latest', n.rows[-1])
    if n.task and n.task.done():
        print('navigation exception', repr(n.task.exception()))
m = getattr(builtins, '_warehouse_manual_task', None)
if m:
    print('manual task',m)
    if m.done():
        print('manual exception',repr(m.exception()))
c = getattr(builtins, '_warehouse_conflict_task', None)
if c:
    print('conflict task',c)
    if c.done():
        print('conflict exception',repr(c.exception()))
f = getattr(builtins, '_warehouse_fourwheel_task', None)
if f:
    print('four-wheel task',f)
    if f.done():
        print('four-wheel exception',repr(f.exception()))
