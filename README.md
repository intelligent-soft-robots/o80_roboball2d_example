
# What it is

o80 is a software for synchronizing and communicating with processes.
It is a candidate for helping the development of software architecture of systems involving several processes running in parallel at various frequencies.
This example is made to evaluate o80 in a lightweight virtual environment, before possible deployment on real systems.

In this example, 5 processes run in parallel:
- 1: a virtual torque controlled robot running continuously at high frequency.
- 2: a virtual ball gun, shooting tennis ball in direction of the robot.
- 3: a vision system, broadcasting the state of the shot ball.
- 4: another virtual robot, but in a simulated environment which performs an iteration only when commanded to do so.
- 5: a virtual ball gun able to shoot 5 balls in this simulated environment.

The processes above have been developed using [roboball2d](https://github.com/intelligent-soft-robots/roboball2d).

Drivers to these processes are encapsulated by o80 backend servers, and o80 frontend API is used to develop, as an example, this application which runs episodes in a loop, each episode consisting of:

- A PD controller is used to send command to (1) via an o80 frontend such as having (1) reaching a starting vertical initial posture
- o80 frontends are used to get (2) and (5) to shoot balls
- a PD controller is used to compute torques such as having (1) moving to random postures.
- the state of (1) is used to create mirroring commands for (4) (i.e. to have (4) mirroring (1)).
- the torques commands are sent via o80 frontend to (1). Mirroring commands are sent via another o80 frontend to (4), which triggers an iteration of the simulation.
- the state of the ball shot by (2) is retrieved using o80 backend connected to (3) (for demonstration only, state not used).
- At the end of the episode, o80 frontend is used to get all the episode's observations. This history is used to compute the number of balls shot by (5) which hit the racket of (4).

When the application is exited, the robot (1) goes back to a safe position before releasing all torques.

The objective of o80 frontends is to provide an API simple yet powerful enough to make the development of the application above trivial.

# Installation

Installation requires a machine installed with ubuntu 18.04.

## installing dependencies

After cloning of [ubuntu installation scripts](https://github.com/machines-in-motion/ubuntu_installation_scripts.git), the script setup_ubuntu (in the 'official' folder) can be run, passing the option 'ros':

```bash
sudo ./setup_ubuntu install ros
```

### Note 1
This installation script does not do anything fancy. It (almost) just install software using aptitute and pip, i.e. it does not create some complicated systems difficult to track, or that could break anything else you already have installed on your machine.

### Note 2
If you'd rather not have ros installed, you may run instead:

```bash
sudo ./setup_ubuntu install core
```
Ros is not a required dependency, but is convenient (e.g. rosrun, roslaunch, etc)

### Note 3

You may also pull the corresponding docker image : docker.is.localnet:5000/amd/18.04:ros
You need first to login to docker.is.localnet:

```bash
docker login https://docker.is.localnet:5000
```

In case of issue, you may try to add to /etc/docker/daemon.json:

```bash
{
    "insecure-registries": [ "docker.is.localnet:5000" ]
}
```

and restart docker:

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

## SSH setup

You need a github account. Set up your ssh key to github : [github help](https://help.github.com/en/enterprise/2.17/user/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)

## Cloning treep project

Create a new workspace and clone treep_isr ('isr'='intelligent soft robots')

```bash
mkdir Software # you may call the folder whatever you like
cd Software
git clone git@github.com:intelligent-soft-robots/treep_isr.git
treep --clone O80_ROBOBALL2D
```

## Compiling

```bash
cd workspace
source /opt/ros/melodic/setup.bash 
catkin_make -DPYTHON_EXECUTABLE=/usr/bin/python3 install
```

## Setting up bashrc file

To make sure things are activated properly in all new terminals you open, you may add to your ~/.bashrc file
(replacing <absolute path to Software> by what makes sense):

```bash
echo "sourcing o80 roboball2d"
source /opt/ros/melodic/setup.bash
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:<absolute path to Software>/workspace/devel/lib
source <absolute path to Software>/workspace/install/setup.bash
```

# Running the example

Must be run in this order:

## starting all the simulated "hardware"

In a terminal:

```bash
rosrun roboball2d_interface start_roboball2d_hardware
```

3 windows should appear : 
- the first simulated robot and ballgun (1) and (2)
- the vision system (3) 
- the second simulated robot (4) and ballgun (5)

## starting the o80 backends

In another terminal, start the backends:

```bash
cd Software/workspace/src/o80/o80_roboball2d_example
python3 start_o80_servers.py
```

## starting the example

```bash
cd Software/workspace/src/o80/o80_roboball2d_example
python3 example.py
```

## Exit

- the example can be exited with ctrl+c. It can then be restarted.
- the o80 backends can not be exited in other way than closing the corresponding terminal. This will be improved soon.
- the "hardware" can be exited by calling "stop_roboball2d_hardware" in a terminal other than the one the hardware was started in.

# Troubleshooting

Issues may occur if programs are not exited cleanly, or not in the right order. This may block the applications to be started again. If this happens, cleaning the shared memory should help:

```bash
sudo rm /dev/shm/*
```
 
# Software overview

The following packages are used in this example:

- robot_interfaces : an common interface for hardware drivers, developed at MPI-IS. See : [github odri](https://github.com/open-dynamic-robot-initiative/robot_interfaces)
- o80, tools for synchronizing processes, sending commands and reading observations. o80 is build on top of robot_interfaces. See: [github isr](https://github.com/intelligent-soft-robots/o80)
- roboball2d : a python simulated robot playing with balls. See : [roboball2d](https://roboball2d.readthedocs.io/)
- roboball2d_interface : the driver to roboball2d, according to the interface provided by robot_interfaces. See: [github isr](https://github.com/intelligent-soft-robots/roboball2d_interface)
- o80_roboball2d : the o80 backends and frontends on top of roboball2d_interface. See: [github isr](https://github.com/intelligent-soft-robots/o80_roboball2d)
- o80_roboball2d_example : an example showing the user code using the API provided by o80_roboball2d. See: [gitub isr](https://github.com/intelligent-soft-robots/o80_roboball2d_example)  

# Limitations

This software has been created for the purpose of testing o80. It is not expected to be used beyond this, and no documentation is offered.
 
 # Author
 
 Vincent Berenz, Max Planck Institute for Intelligent Systems
 
