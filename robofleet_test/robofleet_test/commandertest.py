import rclpy
import threading
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator


class WaypointCollector(Node):

    def __init__(self):

        super().__init__('waypoint_collector')

        self.navigator = BasicNavigator()

        self.navigator.waitUntilNav2Active()

        self.goals = []

        self.subscription = self.create_subscription(

            PoseStamped,
            '/goal_pose',
            self.goal_callback,
            10
        )

        threading.Thread(
            target = self.wait_for_enter,
            daemon=True
        ).start()

        self.started = False

        self.get_logger().info(
            "Click goals in RViz using 2D Goal Pose"
        )

    def goal_callback(self, msg):

        self.goals.append(msg)

        self.get_logger().info(

            f"Stored waypoint #{len(self.goals)} "
            f"at "
            f"({msg.pose.position.x:.2f}, "
            f"{msg.pose.position.y:.2f})"
        )

    def wait_for_enter(self):
        input()
        if self.started:
            return
        self.navigator.followWaypoints(self.goals)
        while not self.navigator.isTaskComplete():
            feedback = self.navigator.getFeedback()
            # if feedback:
            #     self.get_logger().info("Navigating")
        self.get_logger().info(
            f"Result: {self.navigator.getResult()}"
        )


def main(args=None):

    rclpy.init(args=args)
    node = WaypointCollector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()