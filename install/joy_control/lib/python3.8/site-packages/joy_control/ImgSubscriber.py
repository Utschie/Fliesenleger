from rclpy.node import Node
from sensor_msgs.msg import Image
class ImgSubscriber(Node):
    def __init__(self):
        super().__init__('img_subscriber')
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
    def img_callback_left(self,msg):
        self.left_img = msg.data
        self.left_img = self.left_img.reshape((3648,5472,3))
        
    def img_callback_right(self,msg):
        self.right_img = msg.data
        self.right_img = self.right_img.reshape((3648,5472,3))