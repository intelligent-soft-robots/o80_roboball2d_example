import time,sys,atexit

import roboball2d_interface
import o80_roboball2d


# 1 robot, 1 ball
import o80_roboball2d_torques as o80_real_robot
import o80_roboball2d_ball_gun as o80_ball_gun
import o80_roboball2d_vision as o80_vision

# 1 robot, 5 balls
import o80_roboball2d_5balls_ball_gun as o80_sim_ball_gun
import o80_roboball2d_5balls_mirroring as o80_sim_robot



class Standalones:

    @classmethod
    def start(cls):

        # bursting -> o80 server performing one (or several) iteration
        # only when asked to do so (via the "burst" function)
        bursting = True

        # not bursting -> o80 server running continuously at
        # specified frequency
        not_bursting = False

        frequency_real_robot = 2000
        frequency_vision = 500

        # o80 server controlling the ball gun (will send "shoot" commands)
        o80_ball_gun.start_standalone("o80_ball_gun", # o80 id, for front end to plug in
                                      -1, # frequency of server (unused, bursting mode)
                                      bursting, # runs iterations only when front-end demands
                                      "real-ball-gun") # id driver uses to connect to hardware
        
        # o80 server controlling the robot (wil send torque commands)
        o80_real_robot.start_standalone("o80_real_robot",frequency_real_robot,
                                        not_bursting,"real-robot")

        # o80 server controlling simulated ball guns (will send "shoot" commands)
        o80_sim_ball_gun.start_standalone("o80_sim_ball_guns",-1,
                                      bursting,"sim-ball-guns")

        # o80 server controlling simulated robot (will send "mirroring" commands)
        # bursting mode: the simulation will run an iteration only when asked to
        o80_sim_robot.start_standalone("o80_sim_robot",-1,bursting,"sim-robot")

        # o80 server connecting to the vision system, which will returns
        # the position of the ball
        o80_vision.start_standalone("o80_vision",frequency_vision,not_bursting,
                                    "vision")
    

    @classmethod
    def stop(cls):
        o80_ball_gun.stop_standalone("o80_ball_gun")
        o80_real_robot.stop_standalone("o80_real_robot")
        o80_5balls_ball_gun.stop_standalone("o80_sim_ball_guns")
        o80_5balls_sim_robot.stop_standalone("o80_sim_robot")
        o80_vision.stop_standalone("o80_vision")
        
if __name__ == "__main__":
    
    Standalones.start()

    atexit.register(Standalones.stop)

    while True:
        try :
            time.sleep(0.05)
        except KeyboardInterrupt:
            break

    
