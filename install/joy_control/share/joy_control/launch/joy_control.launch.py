import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    pkg_simulation = get_package_share_directory('simulation')#返回环境包share路径
    world_argument = DeclareLaunchArgument(
          'world',
          default_value='world_1',
          choices = ['world_1','world_2'],
          description='world:= world_1 | world_2')
          
    #simulation launch 
    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_simulation, 'launch', 'world.launch.py'),
            
            
        ),
        launch_arguments = {'world':LaunchConfiguration('world')}.items()
    )
    
    #brain node
    brain = Node(
    	package = 'joy_control',
    	executable = 'brain',
    	output='screen',
    	parameters = [{'world':LaunchConfiguration('world')}]
    )
    
    #quer_move node
    quer_move = Node(
    	package = 'joy_control',
    	executable = 'quer_move',
    )
  

#    # RViz
#    rviz = Node(
#        package='rviz2',
#        executable='rviz2',
#        arguments=['-d', os.path.join(pkg_dolly_gazebo, 'rviz', 'dolly_gazebo.rviz')],
#        condition=IfCondition(LaunchConfiguration('rviz'))
#    )

    return LaunchDescription([
       world_argument,
       brain,
       #brain must launch before the simulation, otherwise the shared argument 'world' will be changed by simulation, or can one use a  different argument name, then the launch sequence is egal 
       quer_move,
       simulation,
       

    ])
