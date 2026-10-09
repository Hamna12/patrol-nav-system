# Project folder guide

| Folder | Purpose |
|---|---|
| `navigation/` | Active robot controller, planner, demo preparation, and manual/stop/status scripts. Runs inside Isaac Sim. |
| `config/` | Editable navigation request. |
| `tools/` | Simulator connection client, read-only inspection, screenshot capture, and plotting scripts. |
| `tests/` | Controller and planner unit tests; these run with normal Python. |
| `docs/` | Demo instructions and this folder guide. |
| `diagnostics/` | Raw recorded telemetry, validation notes, and generated route charts. Old failed experiments are also retained as evidence. |
| `presentation_snapshots/` | Slide images and captions. |
| `.vscode/` | VS Code task definitions. |
| `archive/` | Historical scripts and duplicate exports; excluded from Git by default. |

## Main files

- `navigation/run_navigation.py`: executes requests and records results.
- `navigation/navigation_controller.py`: forward/turning commands and smoothing.
- `navigation/obstacle_planner.py`: static-map A* planning.
- `navigation/robot_pose.py`: robot pose readings.
- `navigation/waypoint_manager.py`: target sequence and completion.
- `navigation/prepare_demo.py`: repeatable demo reset and green path display.
- `config/navigation_request.json`: selects the operation and goal.

## Commands from the project root

```bash
# Run tests without Isaac Sim
python3 -m unittest discover -s tests -v

# Execute in the already-running simulator
python3 tools/sim_client.py navigation/prepare_demo.py
python3 tools/sim_client.py navigation/run_navigation.py
python3 tools/sim_client.py navigation/navigation_status.py
python3 tools/sim_client.py navigation/stop_navigation.py

# Regenerate graphs from saved validated evidence (requires Matplotlib)
python3 tools/plot_demo.py
python3 tools/build_figures.py
```

The VS Code task names are unchanged; their file paths have been updated.
Open the project root in VS Code, not an individual subfolder. If an old editor
tab points to a file at the root, close it and open its new location.

`navigation/` scripts require Isaac Sim's Python APIs: send them through the
client, rather than running them directly with the system Python interpreter.
The scene USD assets remain external and have not been moved.
