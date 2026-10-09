"""Run in Isaac Sim 5.1's Script Editor with the existing warehouse open.

Reads live USD transforms (normal GUI physics-to-USD updates must be enabled).
One automatic arrival is recorded per execution, including after pause/resume.
"""

from datetime import datetime
from pathlib import Path
import math

import omni.kit.app
import omni.timeline
import omni.ui as ui
import omni.usd
from pxr import Usd, UsdGeom


class CheckpointMonitor:
    ROBOT = "/IsaacBot"
    CHASSIS = "/IsaacBot/Chassis"
    CHECKPOINT = "/Checkpoint_A"
    RADIUS_METRES = 0.5

    def __init__(self):
        self._subscription = None
        self._arrived = False
        self._log_error = None
        self._context = omni.usd.get_context()
        self._stage = self._context.get_stage()
        self._timeline = omni.timeline.get_timeline_interface()
        self._log_file = (
            Path.home() / "Documents" / "warehouse_patrol" / "patrol_log.txt"
        )
        self._window = ui.Window("Checkpoint A Monitor", width=440, height=220)
        with self._window.frame:
            with ui.VStack(spacing=8):
                ui.Label("CHECKPOINT A", height=25)
                self._distance_label = ui.Label("Horizontal distance: --", height=25)
                ui.Label("Arrival radius: 0.50 m from chassis origin", height=25)
                self._status_label = ui.Label("Checking scene...", word_wrap=True)
                ui.Button("Stop Monitor", height=30, clicked_fn=self.stop)

        self._update(None)
        self._subscription = (
            omni.kit.app.get_app().get_update_event_stream()
            .create_subscription_to_pop(self._update, name="Checkpoint A monitor")
        )

    def _update(self, _event):
        stage = self._context.get_stage()
        if stage is None or stage != self._stage:
            self._distance_label.text = "Horizontal distance: --"
            self._status_label.text = "Stage closed or changed. Rerun this file in the intended scene."
            return

        missing = [
            path for path in (self.ROBOT, self.CHASSIS, self.CHECKPOINT)
            if not stage.GetPrimAtPath(path).IsValid()
            or not stage.GetPrimAtPath(path).IsActive()
        ]
        if missing:
            self._distance_label.text = "Horizontal distance: --"
            self._status_label.text = "Missing/inactive scene objects: " + ", ".join(missing)
            return

        try:
            for path in (self.CHASSIS, self.CHECKPOINT):
                if not UsdGeom.Xformable(stage.GetPrimAtPath(path)):
                    raise ValueError(f"Object has no transform: {path}")
            # A fresh cache avoids stale transforms as the robot moves.
            time_code = Usd.TimeCode(
                self._timeline.get_current_time() * stage.GetTimeCodesPerSecond()
            )
            cache = UsdGeom.XformCache(time_code)
            chassis = cache.GetLocalToWorldTransform(
                stage.GetPrimAtPath(self.CHASSIS)
            ).ExtractTranslation()
            checkpoint = cache.GetLocalToWorldTransform(
                stage.GetPrimAtPath(self.CHECKPOINT)
            ).ExtractTranslation()
            # Isaac scenes normally use Z-up; also support Y-up stages.
            axes = (0, 1) if UsdGeom.GetStageUpAxis(stage) == UsdGeom.Tokens.z else (0, 2)
            distance = math.hypot(*(chassis[i] - checkpoint[i] for i in axes))
            distance *= UsdGeom.GetStageMetersPerUnit(stage)
            if not math.isfinite(distance):
                raise ValueError("Scene contains a non-finite position")
        except Exception as error:
            self._distance_label.text = "Horizontal distance: --"
            self._status_label.text = f"Cannot read distance: {error}"
            return

        self._distance_label.text = f"Horizontal distance: {distance:.3f} m"
        if self._arrived:
            self._status_label.text = "Arrival at A logged. Rerun this file for a new patrol."
        elif self._log_error:
            self._status_label.text = self._log_error
        elif not self._timeline.is_playing():
            self._status_label.text = "Press Play to enable automatic arrival logging."
        elif distance <= self.RADIUS_METRES:
            entry = (
                f"{datetime.now():%Y-%m-%d %H:%M:%S} | "
                f"Automatic arrival at A (horizontal distance: {distance:.3f} m)"
            )
            try:
                self._log_file.parent.mkdir(parents=True, exist_ok=True)
                with self._log_file.open("a", encoding="utf-8") as file:
                    file.write(entry + "\n")
            except OSError as error:
                # Avoid repeating failed writes every frame; rerun after fixing.
                self._log_error = f"Could not save log: {error}. Fix and rerun this file."
                self._status_label.text = self._log_error
                return
            self._arrived = True
            self._status_label.text = "Arrival at A logged. Rerun this file for a new patrol."
            print(entry)
        else:
            self._status_label.text = "Monitoring. Drive to A using your existing W / A / S / D controls."

    def stop(self):
        if self._subscription is not None:
            self._subscription.unsubscribe()
            self._subscription = None
        self._status_label.text = "Monitor stopped. Rerun this file to start again."

    def close(self):
        self.stop()
        self._window.destroy()


# Keep this script's names separate from manual_patrol.py's UI and callbacks.
# Re-execution replaces the previous subscription, avoiding duplicate logging.
if "checkpoint_monitor" in globals():
    checkpoint_monitor.close()
checkpoint_monitor = CheckpointMonitor()
