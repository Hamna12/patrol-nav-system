from pathlib import Path
from datetime import datetime
import omni.ui as ui

# Save observations beside your Python file.
log_file = (
    Path.home() / "Documents" / "warehouse_patrol" / "patrol_log.txt"
)
log_file.parent.mkdir(parents=True, exist_ok=True)

# Close the previous panel if you run this script again.
if "patrol_window" in globals():
    patrol_window.destroy()


def record_event(message):
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{time_now} | {message}"

    try:
        with log_file.open("a", encoding="utf-8") as file:
            file.write(entry + "\n")
    except OSError as error:
        status_label.text = f"Could not save log: {error}"
        return

    status_label.text = message
    print(entry)


patrol_window = ui.Window(
    "Warehouse Manual Patrol",
    width=370,
    height=350,
)

with patrol_window.frame:
    with ui.VStack(spacing=10):
        ui.Label("MANUAL PATROL", height=30)
        ui.Label("Drive using your existing W / A / S / D controls.",
                 height=25)
        ui.Label("Buttons record operator reports.", height=25)

        status_label = ui.Label("Ready to start", height=35)

        ui.Button(
            "Start Patrol Log",
            height=30,
            clicked_fn=lambda: record_event("Manual patrol started"),
        )

        with ui.HStack(spacing=5, height=30):
            ui.Button(
                "Reached A",
                clicked_fn=lambda: record_event(
                    "Operator confirmed arrival at A"
                ),
            )
            ui.Button(
                "Reached B",
                clicked_fn=lambda: record_event(
                    "Operator confirmed arrival at B"
                ),
            )
            ui.Button(
                "Reached C",
                clicked_fn=lambda: record_event(
                    "Operator confirmed arrival at C"
                ),
            )

        ui.Button(
            "Report Obstacle",
            height=30,
            clicked_fn=lambda: record_event(
                "Obstacle reported by operator"
            ),
        )

        ui.Button(
            "Finish Patrol Log",
            height=30,
            clicked_fn=lambda: record_event("Manual patrol finished"),
        )

        ui.Label("Log: Documents/warehouse_patrol/patrol_log.txt",
                 height=25)

print("Manual Patrol panel opened.")