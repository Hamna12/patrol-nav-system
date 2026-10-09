"""Temporarily compose inactive keyboard graph while paused; never save."""
import json
from pathlib import Path
import omni.timeline
import omni.usd
from pxr import Usd
from inspect_scene import inspect

if omni.timeline.get_timeline_interface().is_playing():
    raise RuntimeError('Pause before inspecting inactive graph')
stage = omni.usd.get_context().get_stage()
session = stage.GetSessionLayer()
before = session.ExportToString()
try:
    with Usd.EditContext(stage, session):
        stage.GetPrimAtPath('/World/IsaacBot/IsaacBot/Graphs/differential_controller').SetActive(True)
    report = inspect(stage)
    Path(__file__).with_name('diagnostics').joinpath('keyboard_composed.json').write_text(json.dumps(report, indent=2))
    for p in report['prims']:
        if '/Graphs/differential_controller/' in p['path']:
            print(p['path'].rsplit('/',1)[-1], {k:v for k,v in p['attributes'].items() if k.startswith('inputs:') and (v['value'] != 'None' or v['connections'])})
finally:
    session.ImportFromString(before)
