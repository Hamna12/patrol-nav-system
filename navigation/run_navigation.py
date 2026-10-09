"""Execute through sim_client.py. navigation_request.json selects the operation.
All USD edits are session-only. Imports do not start motion.
"""
import asyncio
import builtins
import json
import importlib
import types
import math
import time
from pathlib import Path
import numpy as np
import omni.kit.app
import omni.physx
import omni.timeline
import omni.usd
from pxr import Usd, UsdGeom, UsdPhysics
from isaacsim.core.prims import SingleArticulation
from isaacsim.core.utils.types import ArticulationAction
from navigation_controller import NavigationController
from robot_pose import RobotPose
from waypoint_manager import WaypointManager

SOURCE = Path(__file__).resolve().parent
PROJECT = SOURCE.parent
ROBOT_PATH = '/World/IsaacBot/IsaacBot'
GRAPH_PATH = ROBOT_PATH + '/Graphs/differential_controller'


class NavigationSession:
    def __init__(self):
        self.stage = omni.usd.get_context().get_stage()
        self.timeline = omni.timeline.get_timeline_interface()
        self.robot = None
        self.subscription = None
        self.task = None
        self.state = 'idle'
        self.rows = []
        self.elapsed = 0.0
        self.reason = None

    def setup_ownership(self, manual=False):
        if self.timeline.is_playing():
            raise RuntimeError('Pause before switching controller ownership')
        if self.stage != omni.usd.get_context().get_stage():
            raise RuntimeError('Stage changed')
        if UsdGeom.GetStageUpAxis(self.stage) != 'Z' or UsdGeom.GetStageMetersPerUnit(self.stage) != 1.:
            raise RuntimeError('Requires the inspected Z-up metre stage')
        floor = self.stage.GetPrimAtPath('/World/Structure/FloorCollider_2')
        if not floor:
            raise RuntimeError('Inspected floor collider is missing')
        bounds = UsdGeom.BBoxCache(Usd.TimeCode.Default(), ['default']).ComputeWorldBound(floor).ComputeAlignedRange()
        self.floor_min, self.floor_max = bounds.GetMin(), bounds.GetMax()
        with Usd.EditContext(self.stage, self.stage.GetSessionLayer()):
            for side in ('Left', 'Right'):
                p = self.stage.GetPrimAtPath(f'{ROBOT_PATH}/Rear_{side}_Wheel/Rear_{side}_Joint')
                p.GetAttribute('drive:angular:physics:targetVelocity').Set(0.)
                front = self.stage.GetPrimAtPath(f'{ROBOT_PATH}/Front_{side}_Wheel/Front_{side}_Joint')
                if manual:
                    # Restore original passive fronts for the two-wheel keyboard graph.
                    for name in ('stiffness', 'damping', 'maxForce', 'targetPosition', 'targetVelocity'):
                        attribute = front.GetAttribute('drive:angular:physics:' + name)
                        if attribute:
                            attribute.Set(0.)
                    front.RemoveAPI(UsdPhysics.DriveAPI, 'angular')
                else:
                    rear_drive = UsdPhysics.DriveAPI(p, 'angular')
                    drive = UsdPhysics.DriveAPI.Apply(front, 'angular')
                    drive.CreateTypeAttr().Set(rear_drive.GetTypeAttr().Get())
                    drive.CreateStiffnessAttr().Set(rear_drive.GetStiffnessAttr().Get())
                    drive.CreateDampingAttr().Set(rear_drive.GetDampingAttr().Get())
                    drive.CreateMaxForceAttr().Set(rear_drive.GetMaxForceAttr().Get())
                    drive.CreateTargetPositionAttr().Set(0.)
                    drive.CreateTargetVelocityAttr().Set(0.)
            graph = self.stage.GetPrimAtPath(GRAPH_PATH)
            if not graph:
                raise RuntimeError('Keyboard graph missing')
            graph.SetActive(manual)
            if manual:
                array = self.stage.GetPrimAtPath(GRAPH_PATH + '/ArrayNames')
                array.GetAttribute('inputs:input0').Set('Rear_Left_Joint')
                array.GetAttribute('inputs:input1').Set('Rear_Right_Joint')
        if manual and not self.timeline.is_stopped():
            # Removing a DriveAPI does not clear an already-built PhysX drive.
            # Zero both USD values above and live actuator parameters here.
            robot = SingleArticulation(ROBOT_PATH, reset_xform_properties=False)
            robot.initialize()
            if not robot.handles_initialized:
                raise RuntimeError('Cannot safely restore manual mode: invalid physics handles')
            indices = np.array([robot.get_dof_index(n) for n in ('Front_Right_Joint', 'Front_Left_Joint')])
            controller = robot.get_articulation_controller()
            kp, kd = controller.get_gains()
            limits = controller.get_max_efforts()
            kp[indices] = kd[indices] = limits[indices] = 0.
            robot.apply_action(ArticulationAction(joint_velocities=np.zeros(robot.num_dof)))
            controller.set_gains(kps=kp, kds=kd, save_to_usd=False)
            controller.set_max_efforts(limits)

    def command(self, wheels):
        if self.robot is not None:
            if len(wheels) == 2:
                wheels = (wheels[0], wheels[1], wheels[1], wheels[0])
            self.robot.apply_action(ArticulationAction(
                joint_velocities=np.asarray(wheels, dtype=float), joint_indices=self.indices))

    def stop(self, reason='operator stop'):
        try:
            self.command((0., 0.))
        finally:
            self.timeline.pause()
            self.subscription = None
            self.reason = reason
            self.state = 'paused'

    def save(self):
        (PROJECT / 'diagnostics' / 'navigation_latest.json').write_text(json.dumps({
            'state': self.state, 'reason': self.reason, 'elapsed': self.elapsed,
            'dof_names': self.robot.dof_names if self.robot else [],
            'waypoints': self.manager.waypoints, 'reached': self.manager.current_index,
            'rows': self.rows}, indent=2))

    async def run(self, request):
        # Ownership changes require paused physics, even when the user has
        # already pressed Play in the GUI.
        if self.timeline.is_playing():
            self.timeline.pause()
            await omni.kit.app.get_app().next_update_async()
        self.manager = WaypointManager()
        self.controller = NavigationController()
        self.controller.position_tolerance = 0.25 if request['operation'] == 'demo' else 0.15
        drive_distance = float(request.get('distance', 3.0))
        if request['operation'] == 'drive' and (not math.isfinite(drive_distance) or not 0.3 <= drive_distance <= 10.):
            raise ValueError('Drive distance must be between 0.3 and 10 metres')
        self.manager.set_waypoints(request.get('waypoints', []))
        self.setup_ownership()
        self.elapsed = 0.
        self.rows = []
        self.state = 'starting'
        self.reason = None
        self.stop_started = None
        self.best_distance = math.inf
        self.best_heading = math.inf
        self.progress_time = 0.
        self.dwell_until = 0.
        self.operation = request['operation']
        self.rotation_rate = float(request.get('rotation_rate', 0.6))
        if not math.isfinite(self.rotation_rate) or not 0 < self.rotation_rate <= 1.5:
            raise ValueError('Rotation test rate must be in (0, 1.5] rad/s')
        self.max_time = 60.
        try:
            self.timeline.play()
            await omni.kit.app.get_app().next_update_async()
            self.robot = SingleArticulation(ROBOT_PATH, name='warehouse_navigation_robot', reset_xform_properties=False)
            self.robot.initialize()
            self.indices = np.array([self.robot.get_dof_index(n) for n in ('Rear_Left_Joint', 'Rear_Right_Joint', 'Front_Right_Joint', 'Front_Left_Joint')], dtype=np.int32)
            gains = self.robot.get_articulation_controller().get_gains()
            limits = self.robot.get_articulation_controller().get_max_efforts()
            print('Autonomous damping:', gains[1], 'effort limits:', limits)
            if any(gains[1][i] <= 0 or limits[i] <= 0 for i in self.indices):
                raise RuntimeError('Front drives did not activate; physics articulation must be rebuilt')
            self.pose = RobotPose()
            x, y, yaw = self.pose.get_pose()
            if not self.on_floor(x,y):
                raise RuntimeError('Robot is too close to the floor edge; reposition fully onto the floor before navigation')
            self.start_yaw = yaw
            self.obstacle_guard = None
            if self.operation == 'demo':
                planner_module = types.ModuleType('obstacle_planner')
                path = SOURCE / 'obstacle_planner.py'
                exec(compile(path.read_text(), str(path), 'exec'), planner_module.__dict__)
                data = planner_module.scene_map(self.stage)
                planner = planner_module.WarehousePlanner(data)
                goal = request.get('goal', [-21., -32.])
                route = planner.plan((x,y), goal)
                self.manager.set_waypoints(route)
                self.obstacle_guard = planner_module.WarehousePlanner(data, clearance=1.45)
                (PROJECT / 'diagnostics' / 'demo_route.json').write_text(json.dumps({'start':[x,y], 'goal':goal, 'route':route, 'clearance':1.7}, indent=2))
                print('Static-map obstacle-aware route:', route)
            elif self.operation in ('nearby', 'multiple', 'drive'):
                distances = [drive_distance] if self.operation == 'drive' else ([0.3] if self.operation == 'nearby' else [0.25, 0.5])
                self.manager.set_waypoints([(x+d*math.cos(yaw), y+d*math.sin(yaw)) for d in distances])
            elif self.operation not in ('rotate','arc') and self.manager.completed():
                raise ValueError('Provide at least one waypoint')
            if any(not self.on_floor(*point) for point in self.manager.waypoints):
                raise ValueError('Waypoint is outside the floor with a 1.5 m robot clearance')
            self.command((0., 0.))
            self.state = 'running'
            self.subscription = omni.physx.get_physx_interface().subscribe_physics_step_events(self.step)
            deadline = time.monotonic() + 600.
            while self.state in ('running', 'stopping'):
                await omni.kit.app.get_app().next_update_async()
                if time.monotonic() > deadline:
                    self.stop('wall-clock timeout')
                elif not self.timeline.is_playing() and self.state in ('running', 'stopping'):
                    self.stop('timeline interrupted')
                elif omni.usd.get_context().get_stage() != self.stage:
                    self.stop('stage changed')
        except BaseException as exc:
            self.stop(repr(exc))
            raise
        finally:
            self.subscription = None
            self.save()

    def on_floor(self, x, y):
        return all(self.floor_min[i]+1.5 < v < self.floor_max[i]-1.5 for i,v in enumerate((x,y)))

    def step(self, dt):
        try:
            self.elapsed += dt
            x, y, yaw = self.pose.get_pose()
            if self.obstacle_guard is not None and not self.obstacle_guard.free((x,y)):
                self.stop('obstacle clearance violated')
                self.state = 'failed'
                return
            if not self.on_floor(x,y):
                self.stop('floor boundary reached')
                self.state = 'failed'
                return
            target = self.manager.get_current_waypoint()
            distance = self.manager.distance_to_waypoint(x, y)
            error = None
            linear = angular = 0.
            if self.state == 'running':
                if self.elapsed >= self.max_time:
                    self.reason = 'simulation timeout'
                    self.state = 'stopping'
                elif self.elapsed < self.dwell_until:
                    pass
                elif self.operation in ('rotate','arc'):
                    if 1. <= self.elapsed < 3.:
                        angular = self.rotation_rate
                        if self.operation == 'arc':
                            linear = 0.25
                    elif self.elapsed >= 3.:
                        self.reason = 'rotation command complete'
                        self.state = 'stopping'
                elif target is None:
                    self.reason = 'all waypoints reached'
                    self.state = 'stopping'
                else:
                    linear, angular, reached = self.controller.compute_command(x,y,yaw,*target)
                    error = self.controller.normalize_angle(math.atan2(target[1]-y,target[0]-x)-yaw)
                    if reached:
                        self.manager.advance()
                        self.controller.turning = True
                        self.dwell_until = self.elapsed + 0.7
                        self.best_distance = math.inf
                        self.best_heading = math.inf
                        self.progress_time = self.elapsed
                    elif self.controller.turning and abs(error) < self.best_heading-0.02:
                        self.best_heading = abs(error)
                        self.progress_time = self.elapsed
                    elif not self.controller.turning and distance < self.best_distance-0.01:
                        self.best_distance = distance
                        self.best_heading = math.inf
                        self.progress_time = self.elapsed
                    elif self.elapsed-self.progress_time > 5.:
                        self.reason = 'no distance or heading progress for 5 simulation seconds'
                        self.state = 'stopping'
            if self.state == 'stopping':
                linear = angular = 0.
                if self.stop_started is None:
                    self.stop_started = self.elapsed
            linear, angular = self.controller.smooth_command(linear, angular, dt)
            wheels = self.controller.wheel_velocities(linear, angular)
            self.command(wheels)
            velocity = self.robot.get_linear_velocity()
            self.rows.append({'t':self.elapsed,'pose':[x,y,yaw],'target':target,
                'distance':distance,'heading_error':error,'linear_command':linear,
                'angular_command':angular,'wheels':wheels,
                'actual_wheels':self.robot.get_joint_velocities().tolist(),
                'body_velocity':velocity.tolist()})
            if self.state == 'stopping' and self.elapsed-self.stop_started >= 1.5:
                reason = self.reason
                speed = float(np.linalg.norm(velocity[:2]))
                spin = float(abs(self.robot.get_angular_velocity()[2]))
                self.stop(reason)
                self.state = 'complete' if speed < 0.02 and spin < 0.03 and reason in ('all waypoints reached','rotation command complete') else 'failed'
                if self.operation in ('rotate','arc') and abs(self.controller.normalize_angle(yaw-self.start_yaw)) < 0.05:
                    self.state = 'failed'
                    self.reason = 'insufficient measured rotation'
        except Exception as exc:
            self.stop(repr(exc))
            self.state = 'failed'


def main():
    global NavigationController, RobotPose, WaypointManager
    request_path = PROJECT / 'config' / 'navigation_request.json'
    request = json.loads(request_path.read_text()) if request_path.exists() else {'operation':'status'}
    operation = request.get('operation', 'status')
    previous = getattr(builtins, '_warehouse_navigation', None)
    if operation == 'status':
        print('Navigation:', previous.state if previous else 'not started')
        if previous:
            print('simulation seconds:', previous.elapsed, 'reason:', previous.reason)
        return
    if operation == 'stop':
        if previous:
            previous.stop()
        return
    if previous and previous.task and not previous.task.done():
        raise RuntimeError('Navigation already running; stop it first')
    for name in ('_warehouse_test_task', '_warehouse_manual_task', '_warehouse_conflict_task', '_warehouse_fourwheel_task'):
        task = getattr(builtins, name, None)
        if task and not task.done():
            raise RuntimeError('A diagnostic test is running; wait for it to finish')
    def fresh_module(name):
        # Kit's custom importer can retain old code across importlib.reload.
        # Compile the actual project source so VS Code edits take effect.
        module = importlib.import_module(name)
        path = SOURCE / (name + '.py')
        exec(compile(path.read_text(), str(path), 'exec'), module.__dict__)
        return module
    NavigationController = fresh_module('navigation_controller').NavigationController
    RobotPose = fresh_module('robot_pose').RobotPose
    WaypointManager = fresh_module('waypoint_manager').WaypointManager
    session = NavigationSession()
    builtins._warehouse_navigation = session
    if operation == 'manual':
        session.setup_ownership(manual=True)
        session.state = 'manual'
        print('Manual graph enabled with corrected rear joint names. Simulation remains paused.')
    elif operation in ('nearby','multiple','drive','demo','rotate','arc','waypoints'):
        session.task = asyncio.ensure_future(session.run(request))
        def finished(task):
            if task.cancelled():
                session.state, session.reason = 'failed', 'cancelled'
            elif task.exception() is not None:
                session.state, session.reason = 'failed', repr(task.exception())
            print('Navigation result:', session.state, session.reason)
        session.task.add_done_callback(finished)
        print('Scheduled bounded', operation, 'run; simulation pauses automatically for setup.')
    else:
        raise ValueError('Unknown operation')


if __name__ == '__main__':
    main()
