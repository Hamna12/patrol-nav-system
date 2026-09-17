# Environment and setup checklist

Status: unverified. This is a preparation checklist, not a tested installation guide.

## Record the environment

| Item | Team value |
| --- | --- |
| Operating system and version | TBD |
| GPU, VRAM, and driver | TBD |
| Isaac Sim version and installation method | TBD |
| Robot asset, source, and drive type | TBD |
| Scene asset and source | TBD |
| ROS 2 distribution, if used | TBD |
| Bridge configuration, if used | TBD |
| Python environment used for scripts | TBD |
| Documentation version used | TBD |

The pitch mentions ROS 2 Jazzy. Treat this as a candidate until compatibility with the team's OS and Isaac Sim release has been checked in the matching official documentation. Do not mix commands from different release guides.

## Setup sequence

- [ ] Check the selected release's system requirements.
- [ ] Launch Isaac Sim and record any errors.
- [ ] Open a small scene with a floor and robot.
- [ ] Confirm collisions, wheel joints, drive behaviour, and initial pose.
- [ ] Choose native manual control or ROS 2 teleoperation and document the choice.
- [ ] If using ROS 2, configure the bridge and verify command flow and simulation time.
- [ ] Demonstrate forward motion, turning, and stopping at low speed.
- [ ] Check behaviour when commands stop arriving; do not assume automatic stopping.
- [ ] Record exact launch steps and reset procedure after they work.
- [ ] Ask another team member to reproduce the setup.

For later ROS 2 navigation, also document frame relationships, odometry, sensors, map source, and navigation configuration. A working bridge alone does not establish a working navigation system.
