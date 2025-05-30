# Copyright (c) 2022-2025, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

# Code based on IsaacLab\scripts\environments\teleoperation\teleop_se3_agent.py

"""
python .\object_override.py --task Isaac-Lift-Cube-Franka-IK-Rel-v0
python .\object_override.py --task Isaac-Lift-Cube-Franka-IK-Rel-v0 --teleop_device spacemouse 

use obj_cfg = list(Labwear.values())[0] # or Labwear[next(iter(Labwear))] # Below to chnage the enviorment object

"""

# Import base main 
 
import argparse
from isaaclab.app import AppLauncher 

# argparse command line arguments
parser = argparse.ArgumentParser(description="Keyboard teleoperation for Isaac Lab environments.")
parser.add_argument("--num_envs", type=int, default=1, help="Number of environments to simulate.")
parser.add_argument("--teleop_device", type=str, default="keyboard", help="Device for interacting with environment")
parser.add_argument("--task", type=str, default="Isaac-Lift-Cube-Franka-v0", help="Name of the task.")
parser.add_argument("--sensitivity", type=float, default=2.0, help="Sensitivity factor.")
parser.add_argument("--enable_pinocchio", action="store_true", default=False, help="Enable Pinocchio.",)

# Isaac Sim app launcher 
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()
app_launcher_args = vars(args_cli)
app_launcher = AppLauncher(app_launcher_args)
simulation_app = app_launcher.app

"""Rest everything follows."""

import torch
import omni.log
import isaaclab_tasks   
import numpy as np
import gymnasium as gym 
from isaaclab.devices import  Se3Keyboard, Se3SpaceMouse 
from isaaclab.managers import TerminationTermCfg as DoneTerm 
from isaaclab_tasks.manager_based.manipulation.lift import mdp
from isaaclab_tasks.utils import parse_env_cfg
from scipy.spatial.transform import Rotation as R 
import os 

# Changes from Euler (360') Angles [x,y,z] to Isaac Quaternion [w,x,y,z] format
def deg2quat_wxyz(euler_deg):
    quat_xyzw = R.from_euler('xyz', euler_deg, degrees=True).as_quat()
    quat_wxyz = np.roll(quat_xyzw, 1)  # xyzw -> wxyz
    return quat_wxyz.tolist()

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
obj_cfg = list(Labwear.values())[2] # or Labwear[next(iter(Labwear))] 

def obj_override(obj : object, overrides : dict) -> object:
    """Dynamically override the object spawn parameters in the environment confg."""
    for key, value in overrides.items():
        parts = key.split(".")
        target = obj
        for part in parts[:-1]:
            target = getattr(target, part)
        setattr(target, parts[-1], value)
    return obj

def pre_process_actions(
    teleop_data: tuple[np.ndarray, bool] | list[tuple[np.ndarray, np.ndarray, np.ndarray]], num_envs: int, device: str) -> torch.Tensor:
    """ Convert teleop data to  Processed actions as a tensor """
    # resolve gripper command, convert to torch and computes actions
    delta_pose, gripper_command = teleop_data
    delta_pose = torch.tensor(delta_pose, dtype=torch.float, device=device).repeat(num_envs, 1)
    gripper_vel = torch.zeros((delta_pose.shape[0], 1), dtype=torch.float, device=device)
    gripper_vel[:] = -1 if gripper_command else 1
    return torch.concat([delta_pose, gripper_vel], dim=1)

def main():
    """Running keyboard teleoperation with Isaac Lab manipulation environment."""

    env_cfg = parse_env_cfg(args_cli.task, device=args_cli.device, num_envs=args_cli.num_envs)
    env_cfg.env_name = args_cli.task
    env_cfg.terminations.time_out = None

    # Set the object to be teleoperated
    if os.path.exists(obj_cfg.get("spawn.usd_path", "")):
        env_cfg.scene.object = obj_override(env_cfg.scene.object, obj_cfg)
             
    env_cfg.commands.object_pose.resampling_time_range = (1.0e9, 1.0e9)
    env_cfg.terminations.object_reached_goal = DoneTerm(func=mdp.object_reached_goal)
    env = gym.make(args_cli.task, cfg=env_cfg).unwrapped
    
    print(f"Environment: {env}")

    # Flags for controlling teleoperation flow
    should_reset_recording_instance = False
    teleoperation_active = True

    # Callback handlers
    def reset_recording_instance():
        """Reset the environment when the user presses the reset key (typically 'R')"""

        nonlocal should_reset_recording_instance
        should_reset_recording_instance = True

    # create controller
    if args_cli.teleop_device.lower() == "keyboard":
        teleop_interface = Se3Keyboard(
            pos_sensitivity=0.05 * args_cli.sensitivity, rot_sensitivity=0.05 * args_cli.sensitivity
        )
    elif args_cli.teleop_device.lower() == "spacemouse":
        teleop_interface = Se3SpaceMouse(
            pos_sensitivity=0.05 * args_cli.sensitivity, rot_sensitivity=0.05 * args_cli.sensitivity
        )
    else:
        raise ValueError(
            f"Invalid device interface '{args_cli.teleop_device}'. Supported: 'keyboard', 'spacemouse', 'gamepad',"
            " 'handtracking', 'handtracking_abs'."
        )

    # add teleoperation key for env reset (for all devices)
    teleop_interface.add_callback("R", reset_recording_instance)
    print(teleop_interface)

    # reset environment
    env.reset()
    teleop_interface.reset()

    while simulation_app.is_running():
        with torch.inference_mode():
            teleop_data = teleop_interface.advance()

            # Only apply teleop commands, compute and aply actions when active
            if teleoperation_active:
                actions = pre_process_actions(teleop_data, env.num_envs, env.device)
                env.step(actions)

            else:
                env.sim.render()

            if should_reset_recording_instance:
                env.reset()
                should_reset_recording_instance = False
    env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()


