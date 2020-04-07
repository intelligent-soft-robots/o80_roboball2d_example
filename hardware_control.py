import time,math,random,atexit

import real_time_tools

from roboball2d.physics import B2World
from roboball2d.robot.pd_controller import PDController

import o80
import roboball2d_interface
import o80_roboball2d

# 1 robot, 1 ball
import o80_roboball2d_torques as o80_real_robot
import o80_roboball2d_ball_gun as o80_ball_gun
import o80_roboball2d_vision as o80_vision

# 1 robot, 5 balls
import o80_roboball2d_5balls_ball_gun as o80_sim_ball_gun
import o80_roboball2d_5balls_mirroring as o80_sim_robot


class HardwareControl:

    def __init__(self,reset_real_robot_angles=[0,0,0]):

        self._reset_real_robot_angles = reset_real_robot_angles
        self._reset_controller = PDController()
        
        # related front ends (clients). Used to send commands to the o80 servers
        self._ball_gun = o80_ball_gun.FrontEnd("o80_ball_gun")
        self._real_robot = o80_real_robot.FrontEnd("o80_real_robot")
        self._sim_ball_guns = o80_sim_ball_gun.FrontEnd("o80_sim_ball_guns")
        self._sim_robot = o80_sim_robot.FrontEnd("o80_sim_robot")
        self._vision = o80_vision.FrontEnd("o80_vision")

        # important: making sure things exit cleanly
        atexit.register(self.clean_exit)
        
        # letting time to start properly
        time.sleep(0.1)

    # bringing robot to save place,
    # and deleting the o80 frontends (important to be able to restart them)
    def clean_exit(self):

        print("\n\texiting, please wait ...\n")
        
        # using pd controller to have the robot almost lying
        self.reset_real_robot(500,duration_sec=2.0,refs=[-math.pi/2.5,0,0])

        # removing torques
        joint = o80_roboball2d.Joint()
        joint.set_torque(0)
        for dof in range(3):
            self._real_robot.add_command(dof,
                                         joint,
                                         o80.Mode.OVERWRITE)
        self._real_robot.pulse()
        time.sleep(0.1)

        # cleaning o80 frontends
        del self._ball_gun
        del self._real_robot
        del self._sim_ball_guns
        del self._sim_robot
        del self._vision

    # send a shoot command to the o80 ball gun server
    def shoot_ball(self):
        shoot = o80.BoolState(True)
        self._ball_gun.add_command(0,shoot,o80.Mode.OVERWRITE)
        self._ball_gun.burst(1)

    # send a shoot command to the o80 simulated ball guns server
    def shoot_sim_balls(self):
        shoot = o80.BoolState(True)
        self._sim_ball_guns.add_command(0,shoot,o80.Mode.OVERWRITE)
        self._sim_ball_guns.burst(1)

    # send torques commands to the o80 real robot
    def set_real_torques(self,torques):
        for dof,torque in enumerate(torques):
            joint = o80_roboball2d.Joint()
            joint.set_torque(torque)
            self._real_robot.add_command(dof,
                                   joint,
                                   o80.Mode.OVERWRITE)
        self._real_robot.pulse()

    # reading newest state of the robot        
    def get_real_robot(self):
        joint_states = self._real_robot.pulse().get_observed_states()
        angles = [ joint_states.get(dof).get_position()
                   for dof in range(3) ]
        angular_velocities = [ joint_states.get(dof).get_velocity()
                               for dof in range(3) ]
        torques = [ joint_states.get(dof).get_torque()
                    for dof in range(3) ]
        return angles,angular_velocities,torques

    # runs a pd controller to set the robot back to the
    # initial posture
    def reset_real_robot(self,frequency,duration_sec=2.0,refs=None):
        if refs is None:
            refs = self._reset_real_robot_angles
        time_start = time.time()
        delta_t = 0
        frequency_manager = real_time_tools.FrequencyManager(frequency)
        while delta_t < duration_sec:
            delta_t = time.time()-time_start
            angles,angular_velocities,_ = self.get_real_robot()
            torques = self._reset_controller.get(refs,
                                                 angles,
                                                 angular_velocities)
            for dof,torque in enumerate(torques):
                joint = o80_roboball2d.Joint()
                joint.set_torque(torque)
                self._real_robot.add_command(dof,joint,
                                             o80.Mode.OVERWRITE)
            self._real_robot.pulse()
            frequency_manager.wait()
            
    # sending mirroring commands to simulated robot.
    # and returning simulated world state (i.e. all info
    # managed by the simulation, including simulated balls)
    def set_mirroring(self,angles,angular_velocities):
        for dof in range(3):
            mirror_joint = o80_roboball2d.MirrorJoint()
            mirror_joint.set(angles[dof],
                             angular_velocities[dof])
            self._sim_robot.add_command(dof,mirror_joint,o80.Mode.OVERWRITE)
        observation = self._sim_robot.burst(1)
        return observation.get_extended_state()

    # getting detected position of the ball
    def get_ball_from_vision(self):
        world_state = self._vision.pulse().get_extended_state()
        return world_state.ball.position

    # getting the current iteration number of the simulation
    def get_sim_iteration(self):
        return self._sim_robot.get_current_iteration()

    # getting the history of observations generated by the
    # simulation (history since the specified iteration number)
    def get_sim_history(self,since_iteration):
        history = self._sim_robot.get_history_since(since_iteration)
        return history
                


        

                
        
