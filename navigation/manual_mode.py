"""Restore the existing keyboard graph while paused; keep saved USD unchanged."""
import builtins
import runpy
from pathlib import Path
NavigationSession = runpy.run_path(str(Path(__file__).with_name('run_navigation.py')), run_name='warehouse_manual_module')['NavigationSession']
previous = getattr(builtins, '_warehouse_navigation', None)
if previous and previous.task and not previous.task.done():
    raise RuntimeError('Stop navigation before restoring manual mode')
session = NavigationSession()
session.setup_ownership(manual=True)
session.state = 'manual'
builtins._warehouse_navigation = session
print('Manual W/A/S/D graph restored. Press Play to use keyboard controls.')
