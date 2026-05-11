#!/usr/bin/python3

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped

class Driver(Node):
    def __init__(self):
        super().__init__('driver')
        thepub = self.create_publisher(PoseStamped,'/goal_pose',1)
        dest = PoseStamped()
        dest.pose.position.x = 2.0
        thepub.publish(dest)
        
def main(args=None):
    rclpy.init(args=args)
    d = Driver()
    rclpy.spin(d)

main()

