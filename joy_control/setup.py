from setuptools import setup
import os
from glob import glob
package_name = 'joy_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/'+ package_name+'/launch',glob('./launch/*.launch.py')),
        ('share/'+ package_name,glob('./joy_control/M_9037*7228.npy')),
        ('share/'+ package_name,glob('./joy_control/M_15061*12046.npy')),
        ('share/'+ package_name,glob('./joy_control/M_30121*24091.npy'))
        
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jsy',
    maintainer_email='littlecat.j@hotmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': ['brain=joy_control.brain:main','quer_move = joy_control.quer_move:main',
        ],
    },
)
