# Warehouse navigation — Isaac Sim 5.1

## Folder layout

```text
navigation/              Active robot and demo code
config/                  Navigation request JSON
tools/                   Connection, inspection, capture, and plotting tools
tests/                   Controller and planner tests
docs/                    Demo instructions and project guide
diagnostics/             Recorded data and validation evidence
presentation_snapshots/  Slide images and captions
.vscode/                 Ready-to-run VS Code tasks
archive/                 Historical experiments (kept locally)
```

See [the project folder guide](docs/PROJECT_STRUCTURE.md) for file descriptions
and updated terminal commands. Existing VS Code task names are unchanged.

For the obstacle-aware presentation, follow [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md).
Use **Isaac Sim: prepare obstacle demo**, then **Isaac Sim: run navigation request**.
The demo uses A* on the known static USD collision map; the straight-line test
modes below do not perform obstacle planning.

The project executes inside the running simulator through NVIDIA's
`isaacsim.code_editor.vscode` extension at localhost:8226. Enable it in
Window → Extensions. The verified running installation is
`/media/hmna/New Volume/IsaacSim`.

## VS Code workflow

Keep the warehouse scene open and paused. Edit `config/navigation_request.json`, then
run Terminal → Run Task → **Isaac Sim: run navigation request**.
If simulation is already playing, the navigation task pauses it automatically
before switching controllers, then resumes it for the run.

After loading the original USD, before pressing Play, run **Isaac Sim: prepare
original scene** once. It moves the known unsupported starting pose 3 m inward,
zeros initial velocities and drive targets, and prepares manual mode without
starting physics or saving the original file. It refuses an unrecognized edge
position. This preparation is not needed again while using the current safe pose.
Running it again while paused safely restores manual mode without repositioning
the robot. If physics is playing, pause it first.

- `{"operation":"status"}` reports status without moving.
- `{"operation":"nearby"}` drives to a point 0.30 m ahead.
- `{"operation":"drive","distance":3.0}` drives toward a point 3 m ahead,
  allowing sustained cruising before arrival. Distance accepts 0.3–10 m.
  It stops at the destination. Use a clear route:
  floor bounds are checked, but obstacles are not detected.
- `{"operation":"multiple"}` visits points 0.25 m and 0.50 m ahead.
- `{"operation":"demo","goal":[-21,-32]}` runs the obstacle-aware presentation
  after demo preparation; this is the configured demonstration request.
- `{"operation":"waypoints","waypoints":[[x1,y1],[x2,y2]]}` follows your route.
  Replace the placeholders with world X/Y coordinates in metres.

Equivalent terminal commands:

```bash
python3 tools/sim_client.py
python3 tools/sim_client.py navigation/prepare_scene.py
python3 tools/sim_client.py navigation/run_navigation.py
python3 tools/sim_client.py navigation/stop_navigation.py
python3 tools/sim_client.py navigation/manual_mode.py
```

**Isaac Sim: stop and pause** sends zero commands and pauses. **Isaac Sim:
restore manual keyboard** restores the existing W/A/S/D graph while paused;
press Play to use it. Navigation source is recompiled from disk at each start
because Kit retained old module code during ordinary reloads in this session.

## Controller and mode changes

The intended robot has four powered wheels (confirmed by the owner). The saved
USD only defines two rear motors; its front joints have zero gains and effort
limits. Autonomous mode adds matching angular drives to both front joints in the
**session layer**, using the existing rear drive type, stiffness, damping and
force limit. It commands rear-left, rear-right, front-right and front-left by
resolved joint names. Geometry and rear drive parameters are unchanged.

Manual mode removes those session front-drive APIs so the original rear-wheel
keyboard controller retains its passive-front behavior. It explicitly zeros the
front session drive values and live PhysX gains/effort limits: removing the USD
API alone did not clear existing runtime drives. It also corrects the
observed malformed joint-name array to rear-left/rear-right in the session layer.
The graph is disabled during autonomy and enabled during manual mode. Both modes
zero the saved negative rear drive targets at handoff. ROS2 LiDAR is untouched.

The proportional follower uses radius 0.375 m and track width 1.5 m, caps linear
speed at 0.65 m/s and angular speed at 0.6 rad/s, and rotates first for heading
errors greater than 0.20 rad, resuming translation below 0.08 rad. It slows with remaining distance, accepts arrival
within 0.15 m (0.25 m for the obstacle demo), commands zero during a 0.7-second waypoint dwell, and measures the
final stop for 1.5 simulation seconds before pausing. Commands ramp at 0.6 m/s²
when accelerating, 0.9 m/s² when braking, and 1.2 rad/s² when turning.
Approach speed also respects the remaining braking distance. Operator stops
and boundary failures still send zero commands immediately. Final success requires
horizontal speed below 0.02 m/s and yaw rate below 0.03 rad/s.

A run ends after 60 simulation seconds, 600 wall-clock seconds, or five simulation
seconds without distance/heading progress. Straight-line diagnostic modes require
a clear route. The `demo` mode adds static-map A* planning; see docs/DEMO_GUIDE.md for
its limits.

## Starting position and preservation

The saved robot starts partly outside the floor: the rear-right wheel was around
x=-32.55 m, while the floor collider starts at x=-32.1 m. The live test robot was
moved 3 m inward without saving. A fresh scene load restores the problematic pose.
Place the entire robot over the floor before navigation; the runner refuses starts
or waypoints within 1.5 m of its boundary. `navigation/prepare_scene.py` handles the inspected
original start while stopped; it is not an obstacle-aware relocation planner.

Neither original USD is saved or overwritten. Session changes disappear when the
scene is reopened; autonomous mode recreates its front drives on the next run.
Original project Python files are in `diagnostics/original_python`.

## Evidence

`diagnostics/navigation_latest.json` contains the latest run. Preserved named logs
include actual poses, wheel velocities, commands, targets, distances and body
velocities. Failed tuning experiments are retained and are not navigation passes.
See `diagnostics/VALIDATION.md` for the final findings and physical test results.

```bash
python3 -m unittest tests/test_navigation_math.py
```

These local checks verify controller math and waypoint validation; physical
behavior is verified separately in the live simulator.
