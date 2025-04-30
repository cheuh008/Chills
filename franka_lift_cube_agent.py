import argparse
from isaaclab.app import AppLauncher

args_task = "Isaac-Lift-Cube-Franka-IK-Rel-v0"
args_teleop_device = "spacemouse"
args_num_envs = 1
args_sensitivity = 1.0

app_launcher = AppLauncher({
    "task": args_task,
    "teleop_device": args_teleop_device,
    "num_envs": args_num_envs,
    "sensitivity": 1,
    "enable_pinocchio": False
})
simulation_app = app_launcher.app

import gymnasium as gym
import numpy as np
import torch
import os
import omni.log
from isaaclab.devices import Se3Keyboard, Se3SpaceMouse
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab_tasks.manager_based.manipulation.lift import mdp
from isaaclab_tasks.utils import parse_env_cfg
from isaaclab.assets import RigidObjectCfg
from isaaclab.sim.spawners.from_files.from_files_cfg import UsdFileCfg
from isaaclab.sim.schemas.schemas_cfg import RigidBodyPropertiesCfg

glassware = ["round_bot", "beaker", "con_flask"]
usd_path = os.path.join(os.path.dirname(__file__), "assets", "Props", glassware[1], "instanceable_meshes.usd")


def pre_process_actions(teleop_data: tuple[np.ndarray, bool] | list[tuple[np.ndarray, np.ndarray, np.ndarray]], num_envs: int, device: str) -> torch.Tensor:
    delta_pose, gripper_command = teleop_data
    delta_pose = torch.tensor(delta_pose, dtype=torch.float, device=device).repeat(num_envs, 1)
    gripper_vel = torch.zeros((delta_pose.shape[0], 1), dtype=torch.float, device=device)
    gripper_vel[:] = -1 if gripper_command else 1
    return torch.concat([delta_pose, gripper_vel], dim=1)

def main():
    env_cfg = parse_env_cfg(args_task, device="cuda", num_envs=args_num_envs) #manually passing in Cuda for now
    env_cfg.env_name = args_task
    env_cfg.terminations.time_out = None
    env_cfg.scene.object = RigidObjectCfg(
        prim_path="{ENV_REGEX_NS}/Object",
        init_state=RigidObjectCfg.InitialStateCfg(pos=[0.5, 0, 0.055], rot=[1, 0, 0, 0]),
        spawn=UsdFileCfg(
            usd_path = usd_path,
            scale=(0.8, 0.8, 0.8),
            rigid_props=RigidBodyPropertiesCfg(
                solver_position_iteration_count=16,
                solver_velocity_iteration_count=1,
                max_angular_velocity=1000.0,
                max_linear_velocity=1000.0,
                max_depenetration_velocity=5.0,
                disable_gravity=False,
            ),
        ),
    )
    env_cfg.commands.object_pose.resampling_time_range = (1.0e9, 1.0e9)
    env_cfg.terminations.object_reached_goal = DoneTerm(func=mdp.object_reached_goal)
    env = gym.make(args_task, cfg=env_cfg).unwrapped
    should_reset_recording_instance = False
    teleoperation_active = True

    def reset_recording_instance():
        nonlocal should_reset_recording_instance
        should_reset_recording_instance = True

    devices = {
        "keyboard": Se3Keyboard,
        "spacemouse": Se3SpaceMouse,
    }
    try:
        teleop_interface = devices[args_teleop_device.lower()](
            pos_sensitivity=0.05 * args_sensitivity, rot_sensitivity=0.05 * args_sensitivity
        )
    except KeyError:
        raise ValueError(f"Unsupported device: {args_teleop_device}")

    teleop_interface.add_callback("R", reset_recording_instance)
    print(teleop_interface)

    env.reset()
    teleop_interface.reset()

    while simulation_app.is_running():
        with torch.inference_mode():
            teleop_data = teleop_interface.advance()
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
