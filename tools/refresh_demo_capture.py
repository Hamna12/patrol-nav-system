"""Refresh the staged physics pose for a genuine start screenshot, then pause."""
import asyncio
import builtins
import runpy
from pathlib import Path
import omni.timeline
import omni.kit.app
async def refresh():
    t=omni.timeline.get_timeline_interface()
    n=getattr(builtins,'_warehouse_navigation',None)
    if not n or n.state!='demo_ready' or t.is_playing():
        raise RuntimeError('Requires paused staged demo')
    try:
        t.play()
        for _ in range(3):await omni.kit.app.get_app().next_update_async()
    finally:
        t.pause()
    for _ in range(3):await omni.kit.app.get_app().next_update_async()
    runpy.run_path(str(Path(__file__).with_name('capture_presentation.py')),run_name='capture_refreshed')
builtins._warehouse_refresh_task=asyncio.ensure_future(refresh())
print('Refreshing staged pose; automatic pause and capture follow')
