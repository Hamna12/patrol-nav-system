# Patrol Navigation System

A learning and simulation project for an autonomous monitoring and anomaly-alert robot in NVIDIA Isaac Sim.

**Status: concept and foundational learning. Implementation and simulation results are not yet documented in this starter.**

Control & Navigation Team: Hamna, Ahmad, Tareq.  
Program: Helpforce AI R&D.

## Project idea

We plan to build a robot that patrols a simulated warehouse, stops at checkpoints, checks for unusual conditions, and records what happened, where, and when. Development starts with manual driving and progresses toward autonomous navigation.

Potential checks include blocked routes, readings outside a configured range, and moved or missing objects. These are planned features. The first prototype will use one or two simple cases.

## First milestone

Manually drive one robot through three or four checkpoints in a small Isaac Sim scene. Stop at each checkpoint and record one staged anomaly with its location and time. Clearly label whether the operator reported the anomaly or a software rule detected it.

The first milestone demonstrates manual control and the inspection workflow. Later milestones add automatic movement and detection.

## Learning and build sequence

| Stage | Focus | Evidence required |
| --- | --- | --- |
| Foundations | Coordinates, motion, sensors, ROS 2 concepts | Team notes explaining each concept using our robot |
| Phase 0A | Scene setup and manual control | Reproducible setup notes and a drive/stop recording |
| Phase 0B | Manual checkpoint patrol | Completed route and one clearly labelled anomaly record |
| Phase 1A | Automatic waypoint patrol | Robot visits checkpoints without steering input |
| Phase 1B | Rule-based checks and obstacle response | Clear-route and blocked-route trials with logs |
| Phase 2 | Richer perception and detection | Evaluated methods and recorded failure cases |

No milestone is marked complete until its evidence is linked.

## Start here

1. Read [the project scope](docs/project-scope.md).
2. Work through [the foundations](docs/learning-roadmap.md) while practising in simulation.
3. Complete [the environment checklist](docs/setup-checklist.md).
4. Follow [the milestone plan](docs/milestones.md).
5. Record each trial with [the experiment template](experiments/TEMPLATE.md).

## Repository contents

| Path | Purpose |
| --- | --- |
| `README.md` | Project purpose, current stage, and entry points |
| `docs/project-scope.md` | Prototype boundaries and intended behaviour |
| `docs/learning-roadmap.md` | Basic concepts and small exercises |
| `docs/setup-checklist.md` | Environment decisions and reproducibility |
| `docs/milestones.md` | Build tasks and completion criteria |
| `docs/resources.md` | Starting points for official documentation |
| `experiments/TEMPLATE.md` | Repeatable record of each simulation experiment |
| `CONTRIBUTING.md` | Team workflow and evidence requirements |

Add `simulation/`, `config/`, and `src/` when actual scenes, configuration, and code exist. Keep asset origins and instructions with simulation files. Link large recordings instead of committing them directly.

## Current next tasks

- [ ] Agree on the Isaac Sim environment and robot model.
- [ ] Explain the robot's drive mechanism and coordinate frames.
- [ ] Load a simple scene and confirm stable physics.
- [ ] Demonstrate forward motion, turning, and stopping.
- [ ] Mark three or four checkpoints and a base position.
- [ ] Complete and document a manual patrol.

## Planned tools

Isaac Sim is the simulation environment. ROS 2 and Nav2 are candidates for communication and later autonomous navigation. Confirm compatible versions before installation; this repository does not yet specify a tested software stack.

## Limitations

This project is a simulation prototype. No real-world safety, continuous monitoring, detection accuracy, or autonomous navigation performance has been demonstrated here.
