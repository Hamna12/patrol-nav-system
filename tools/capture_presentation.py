"""Capture actual simulator pixels; no generated or reconstructed scene images."""
import asyncio
import builtins
from pathlib import Path
import omni.kit.app
from omni.kit.viewport.utility import get_active_viewport, capture_viewport_to_file
ROOT=Path(__file__).resolve().parents[1]
async def capture():
    viewport=get_active_viewport()
    if viewport is None:
        raise RuntimeError('No active viewport')
    session=getattr(builtins,'_warehouse_navigation',None)
    state=session.state if session else 'unknown'
    filename='01_demo_start.png' if state=='demo_ready' else '02_demo_current_view.png'
    for _ in range(5):
        await omni.kit.app.get_app().next_update_async()
    result=capture_viewport_to_file(viewport,str(ROOT/'presentation_snapshots'/filename))
    await result.wait_for_result()
    print('Saved actual viewport:',filename,'navigation state:',state)
    (ROOT/'presentation_snapshots'/(filename+'.txt')).write_text('Actual Isaac Sim viewport capture. Navigation state: '+state+'\n')
builtins._warehouse_capture_task=asyncio.ensure_future(capture())
print('Viewport capture scheduled')
