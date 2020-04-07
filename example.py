import time,threading
import real_time_tools
from hardware_control import HardwareControl
from policy import Policy

def run():
    
    # encapsulates all the calls to
    # o80 frontends, for clarity
    # Note: hw_control also ensure clean exit
    #       of the robot (i.e. going to safe position)
    hw_control = HardwareControl()

    # initializing the simulation by having it mirroring
    # the real robot
    angles,angular_velocities,_ = hw_control.get_real_robot()
    hw_control.set_mirroring(angles,angular_velocities)
    
    # a dummy policy using pd control
    # with random target angles
    policy = Policy()

    # for drawing a goal in the simulation
    goal = [3,4]

    # torque control, at least 500Hz
    frequency_manager = real_time_tools.FrequencyManager(500)

    running=True
    while running:

        print("\n-- starting episode --")
        
        # starting an episode

        # set back the robot to init position using
        # pd controller
        print("\treset robot")
        hw_control.reset_real_robot(500)

        # shooting a real ball
        print("\tshooting real ball")
        hw_control.shoot_ball()
        
        # shooting simulated balls
        print("\tshooting virtual balls")
        hw_control.shoot_sim_balls()

        # getting the iteration number of the simulation at the start of the
        # episode. Will be used to retrieve at the end of the episode
        # its full history of observations 
        sim_iteration = hw_control.get_sim_iteration()
        
        time_start = time.time()

        # episode ends after 3 seconds,
        while time.time()-time_start < 3 :

            # getting newest state of the robot
            angles,angular_velocities,_ = hw_control.get_real_robot()
            
            # getting related torques from policy
            torques = policy.get_torques(angles,
                                         angular_velocities)

            # sending torques to real robot
            hw_control.set_real_torques(torques)

            # sending mirroring commands to simulated robot
            simulated_world_state = hw_control.set_mirroring(angles,angular_velocities)

            # getting position of real ball from vision system
            ball_position  = hw_control.get_ball_from_vision()

            # imposing frequency
            frequency_manager.wait()
            

        # episode end
        # getting episode's simulation history 
        history = hw_control.get_sim_history(sim_iteration)
        # counting the number of contacts between virtual racket
        # and virtual balls
        nb_contacts = sum([sum(observation.get_extended_state().balls_hits_racket)
                           for observation in history])
        print("\tvirtual contacts: "+str(nb_contacts))
        

        
if __name__ == "__main__":

    try :
        run()
    except KeyboardInterrupt:
        pass
