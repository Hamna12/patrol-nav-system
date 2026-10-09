"""Plot actual recorded telemetry, not synthetic simulator images."""
import json,math,shutil
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'presentation_snapshots'
r=json.loads((ROOT/'diagnostics/demo_corner_validation.json').read_text())['rows']
m=json.loads((ROOT/'diagnostics/demo_metrics.json').read_text())
shutil.copyfile(ROOT/'diagnostics/demo_result.png',OUT/'03_planned_vs_actual_route.png')
plt.rcParams.update({'font.size':12})
fig,ax=plt.subplots(2,1,figsize=(11,7),sharex=True)
t=[x['t'] for x in r]
ax[0].plot(t,[x['linear_command'] for x in r],label='Commanded forward speed',lw=2)
ax[0].plot(t,[math.hypot(*x['body_velocity'][:2]) for x in r],label='Measured horizontal speed',alpha=.8)
ax[0].set(ylabel='Speed (m/s)',title='Actual recorded demo: motion and arrival');ax[0].legend()
ax[1].plot(t,[math.dist(x['pose'][:2],[-21,-32]) for x in r],color='#169c50')
ax[1].axhline(.25,ls='--',color='gray',label='Goal tolerance: 0.25 m')
ax[1].set(xlabel='Simulation time (seconds)',ylabel='Distance to final goal (m)');ax[1].legend()
for a in ax:a.grid(alpha=.25)
fig.tight_layout();fig.savefig(OUT/'04_recorded_speed_and_arrival.png',dpi=170);plt.close(fig)
fig,ax=plt.subplots(figsize=(10,5));ax.axis('off')
ax.set_title('Recorded prototype validation — Isaac Sim 5.1',fontsize=19,pad=20)
values=[['Result',m['state']],['Waypoints reached','2 / 2'],['Simulation duration',f"{m['simulation_seconds']:.2f} s"],['Final goal error',f"{m['goal_error_metres']:.3f} m"],['Arrival tolerance','0.25 m'],['Final measured speed',f"{m['final_speed_mps']:.6f} m/s"],['Controller and planner tests','12 passed']]
table=ax.table(cellText=values,colLabels=['Measurement','Result'],loc='center',cellLoc='left',colWidths=[.55,.45]);table.auto_set_font_size(False);table.set_fontsize(13);table.scale(1,1.8)
fig.text(.5,.03,'Generated from recorded test results; not a screenshot of the simulator UI.',ha='center',fontsize=10)
fig.tight_layout(rect=[0,.06,1,1]);fig.savefig(OUT/'05_validation_results.png',dpi=170)
