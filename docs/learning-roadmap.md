# Learning roadmap

Work through these concepts with small experiments. Record what you observed before adding another subsystem.

| Concept | Plain explanation | Exercise |
| --- | --- | --- |
| Simulation scene and physics | The world, robot, collisions, and motion rules | Load a robot on a floor and check that it remains stable |
| Pose and coordinate frames | Where the robot is and which direction it faces, relative to a reference | Mark the world axes and record the robot's position and heading |
| Linear and angular velocity | Forward speed and turning speed | Drive straight, turn, and stop; explain the difference |
| Drive mechanism | How wheel motion produces robot motion | Identify wheel joints and whether the model uses differential, skid-steer, or another drive |
| Manual control / teleoperation | A person supplies movement commands | Drive a short route and demonstrate a stop |
| Feedback control | Correcting motion based on the difference between target and actual motion | Observe overshoot when approaching a stopping point |
| Sensors | Measurements that tell the robot about its surroundings | View available camera or range data with and without an obstacle |
| ROS 2 nodes and topics | Programs exchanging messages | Once the bridge works, identify the command and sensor message paths |
| Simulation time | The simulation's clock, which can pause or reset | Pause the scene and explain how timestamps should be interpreted |
| Odometry and localization | Estimating movement and position in a reference frame or map | Compare an estimate with simulator ground truth, clearly labelling both |
| Waypoints and maps | Target poses and a representation of the environment | Define checkpoint coordinates and the frame they use |
| Planning and control | Choosing a route and producing commands to follow it | Explain why a valid route still needs a motion controller |
| Obstacle response | Stopping, avoiding, or finding another path | Compare an open aisle with a blocked aisle |
| Mission states | Tracking what the robot is currently doing | Describe idle, travelling, inspecting, blocked, returning, and finished |

A checkpoint ID is only a label. The robot still needs a pose estimate and a known target location, or an explicitly implemented marker-based localization method.

## Immediate learning session

Explain pose, velocity, drive type, and teleoperation. Then load the scene and practise forward, turn, stop, and reset. Save a short experiment record. Do not wait to finish every topic before beginning manual practice.
