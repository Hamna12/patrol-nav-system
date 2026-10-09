# Actual project visuals for slides

1. **01_demo_start.png** — Actual Isaac Sim viewport capture after demo preparation. Use on the prototype setup/demo slide. Caption: “Robot at the staged start; green line shows the planned detour around the rack.” Preparation deliberately resets the robot; this is not autonomous recovery.
2. **02_demo_current_view.png** — Actual Isaac Sim viewport capture with navigation state complete. Use on the successful demonstration slide. Caption: “Robot at the end of the obstacle-aware demonstration.” The green goal is partly hidden by the robot. Visible orange sensor rays do not imply sensor-based avoidance.
3. **03_planned_vs_actual_route.png** — Plot of the recorded robot trajectory and planned route. Use on the path-planning slide. Caption: “A* route and measured trajectory, with robot-clearance constraints.” The direct route is blocked by required robot clearance, not necessarily by its centre line intersecting raw geometry.
4. **04_recorded_speed_and_arrival.png** — Plot of actual recorded commands, body speed, and distance to the final goal. Use on the control/validation slide. Horizontal axis is simulation time, not elapsed real time.
5. **05_validation_results.png** — Figure summarising recorded results and test count. Use on the results slide. This is a generated results figure, not a simulator screenshot.

The two scene images are real simulator captures at the current 640×360 viewport resolution. The other three images are plots/tables generated from project evidence, not fabricated screenshots. No AI-generated scene images are included.

Scope: static USD collision-map navigation. Moving-obstacle avoidance and SLAM are not implemented.
