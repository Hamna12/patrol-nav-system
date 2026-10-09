# Warehouse navigation prototype — presentation guide

This prototype plans against **known static collision geometry in the USD scene**.
It is not LiDAR-based SLAM or dynamic obstacle avoidance.

## Repeat the demonstration

1. Keep the warehouse open, with VS Code integration enabled.
2. In VS Code: Terminal → Run Task → **Isaac Sim: stop and pause**.
3. Run **Isaac Sim: prepare obstacle demo**. Wait for **DEMO READY**.
   This deliberately stages the robot at (-28, -28), draws a green planned path,
   and selects a goal at (-21, -32). It does not drive or save the original USD.
4. The preparation task frames the demo area automatically. You should see the
   robot, the rack end, and the green route. You can select **World → IsaacBot**
   and press **F** over the viewport if you want a closer view.
5. In VS Code, run **Isaac Sim: run navigation request**.
   Do not press Play separately. The robot turns, follows a detour around the rack,
   and stops near the green goal. Low FPS makes the demonstration take longer
   than its simulation duration.
6. To stop early, run **Isaac Sim: stop and pause**.
   To repeat from the beginning, return to step 3.
7. Run **Isaac Sim: navigation status** to see progress or the final result.

## What to say

“I built a four-wheel warehouse navigation prototype in Isaac Sim 5.1.
It reads static collision geometry from the scene, expands obstacle bounds to
allow for the robot's size, plans a path with A*, and follows the path with
bounded acceleration and braking. It detects lack of progress and stops.
The green line shows the planned detour. Scene changes are session-only.”

## Limits to disclose

- Preparation teleports the robot to a checked starting position; it is a demo
  reset, not autonomous recovery from a collision.
- The map is rebuilt at the start of a demo run; it does not detect moving or
  newly introduced obstacles during the run.
- Planning uses conservative 2-D obstacle bounds with 1.7 m center clearance.
  Runtime checks use 1.45 m center clearance against the same static map.
- Only the tested demonstration route is validated in simulation. Narrow aisles
  may be rejected. This is not a general production navigation system.
- `drive` and `nearby` remain straight-line diagnostic modes without planning.
  Use `demo` for the obstacle-aware presentation.
- The robot slows at route corners, aligns before driving, and stops within a
  25 cm goal zone. Small steering corrections and wheel slip can still occur.

The latest physical result is in `../diagnostics/navigation_latest.json`.
