# Project scope

## Problem

Repeated facility inspections take time and can leave gaps in coverage. We want to explore whether a simulated mobile robot can follow a repeatable inspection route and report unusual conditions.

## Initial boundaries

- One robot in a small shared Isaac Sim warehouse or simplified training scene.
- Three or four checkpoints and one base position.
- Manual control before autonomous navigation.
- One staged blocked-route case first; a second case is optional.
- Local experiment records before external notifications or dashboards.

Start with a visible box or pallet blocking an aisle. A spill may require a different sensing method and is outside the initial blocked-route test.

## Intended patrol behaviour

Travel to a checkpoint, stop, inspect, record the result, and continue. On an anomaly, record an alert and select a response. Early work uses an operator-selected response. Autonomous response comes later.

Obstacle checks must also operate during travel in the autonomous phase, not only at checkpoints. A temporary obstacle may trigger a hold; a blocked route may require a new path. If no route is available, stop and report the failure. Returning to base also requires a traversable route.

## Alert record

Record run ID, checkpoint or pose, coordinate frame, event type, timestamp and clock source, observation, reporting method, and action taken. Example reporting methods: operator, simulator ground truth, sensor threshold, or perception model.

Simulated temperature values must be labelled as synthetic inputs unless a temperature simulation is explicitly implemented. Reading object positions directly from the simulator is ground-truth logic, not camera-based detection.

## Later scope

Automatic waypoint following, obstacle avoidance, replanning, return to base, scheduled rounds, and richer detection. Computer vision, ML, and deep learning are optional methods to evaluate after a working baseline.

## Decisions still open

Robot model and drive type; operating system; Isaac Sim version; ROS 2 version and bridge configuration; sensing method; route coordinates; stopping tolerance; checkpoint dwell time; obstacle clearance and timeout values.
