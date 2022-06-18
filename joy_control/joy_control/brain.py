import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import numpy as np
from std_msgs.msg import String
from sensor_msgs.msg import Joy
from .ImgSubscriber import ImgSubscriber
from .Recognizer import Recognizer_small,Recognizer_middle,Recognizer_big
#import time
from gazebo_msgs.srv import SpawnEntity
from ament_index_python.packages import get_package_share_directory
from sensor_msgs.msg import Image
class Brain(Node):
    def __init__(self):
        super().__init__('brain')
        self.declare_parameter('world','world_1')
        self.tile_type = {'world_1':'/models/Fliesen/Yellow_60*60_noshadow_notexture/model.sdf',
                          'world_2':'/models/Fliesen/Yellow_60*30_noshadow_notexture/model.sdf'
                        }
        self.world = self.get_parameter('world').get_parameter_value().string_value
        self.tile_path = get_package_share_directory('simulation')+self.tile_type[self.world]
        self.state_subscription = self.create_subscription(Twist,'/cmd_vel',self.state_callback,10)
        self.state_subscription  # prevent unused variable warning
        self.publisher = self.create_publisher(String, '/dialog', 10)
        self.output = String()
        self.joy_subscription = self.create_subscription(Joy,'/joy',self.joy_callback,1)
        self.joy_subscription
        self.img_subscription_left = self.create_subscription(
            Image,
            '/demo_cam/mycamera/left/image_demo',
            self.img_callback_left,
            1)
        self.img_subscription_right = self.create_subscription(
        Image,
        '/demo_cam/mycamera/right/image_demo',
        self.img_callback_right,
        1)
        #self.img_publisher_left = self.create_publisher(Image,'/camera/left',10)#
        #self.img_publisher_right= self.create_publisher(Image,'/camera/right',10)
        self.img_subscription = ImgSubscriber()
        self.img_subscription
        self.recognizer = Recognizer_small(self.world)
        self.spawn_node = rclpy.create_node("entity_spawner")
        self.spawn_node.cli = self.spawn_node.create_client(SpawnEntity, "/spawn_entity")
        self.commu_subscriber = self.create_subscription(Twist,'/cmd_vel',self.commu_callback,10)
        self.commu_publisher = self.create_publisher(Twist,'/demo/cmd_demo',10)
        #self.tile_path = get_package_share_directory('simulation')+'/models/Fliesen/Yellow_60*60/model.sdf'
        self.state = {'Mode':'Move Mode','recog_finished':False,}
        self.if_static = True
        self.if_move = True
        self.box_coordinate = None
    
    def img_callback_left(self,msg):
        #if self.state['Mode'] == 'Move Mode':
            #self.img_publisher_left.publish(msg)
        self.left_img = np.array(msg.data)
        self.left_img = self.left_img.reshape((3648,5472,3))

    def img_callback_right(self,msg):
        #if self.state['Mode'] == 'Move Mode':
            #self.img_publisher_right.publish(msg)
        self.right_img = np.array(msg.data)
        self.right_img = self.right_img.reshape((3648,5472,3))
    
    def commu_callback(self,msg):
        if self.if_move == True:
            self.commu_publisher.publish(msg)

    def state_callback(self,msg):
        self.state_msg = msg
        self.if_static =([self.state_msg.linear.x,self.state_msg.linear.y,self.state_msg.linear.z,self.state_msg.angular.x,self.state_msg.angular.y,self.state_msg.angular.z]==[0.,0.,0.,0.,0.,0.])
        if self.state['Mode'] == 'Move Mode':#if in Move Mode
            if self.if_static and self.state['recog_finished'] == False:#if the machine is static and haven't recognized the ground
                if self.output.data =='Moving...':
                    self.output.data = 'The Flisenleger is stopped, will you start to recognize?  Press "B" enter Pave Mode'
                    self.publisher.publish(self.output)
                    self.get_logger().info('The Flisenleger is stopped, will you start to recognize?  Press "B" enter Pave Mode')
            else:
                if self.output.data !='Moving...':
                    self.output.data = 'Moving...'
                    self.publisher.publish(self.output)
                    self.get_logger().info('Moving...')
    
    def joy_callback(self,msg):
        self.joy_msg = msg
        if self.if_static:#only in static can switch the Mode      
            if self.joy_msg.buttons[1]==1 and self.state['Mode']=='Move Mode':#in Move Mode, press "B" to switch to Pave Mode
                self.state['Mode'] ='Pave Mode'
                self.if_move=False
                if self.output.data != 'Now you are in Pave Mode, press "X" to recognize or ,press "Y" to move.':
                    self.output.data = 'Now you are in Pave Mode, press "X" to recognize or ,press "Y" to move.'
                    self.publisher.publish(self.output)
                    self.get_logger().info('Now you are in Pave Mode, press "X" to recognize or ,press "Y" to move.')
               
            elif self.joy_msg.buttons[2]==1 and self.state['Mode']=='Pave Mode':
                if self.output.data != 'Start recognizing...':
                    self.output.data = 'Start recognizing...' 
                    self.publisher.publish(self.output)
                    self.get_logger().info('Start recognizing...')
                    self.img_recognition()
            elif self.joy_msg.buttons[3]==1 and self.state['Mode']=='Pave Mode':#in Pave Mode, press "Y" to switch to Move Mode
                self.state['Mode'] ='Move Mode'
                self.if_move=True
                self.state['recog_finished']=False
                if self.output.data != 'Now you are in Move Mode, press "Y" to enter into Pave Mode.':
                    self.output.data = 'Now you are in Move Mode, press "Y" to enter into Pave Mode.'
                    self.publisher.publish(self.output)
                    self.get_logger().info('Now you are in Move Mode, press "Y" to enter into Pave Mode.')
            elif self.joy_msg.buttons[0] == 1 and self.state['recog_finished'] and self.state['Mode']=='Pave Mode':#if Recognition finished and still in Pave Mode
                self.spawn_a_tile(self.box_coordinate[0])#spawn a tile on given coordinates
    
                
    def img_recognition(self):
        self.box_coordinate = self.recognizer.durch_translation(self.left_img)
        #if self.output.data != 'Recognition finished!, the coordinate is...':
        if len(self.box_coordinate)==0:
            #self.output.data = 'Recognition failed,please adjust the maschine\'s position and try it again '
            #self.publisher.publish(self.output)
            self.get_logger().info('Recognition failed,please adjust the maschine\'s position and try it again ')

        else:
            #self.output.data = 'Recognition finished!, the coordinate is '+str(self.box_coordinate[0])#there is the other topic '/dialog',in which one can see the messeges
            #self.publisher.publish(self.output)
            self.get_logger().info('Recognition finished!, the coordinate is '+str(self.box_coordinate[0]))
            self.state['recog_finished'] = True#after Recognition this state switch to True
            #if self.output.data != 'Press "A" to pave a tile,or press "Y" to move':
            #self.output.data = 'Press "A" to pave a tile, or press "Y" to move'
            #self.publisher.publish(self.output)
            self.get_logger().info('Press "A" to pave a tile, or press "Y" to move')
    
    
    
    def spawn_a_tile(self,coordinate):
        request = SpawnEntity.Request()
        request.xml = open(self.tile_path, 'r').read()
        request.initial_pose.position.x = coordinate[0]
        request.initial_pose.position.y = coordinate[1]
        request.initial_pose.position.z = coordinate[2]
        request.initial_pose.orientation.z = -np.sin(np.deg2rad(coordinate[5])/2)#orientation.z ist from quaternion,so we must transform the angle um Z-axis to quaternion
        request.reference_frame = 'move_wheel_box::link_1'
        future = self.spawn_node.cli.call_async(request)
        rclpy.spin_until_future_complete(self.spawn_node, future)
        if future.result() is not None:
            print('response: %r' % future.result())
            self.state['recog_finished'] = False #after paving a tile, this state is set to be False, one must recognize one more time to pave
            self.output.data ='The tile has benn paved, press "X" continue to recognition or press "Y" to move'
            self.publisher.publish(self.output)
            self.get_logger().info('The tile has benn paved, press "X" continue to recognition or press "Y" to move')
        return
        
        


def main(args=None):
    rclpy.init(args=args)
    brain = Brain()
    rclpy.spin(brain)
    brain.spawn_node.destroy_node()
    brain.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
