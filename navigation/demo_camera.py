"""Frame the demonstration area using the existing perspective viewport."""
import numpy as np
import omni.usd
from pxr import Usd
from isaacsim.core.utils.viewports import set_camera_view
stage=omni.usd.get_context().get_stage()
with Usd.EditContext(stage,stage.GetSessionLayer()):
    set_camera_view(eye=np.array([-27.,-34.5,8.]),target=np.array([-24.5,-30.,0.5]))
print('Demo camera framed')
