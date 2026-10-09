"""Read-only presentation status for the current navigation session."""
import builtins
session=getattr(builtins,'_warehouse_navigation',None)
if session is None:
    print('Navigation has not been started.')
else:
    print('State:',session.state)
    print('Reason:',session.reason or 'in progress')
    print('Simulation seconds:',round(session.elapsed,2))
    if hasattr(session,'manager'):
        print('Waypoints reached:',session.manager.current_index,'/',len(session.manager.waypoints))
    if session.rows:
        row=session.rows[-1]
        print('Robot XY:',[round(v,2) for v in row['pose'][:2]])
        print('Distance to current waypoint:',round(row['distance'],2),'m')
