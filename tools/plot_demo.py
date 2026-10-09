"""Render the recorded demo route and measured robot trajectory."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
root=Path(__file__).resolve().parents[1]
plan=json.loads((root/'diagnostics/demo_plan.json').read_text())
route=json.loads((root/'diagnostics/demo_route.json').read_text())
fig,ax=plt.subplots(figsize=(10,7))
for obstacle in plan['map']['obstacles']:
    x,y=obstacle['min'][:2]; X,Y=obstacle['max'][:2]
    if X < -31 or x > -18 or Y < -35 or y > -24:continue
    ax.add_patch(Rectangle((x,y),X-x,Y-y,facecolor='#7e8994',edgecolor='none'))
points=[route['start']]+route['route']
ax.plot(*zip(*points),'o--',color='#169c50',lw=2,label='A* planned detour')
ax.plot([route['start'][0],route['goal'][0]],[route['start'][1],route['goal'][1]],':',color='#c93636',label='Blocked direct route')
log=json.loads((root/'diagnostics/demo_validation.json').read_text())
ax.plot(*zip(*[r['pose'][:2] for r in log['rows']]),color='#185ed1',lw=2,label='Measured robot path')
ax.scatter(*route['goal'],s=160,marker='*',color='#169c50')
ax.set(xlim=(-31,-18),ylim=(-35,-24),aspect='equal',xlabel='World X (m)',ylabel='World Y (m)',title='Warehouse prototype: static-map obstacle detour')
ax.grid(alpha=.2);ax.legend();fig.tight_layout()
fig.savefig(root/'diagnostics/demo_result.png',dpi=160)
print(root/'diagnostics/demo_result.png')
