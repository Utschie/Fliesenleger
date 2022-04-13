import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy

class Quermove(Node):
    def __init__(self):
        super().__init__('joy_subscriber')
        self.joy_subscription = self.create_subscription(
            Joy,
            '/joy',
            self.sub_callback,
            10)
        self.joy_publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10)
        self.pub_msg = Twist()
    def sub_callback(self,msg):
        if (msg.axes[6]!=0.) or (msg.axes[7]!=0.):
            self.pub_msg.linear.x = msg.axes[7]*0.7
            self.pub_msg.linear.y = msg.axes[6]*0.7
            self.joy_publisher.publish(self.pub_msg)


def main(args=None):
    rclpy.init(args=args)
    quermove_node = Quermove()
    rclpy.spin(quermove_node)
    quermove_node.destroy_node()
    rclpy.shutdown()

    
if __name__ == '__main__':
    main()