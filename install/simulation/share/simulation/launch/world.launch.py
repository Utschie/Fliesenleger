import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration,Command
from launch_ros.actions import Node


def generate_launch_description():
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')#返回gazebo_ros包的路径
    pkg_simulation = get_package_share_directory('simulation')
    pkg_teleop_twist_joy = get_package_share_directory('teleop_twist_joy')#返回teleop_twist_joy包的路径
    world_argument = DeclareLaunchArgument(
          'world',
          default_value='world_1',
          choices = ['world_1','world_2'],
          description='world:= world_1 | world_2')
    world_file_dir = os.path.join(pkg_simulation,'worlds')
    # Gazebo  launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py'),
            
            
        ),
        #use [] to join the strings and substitutions
        launch_arguments = {'world':[world_file_dir,'/',LaunchConfiguration('world'),'.world']}.items()
    )
    
    #teleop_twist_joy launch
    teleop = IncludeLaunchDescription(
       PythonLaunchDescriptionSource(
            os.path.join(pkg_teleop_twist_joy, 'launch', 'teleop-launch.py'),
        ),
        launch_arguments={'joy_config':'xbox','config_filepath':pkg_simulation+'/launch/teleop_twist_joy_node.yaml'}.items(),
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
       gazebo,
       teleop

    ])
