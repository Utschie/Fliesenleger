# Fliesenleger

## update on 2022.04.13

  will be restart
  
## update on 2021.06.20
1. one of two types of recognition methods has been integrated, not perfekt, but one can play.  
2. rviz2 isn't  launched with the world  

## update on 2021.06.18
1. under the directory run these orders  
```
colcon build
. install/setup.bash
. /usr/share/gazebo/setup.sh
```
2. launch the world, then all nodes startup,you can use joystick to control the maschine
```
ros2 launch joy_control joy_control.launch.py
```
or  
```
ros2 launch joy_control joy_control.launch.py world:=world_2
```
if the 'world' argument not modified, the default world is world_1  
3. the recognition part haven't been integrated yet.
## update on 2021.06.07
1.insert the model 'nested_model' in your world  
2.enable your xbox joystick, see update in 2021.06.02  
3.under '/Fliesenleger/ros2_control' open a terminal, use the order
```
. install/setup.bash

ros2 run brain brain_node
```

with the messages showing on the screen you can do it
## update on 2021.06.02

under the directory 'Fliesenleger' open a terminal,use the order
```
ros2 launch teleop_twist_joy teleop-launch.py joy_config:='xbox' config_filepath:=./ros2_control/teleop_twist_joy_node.yaml
```
then you can use your xbox joystick control your fliesenleger


