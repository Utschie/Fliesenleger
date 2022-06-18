# Fliesenleger
## Install the environment and dependencies
1. Install ros2 Rolling <https://docs.ros.org/en/rolling/Installation/Ubuntu-Install-Debians.html>
2. Install Gazebo 11 <https://classic.gazebosim.org/tutorials?tut=install_ubuntu#Defaultinstallation:one-liner>
3. Install gazebo_ros,ros-rolling-joy,Numpy,Opencv
```
sudo apt install ros-rolling-gazebo-ros-pkgs
sudo apt-get install ros-rolling-joy
pip install numpy
sudo apt install libopencv-dev python3-opencv
```
4. Clone this repository to local
```
git clone https://github.com/Utschie/Fliesenleger.git
```
## Build the project and play.
5. Change directory to the local repository
```
cd Fliesenleger
```
6. Build and setup the project
```
colcon build
. install/setup.bash
. /usr/share/gazebo/setup.sh
```
7. In the same terminal and directory, launch the world, then all nodes startup,you can use joystick to control the maschine
```
ros2 launch joy_control joy_control.launch.py
```
or  
```
ros2 launch joy_control joy_control.launch.py world:=world_2
```
If the 'world' argument not modified, the default is world_1  
8. Open a new terminal and run rviz2
```
rviz2
```
Add a Image visualization, set the Topic to '/demo_cam/mycamera/left/image_demo' or '/demo_cam/mycamera/right/image_demo'

9. Use your Xbox joystick and follow the prompts on the screen.



