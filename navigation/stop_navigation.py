"""Emergency zero command and pause for the active project controller."""
import builtins
import omni.timeline
for name in ('_warehouse_test_task', '_warehouse_manual_task', '_warehouse_conflict_task', '_warehouse_fourwheel_task'):
    task = getattr(builtins, name, None)
    if task and not task.done():
        task.cancel()
session = getattr(builtins, '_warehouse_navigation', None)
if session is not None:
    session.stop('operator stop')
else:
    omni.timeline.get_timeline_interface().pause()
print('Simulation paused')
