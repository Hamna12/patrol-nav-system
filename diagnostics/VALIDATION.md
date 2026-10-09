# Physical validation — 2026-10-09

These results were measured in the live Isaac Sim 5.1 warehouse before the system restart. Successful execution alone was not counted as a pass.

| Test | Measured result | Evidence |
|---|---|---|
| Python forward and stop | Forward travel; final speed approximately 0.002 m/s | motion_test.json |
| One forward waypoint, rear-only | Final error 0.0653 m; final speed 0.000867 m/s | one_waypoint.json |
| Two forward waypoints, rear-only | Both reached; final error 0.0576 m; final speed 0.001923 m/s | multiple_waypoints.json |
| Four-wheel rotation and stop | Approximately 0.37 rad heading change; final speed approximately 0.00036 m/s | four_wheel_rotation.json |
| Two turning waypoints, four-wheel | Both reached in 11.6167 simulation seconds; heading change 0.5883 rad; final error 0.14896 m; final speed 0.0000675 m/s | turning_waypoints.json |
| Keyboard W/A, before final mode changes | Forward movement and measured turn, followed by released keys and pause | manual_test_before_restart.json |
| Post-restart manual handoff | Front damping/effort limits restored to zero; W displacement 0.2557 m; A yaw change 0.3770 rad; final speed 0.000475 m/s | manual_test.json |
| Post-restart autonomous startup | Four drives active; nearby waypoint reached and stopped | post_restart_waypoint.json |

## Findings and final changes

The owner confirmed all four wheels should be powered. The saved USD defines angular drives only on the rear joints; front joints have zero damping and zero actuator effort limits. Adding actual front DriveAPI schemas in the session layer and commanding all four joints resolved the poor turning seen with rear-only control. Runtime gain-only experiments did not activate the missing drives and were not retained. Rear drive parameters and robot geometry were preserved.

The original starting position also places a rear wheel beyond the physical floor boundary (wheel X approximately -32.55 m, floor minimum X -32.1 m). Testing used a live position 3 m farther inside the floor. Reopening the original file loses that session placement. Navigation checks a 1.5 m floor clearance and refuses an unsafe start or destination.

Autonomy disables the keyboard graph and zeros saved negative velocity targets. Manual restoration corrects its joint-name array and removes the added front-drive APIs to preserve the original rear-driven keyboard backup. No ROS2 LiDAR changes were made. The original graph uses the same SingleArticulation/ArticulationAction API as Python.

The post-restart graph-on/graph-off comparison completed successfully. With the graph active, sampled applied targets returned to zero and rear measured velocities were near zero despite Python commanding 0.5 rad/s. With the graph inactive, the 0.5 rad/s targets remained applied and measured rear velocities tracked them. This confirms competing controller writes. However, command-interval chassis travel was similar (0.1614 m active, 0.1570 m inactive), so the comparison does NOT establish that graph interference alone caused the historical report of no movement. It demonstrates why sampled wheel readings alone were misleading. Evidence: controller_conflict.json.

Manual handoff testing exposed another issue: removing front DriveAPI schemas alone left PhysX gains and effort limits active. The final handoff now zeros both session attributes and runtime actuator parameters. The repeated W/A test verified original passive-front settings and actual movement/stopping. The failed handoff is retained as manual_handoff_stale_gains.json.

The final implementation uses proportional steering, four named wheel commands, a physics-step loop, approach slowdown, waypoint dwell, measured final stopping, bounded run duration and progress watchdogs. Earlier unsuccessful rear-only steering experiments are retained separately and are not validation passes.

## Restart follow-up

Connection was reverified after the user enabled the extension. The controller-interference comparison and corrected manual handoff passed. A session-only preparation helper restores the inspected original starting pose safely without Play or saving the USD. The return from manual mode to four-wheel autonomy passed: all four drives reactivated, the nearby waypoint was reached in 3.7833 simulation seconds, and the robot stopped (manual_to_autonomous.json). Final handoff was measured: timeline paused, keyboard graph active, all targets zero, front DriveAPIs absent, and front damping/effort limits zero (final_handoff.json). navigation_request.json is set to status.

The final turning route finished and wrote its measurements before a later renderer crash. The crash backtrace points into GPU foundation/renderer plugins; its underlying cause has not been established.

## Preservation

Neither original USD was saved or overwritten during the recorded work. Original Python files are backed up in original_python/.

Recorded original SHA256 values:

- Warehouse_Robot_Autonomous_Navigation.usd: a468877c1465101654ca696491345d221f645f786b83e331e805ffb7ea6f4195
- IsaacBot.usd: 23b43ab3b7fe97257cd0f303681de5c0789882c293387e53cfeb016fd612db7d

## Final checks

Five controller/waypoint math tests passed. Updated Python files compile and VS Code task JSON parses. Both original USD SHA256 hashes were rechecked after the post-restart tests and match the values below/above. The verified turning-route plot is [verified_navigation.png](verified_navigation.png). Validation covers the recorded nearby routes; obstacle avoidance and arbitrary warehouse routes are outside this simple follower.
