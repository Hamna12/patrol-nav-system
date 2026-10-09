> Historical initial investigation. For completed results and current behavior, see [VALIDATION.md](VALIDATION.md) and the project [README](../README.md).

# Investigation — 2026-10-09

## Evidence

Read all four navigation files, both existing patrol utilities, the warehouse USD
and its composed `IsaacBot.usd` payload. `saved_scene.json` contains a read-only
programmatic inspection of the composed stage, not a live simulation measurement.

- Running Kit process uses `/media/hmna/New Volume/IsaacSim`, version
  `5.1.0-rc.19+release.26219.9c81211b.gl`. `/home/hmna/isaac-sim` has the same
  version marker but several relevant extension directories there are empty.
- Both installations include `python.sh` and `kit/python/bin/python3`.
  The active installation supports standalone SimulationApp and GUI extensions.
  Use the existing GUI process for this investigation to preserve its live state.
- The active installation includes NVIDIA `isaacsim.code_editor.vscode` 1.1.0.
  Its source implements the TCP Python execution server at localhost:8226.
  The newer separate `isaacsim.code_editor.python_server` is not the installed
  5.1 workflow. Do not assume its newer protocol applies here.
- Host process and GPU access were verified outside the sandbox. No server was
  listening at 8226; a connection attempt returned ConnectionRefusedError.
- Stage is Z-up, metersPerUnit=1. Articulation root is
  `/World/IsaacBot/IsaacBot`; chassis is its `Chassis` child.
- Four revolute joints exist. Only Rear_Left_Joint and Rear_Right_Joint have
  angular drives. Both have stiffness 0, damping 10000, unlimited force,
  target velocity -100 degrees/second. Front wheels are passive in this USD.
- All wheel axes are Y, with identity localRot0 on the chassis side. No evidence
  supports adding front drives or reversing one wheel's sign.
- DifferentialController radius=0.375 and distance=1.5. Its velocity output feeds
  ArticulationController, which executes on every OnPlaybackTick.
- NVIDIA's installed OgnIsaacArticulationController.py uses SingleArticulation,
  ArticulationAction, and apply_action, just like the existing Python script.
  The graph wrapper sets reset_xform_properties=False.
- Saved ArrayNames has arraySize=2, input0 unset, input1=Rear_Left_Joint. This is
  suspicious and must be compared to the live graph, since keyboard motion was
  reported working. Static evidence does not establish its runtime values.
- run_navigation.py sends rear-wheel targets every 0.1 wall-clock seconds while
  leaving graph ownership unchanged; its final zero command can also be
  overwritten. It does not measure chassis displacement or verify stopping.

## Current conclusion

Competing graph commands are a leading hypothesis, not a confirmed root cause.
The saved negative drive targets could explain motion when graph commands are
removed, but this has not been reproduced. No motion test has passed yet.
Waypoint implementation is deliberately deferred until forward/stop tests pass,
as requested. Existing navigation source and both USD files remain unchanged.

## Execute from VS Code

One-time GUI setup: Window → Extensions → search `isaacsim.code_editor.vscode`
→ enable **VS Code integration**. Its configured bind address is 127.0.0.1.

Then use Terminal → Run Task → **Isaac Sim: verify connection**, or:

```bash
python3 sim_client.py
python3 sim_client.py inspect_scene.py
```

The client sends a short file loader to NVIDIA's installed server. Code stays in
this project. A successful handshake must print ISAAC_CONNECTION_VERIFIED and
the live stage before claiming a connection. Do not run the old motion script
as a validation test until controller ownership has been addressed.

## Next live steps

1. Compare live graph names, drive targets, articulation and stage to saved data.
2. Record graph output, actual wheel speeds and chassis pose with no keys pressed.
3. Implement reversible controller ownership with zero targets at handoff and
   physics-step commands; preserve graph configuration and ROS2 LiDAR.
4. Measure forward displacement and sustained zero-command stopping; compare
   against graph-active behavior. Do not infer success from script execution.
5. Only after those pass, implement and validate rotation, one waypoint,
   multiple waypoints, final stopping, and manual restoration.

## Preservation fingerprints

SHA256 warehouse USD:
`a468877c1465101654ca696491345d221f645f786b83e331e805ffb7ea6f4195`

SHA256 IsaacBot.usd:
`23b43ab3b7fe97257cd0f303681de5c0789882c293387e53cfeb016fd612db7d`

Validation so far: both added Python files compile; the inspector successfully
loads the composed USD and writes the report. These are tooling checks only.
