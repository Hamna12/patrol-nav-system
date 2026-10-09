"""Summarize preserved physical measurements; does not control the simulator."""
import json
import math
from pathlib import Path

root=Path(__file__).resolve().parents[1]/'diagnostics'
summaries={}
for name in ('one_waypoint','multiple_waypoints','turning_waypoints'):
    path=root/(name+'.json')
    if not path.exists():
        continue
    d=json.loads(path.read_text()); rows=d['rows']; final=rows[-1]
    tail=[r for r in rows if r['t']>=final['t']-0.5]
    summaries[name]={
        'state':d['state'],'reason':d['reason'],'simulation_seconds':d['elapsed'],
        'reached':d['reached'],'requested':len(d['waypoints']),
        'final_error_m':math.dist(final['pose'][:2],d['waypoints'][-1]),
        'final_speed_m_s':math.hypot(*final['body_velocity'][:2]),
        'max_speed_last_half_second_m_s':max(math.hypot(*r['body_velocity'][:2]) for r in tail),
        'heading_change_rad':math.atan2(math.sin(final['pose'][2]-rows[0]['pose'][2]),math.cos(final['pose'][2]-rows[0]['pose'][2])),
        'turn_command_steps':sum(abs(r['angular_command'])>0.1 for r in rows),
    }
path=root/'controller_conflict.json'
if path.exists():
    comparisons=[]
    for d in json.loads(path.read_text()):
        rows=d['rows']; a=min(rows,key=lambda r:abs(r['t']-0.5));b=min(rows,key=lambda r:abs(r['t']-1.5))
        comparisons.append({'graph_active':d['graph_active'],'command_interval_displacement_m':math.dist(a['pose'][:2],b['pose'][:2]),'final_pose':rows[-1]['pose']})
    summaries['controller_conflict']=comparisons
(root/'validation_summary.json').write_text(json.dumps(summaries,indent=2))
print(json.dumps(summaries,indent=2))
