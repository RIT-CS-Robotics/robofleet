#!/usr/bin/python3
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PoseWithCovarianceStamped

class InitPub(Node):
    def __init__(self):
        super().__init__('initpub')
        self.ippub = self.create_publisher(PoseWithCovarianceStamped, '/initialpose', 1)
        self.create_timer(1.0,self.doit)
        
    def doit(self):
        initpose = PoseWithCovarianceStamped()
        initpose.pose.pose.position.x = 10.0
        initpose.header.frame_id = 'map'
        self.ippub.publish(initpose)
        
def main(args=None):
    rclpy.init(args=args)
    ip = InitPub()
    rclpy.spin(ip)

main()

