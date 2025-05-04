
## 

The following file is based off `IsaacLab\scripts\environments\teleoperation\teleop_se3_agent.py`
With unused modularity trimmed and condensed
Please refer to docs for more information 

# To run 

``` bash
python .\object_override.py --task Isaac-Lift-Cube-Franka-IK-Rel-v0
```
or 

``` bash
python .\object_override.py --task Isaac-Lift-Cube-Franka-IK-Rel-v0 --teleop_device spacemouse 
```


### Changes added 

``` py

from scipy.spatial.transform import Rotation as R 
import os 

# Changes from Euler (360') Angles [x,y,z] to Isaac Quaternion [w,x,y,z] format
def deg2quat_wxyz(euler_deg):
    quat_xyzw = R.from_euler('xyz', euler_deg, degrees=True).as_quat()
    quat_wxyz = np.roll(quat_xyzw, 1)  # xyzw -> wxyz
    return quat_wxyz.tolist()

# Custom Labware being used 
cwd = os.getcwd()
Labwear = {
    "Beaker": {
        "spawn.usd_path": os.path.join(cwd, "assets", "beaker", "beaker.usd"),
        "spawn.scale": (0.01, 0.01, 0.01),
        "init_state.pos": [0.5, 0, 0.055],
        "init_state.rot": deg2quat_wxyz([90, 0, 0]), # This is upright
    }, 
    "Round_Bot": {
        "spawn.usd_path": os.path.join(cwd, "assets", "round_bot", "round_bot.usd"),
        "spawn.scale": (0.01, 0.01, 0.01),
        "init_state.pos": [0.5, 0, 0.055],
        "init_state.rot": deg2quat_wxyz([90, 0, 0]), # This is upright
    },
    "Conical_flask": {
        "spawn.usd_path": os.path.join(cwd, "assets", "con_flask", "con_flask.usd"),
        "spawn.scale": (0.01, 0.01, 0.01),
        "init_state.pos": [0.5, 0, 0.055],
        "init_state.rot": deg2quat_wxyz([0, 0, 90]), # This is upright
    },
    
}
# Comment the following line to use the default object in the environment
obj_cfg = list(Labwear.values())[0] # or Labwear[next(iter(Labwear))] 

def obj_override(obj : object, overrides : dict) -> object:
    """Dynamically override the object spawn parameters in the environment confg."""
    for key, value in overrides.items():
        parts = key.split(".")
        target = obj
        for part in parts[:-1]:
            target = getattr(target, part)
        setattr(target, parts[-1], value)
    return obj

""" Rest as follows ... """

def main():
    """Running keyboard teleoperation with Isaac Lab manipulation environment."""

    """ ... """

    # Set the object to be overridden and teleported
    if os.path.exists(obj_cfg.get("spawn.usd_path", "")):
        env_cfg.scene.object = obj_override(env_cfg.scene.object, obj_cfg)

    """ ... """
   
```