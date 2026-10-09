# Completed follow-up — 2026-10-09

The restart follow-up below is now complete. See VALIDATION.md and final_handoff.json. Connection verified, graph comparison completed, stale PhysX front gains fixed during manual restoration, keyboard W/A retested, and return to four-wheel autonomy passed. Simulator left paused in manual mode with zero wheel targets. Both original USD hashes unchanged. navigation_request.json is status. The remainder of this file is the historical restart checkpoint, not pending work.

# Resume checkpoint — 2026-10-09

User paused work to restart the system. Do not start simulation work until they return.

## Verified results
- Connected to live Isaac Sim 5.1 using NVIDIA isaacsim.code_editor.vscode on localhost:8226 and sim_client.py.
- Actual installation: /media/hmna/New Volume/IsaacSim. /home/hmna/isaac-sim contains incomplete extension directories.
- Original warehouse and IsaacBot USD files were not saved or overwritten. Original Python sources backed up in diagnostics/original_python.
- Saved robot starts partly outside floor: floor minimum X=-32.1 m, rear-right wheel approximately X=-32.55 m. Live robot was shifted +3 m inward for testing. Reopening original USD loses this session relocation.
- USD has rear drives only; front damping and maximum effort are zero. User explicitly confirmed ALL FOUR WHEELS SHOULD BE POWERED.
- Autonomous runner now adds real front angular DriveAPI schemas in SESSION layer, matching rear parameters, and commands RL, RR, FR, FL. Runtime gains alone did not activate missing drives. Earlier temporary gains/effort experiments were restored.
- Keyboard graph is disabled during autonomy. Manual restoration removes front DriveAPIs to restore original passive-front backup behavior and corrects session joint-name array to rear-left/rear-right (saved first entry was unset).
- Rear-only forward and stop passed. Single forward waypoint: 6.53 cm final error, final speed 0.000867 m/s. Two forward waypoints: 5.76 cm, 0.001923 m/s.
- Keyboard graph W/A test passed before final front-drive changes; manual_test.json contains real pose and graph-output evidence.
- FOUR-POWERED-WHEEL rotation passed: approximately 0.37 rad yaw change, final horizontal speed approximately 0.00036 m/s. See four_wheel_rotation.json.
- FINAL four-wheel proportional controller completed TWO TURNING WAYPOINTS: 11.6167 simulation seconds; heading change 0.5883 rad; final error 0.148964 m (15 cm tolerance); final speed 0.0000675 m/s; max speed in last half-second 0.000176 m/s. Preserved in turning_waypoints.json and validation_summary.json.
- Five current local math tests passed. Re-run only after relevant changes.

## Interruption / crash
The turning route completed and wrote telemetry BEFORE Isaac Sim crashed. Host process disappeared and port 8226 refused connections. Crash log:
/home/hmna/.nvidia-omniverse/logs/Kit/Isaac-Sim Full/5.1/kit_20261009_062032.log
Backtrace at 09:49:08Z points into GPU foundation / renderer plugins; exact underlying cause not established.
Restart was launched (unified exec session 93160) just before user requested system restart. It may still be running until reboot. Do not launch another process without checking.
Launcher has an unquoted dirname bug with absolute paths containing spaces. Working launch:
  working directory: /media/hmna/New Volume/IsaacSim
  bash ./isaac-sim.sh --enable isaacsim.code_editor.vscode --/app/window/width=1280 --/app/window/height=720
Output: diagnostics/restart.log.

## Remaining work when user returns
1. Check existing Kit process and verify server with python3 sim_client.py. Do not assume connection survives reboot. Enable extension if needed or launch once with --enable.
2. Reopen original warehouse if needed, without saving over it. Scene should remain paused. Reapply safe session-only starting pose (+3 m X from original was inspected as clear) and zero drive targets BEFORE Play. A recovery/preparation helper was contemplated but NOT created.
3. Re-verify manual restoration after adding/removing actual front DriveAPI schemas: front gains/effort should return to zero; existing graph works; leave paused. manual_mode.py now loads current run_navigation.py via runpy to avoid stale import cache.
4. Finish graph-on/graph-off causal comparison in conflict_test.py. First attempt failed due timeline.pause being asynchronous, so no successful A/B result may be claimed. Script was fixed to await an app update after pause; it has NOT been rerun successfully. Uses rear-only original plant for both phases, toggles graph, logs pose/actual/applied commands, restores manual. Check its current source before execution and avoid overlapping tests.
5. Optionally repeat final four-wheel route after fresh restart if needed to validate startup/mode transitions; final route already physically passed, do not call it unverified.
6. Finish diagnostics/VALIDATION.md (README references it but it has NOT been created). Explain scene mismatch, verified tests, failed experiments, controller ownership hypothesis vs A/B proof, crash limitation, original file preservation.
7. Reset navigation_request.json to {"operation":"status"} for safe handoff (currently contains the successful turning-route coordinates). Provide concise user instructions and final result.

## Current implementation
- robot_pose.py: preserves transforms, reads chassis pose, quaternion WXYZ to yaw.
- waypoint_manager.py: finite XY validation, sequence tracking.
- navigation_controller.py: simple proportional controller again (rear-only turn-then-drive experiments were discarded). v max .25 m/s, omega max .6 rad/s; heading gain1.5; radius .375, track1.5; four wheel outputs RL/RR/FR/FL; tolerance .15.
- run_navigation.py: explicit requests, no import motion; exclusive graph ownership; front drive session setup; physics callbacks; 60-s simulation and 600-s wall timeout; 5-s distance/heading progress watchdog; .7-s waypoint dwell, 1.5-s stop measurement; completion requires body speed<.02 m/s and yaw rate<.03 rad/s; floor boundary guard1.5m. Resolves all indices by name.
- Kit retained stale code with importlib.reload; main explicitly compiles project module source at each start. Keep this behavior.
- sim_client.py and .vscode/tasks.json give file execution, status, stop, manual restore. stop_navigation.py also cancels diagnostic tasks.
- README.md describes current four-wheel design and limits. diagnostics/README.md is the initial historical investigation and is outdated as a final report.
- Many diagnostic scripts and failed logs are retained; do not treat failed rear-only steering experiments as passes.

## Original file SHA256
Warehouse_Robot_Autonomous_Navigation.usd:
a468877c1465101654ca696491345d221f645f786b83e331e805ffb7ea6f4195
IsaacBot.usd:
23b43ab3b7fe97257cd0f303681de5c0789882c293387e53cfeb016fd612db7d
