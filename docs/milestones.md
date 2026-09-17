# Milestones and initial issue backlog

All stages below are planned. Suggested repetition counts are team acceptance targets, not achieved results.

## Foundations: agree on the environment

Tasks: fill in the setup table, select the robot, explain pose and drive type, and identify relevant versioned documentation.

Done when: the team can describe how commands move the robot and how position is represented.

## Phase 0A: manual driving

Tasks: load the scene, drive forward, turn, stop, and reset.

Done when: another team member can reproduce the setup and the operator demonstrates controlled driving and stopping. Attach setup notes and a short recording.

## Phase 0B: manual inspection route

Tasks: define three or four checkpoint poses and base; select stopping tolerance and dwell time; stage one blocked aisle; record one alert.

Done when: three manual trials visit all reachable checkpoints and stop within the team's documented tolerance, with no observed collisions. The staged blockage produces a time-and-location record. Label human observations and manual intervention explicitly. If a checkpoint is unreachable, log that outcome rather than claiming full completion.

## Phase 1A: automatic waypoint patrol

Tasks: establish the pose source; choose a navigation approach; implement or configure sequential goals; handle goal success, cancellation, and timeout.

Done when: the robot completes the clear route without steering input in three documented trials. Record any interventions and failed runs.

## Phase 1B: rule-based checks and obstacle response

Tasks: add a sensor-based obstacle rule; define clearance, timeout, and repeat-alert policy; stop or hold on obstruction; add alternate-route handling when a valid path exists.

Done when: clear-route trials avoid false blocked-route alerts; blockage trials produce an alert and appropriate stop/hold; an alternate route is demonstrated separately; no-route cases stop and report failure. Ground-truth shortcuts are labelled.

## Phase 2: richer detection

Tasks: choose one detection problem; define normal and abnormal examples; compare a simple baseline with a proposed perception method.

Done when: results report both missed anomalies and false alerts on held-out scenarios. Add complexity only if it addresses a demonstrated limitation.

## First GitHub issues to create

1. Record the shared environment and select robot model.
2. Document pose, coordinate frames, and drive mechanism.
3. Demonstrate manual forward/turn/stop controls.
4. Define checkpoint positions and manual patrol procedure.
5. Stage one blocked aisle and record an inspection alert.
6. Publish the first experiment record and reproduction steps.

Use labels such as `learning`, `setup`, `simulation`, `documentation`, and `bug`. Assign owners with the team rather than assuming individual responsibilities.
