import time,math,random
from roboball2d.physics import B2World
from roboball2d.robot.pd_controller import PDController


# dummy policy moving the robot to a new
# reference posture every 2 seconds
class Policy:

    def __init__(self,
                 min_angle = -math.pi/3,
                 max_angle = 0,
                 transition_time=0.8):
        self._min_angle = min_angle
        self._max_angle = max_angle
        self._range = max_angle-min_angle
        self._references = self._random_references()
        self._start_time = time.time()
        self._controller = PDController()
        self._transition_time = transition_time

    def _random_references(self):
        references = [self._min_angle+random.random()*self._range
                           for _ in range(3)]
        return references
        
    def _switch_ref(self):
        t = time.time()
        if t-self._start_time>self._transition_time:
            self._start_time = t
            self._references = self._random_references()
                
    def get_torques(self,angles,angular_velocities):

        self._switch_ref()
        return self._controller.get(self._references,
                                    angles,
                                    angular_velocities)
