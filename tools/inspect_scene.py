"""Read-only USD inspection; run locally with USD or inside the live simulator."""
import json
from pxr import Usd, UsdGeom

SCENE = "/home/hmna/Downloads/Warehouse_Robot_Autonomous_Navigation.usd"


def inspect(stage):
    if stage is None:
        raise RuntimeError("No stage is open")
    result = {
        "root_layer": stage.GetRootLayer().identifier,
        "meters_per_unit": UsdGeom.GetStageMetersPerUnit(stage),
        "up_axis": str(UsdGeom.GetStageUpAxis(stage)),
        "layers": [layer.identifier for layer in stage.GetUsedLayers()],
        "prims": [],
    }
    for prim in stage.Traverse():
        path = str(prim.GetPath())
        schemas = list(prim.GetAppliedSchemas())
        if ("PhysicsArticulationRootAPI" in schemas
                or "Joint" in prim.GetTypeName()
                or "/Graphs/differential_controller" in path):
            result["prims"].append({
                "path": path, "type": prim.GetTypeName(),
                "active": prim.IsActive(), "schemas": schemas,
                "attributes": {
                    a.GetName(): {"value": str(a.Get()),
                                  "connections": [str(p) for p in a.GetConnections()]}
                    for a in prim.GetAttributes()
                    if not a.GetName().startswith("ui:")
                },
                "relationships": {r.GetName(): [str(p) for p in r.GetTargets()]
                                  for r in prim.GetRelationships()},
            })
    return result


if __name__ == "__main__":
    try:
        import omni.usd
    except ImportError:
        stage = Usd.Stage.Open(SCENE)
    else:
        stage = omni.usd.get_context().get_stage()
    print(json.dumps(inspect(stage), indent=2))
