import sys
import cv2 as cv
import numpy as np
import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator


MAP_IMAGE = "golisano3hi.png"
RESOLUTION = 0.0388
ORIGIN_X = 0.0
ORIGIN_Y = 0.0


class Point:
    def __init__(self, point, name):
        self.x = point[0]
        self.y = point[1]
        self.name = name

    def get_coords(self):
        return self.x, self.y

    def set_coords(self, point):
        self.x = point[0]
        self.y = point[1]

    def get_name(self):
        return self.name

    def __repr__(self):
        return (f"{self.name} \t\t {self.x:.2f} {self.y:.2f}")


class PointDataset:

    def __init__(self, path):

        self.points = []

        self.lookup = {}

        self.load_points(path)

    def load_points(self, path):

        with open(path) as F:

            F.readline()

            for line in F:

                x, y, name = line.split()

                coords = (
                    int(x),
                    int(y)
                )

                point = Point(
                    coords,
                    name
                )

                self.lookup[name] = point

                self.points.append(point)

    def get_coords(self, print_points=True):

        coords = []

        for point in self.points:

            x, y = point.get_coords()

            coords.append([int(x), int(y)])

            if print_points:

                print(
                    f"{point.get_name()} : "
                    f"{point.get_coords()}"
                )

        return coords

    def apply_homography(self, H):

        coords = self.get_coords(
            print_points=False
        )

        coords = np.asarray(
            coords,
            dtype=np.float32
        )

        coords = coords.reshape(-1, 1, 2)

        transformed_coords = (
            cv.perspectiveTransform(
                coords,
                H
            )
        )

        for tc, point in zip(
            transformed_coords,
            self.points
        ):

            point.set_coords(tc[0])

    def pixel_to_map(self, px, py):

        image_height = cv.imread(
            MAP_IMAGE
        ).shape[0]

        map_x = (
            px * RESOLUTION
            + ORIGIN_X
        )

        map_y = (
            (image_height - py)
            * RESOLUTION
            + ORIGIN_Y
        )

        return map_x, map_y

    def print_real_world_coords(self):

        for point in self.points:

            px, py = point.get_coords()

            map_x, map_y = (
                self.pixel_to_map(px, py)
            )

            print(
                f"{point.get_name()} | "
                f"pixel=({px:.2f}, {py:.2f}) | "
                f"map=({map_x:.2f}, {map_y:.2f})"
            )


src_pts = np.array([
    [258.8, 592.8],
    [265.0, 760.0],
    [261.9, 930.3],
    [271.1, 1100.6],
    [268.0, 1267.8],
    [265.0, 1435.0],
    [261.9, 1608.3],
    [265.0, 1775.5],
    [258.8, 1948.9],
    [265.0, 2109.9],
    [1004.9, 589.7],
    [1008.0, 760.0],
    [995.6, 927.2],
    [1004.9, 1097.5],
    [1008.0, 1267.8],
    [1008.0, 1435.0],
    [1004.9, 1602.2],
    [1004.9, 1769.3],
    [1004.9, 1939.6]
], dtype=np.float32)

dst_pts = np.array([
    [1089.0, 2587.1],
    [1089.0, 2450.4],
    [1089.0, 2309.6],
    [1089.0, 2164.5],
    [1084.9, 2019.5],
    [1084.9, 1882.8],
    [1089.0, 1741.9],
    [1080.8, 1588.6],
    [1080.8, 1451.9],
    [1084.9, 1306.9],
    [1718.8, 2591.3],
    [1718.8, 2446.3],
    [1722.9, 2305.4],
    [1722.9, 2160.4],
    [1718.8, 2015.4],
    [1718.8, 1878.7],
    [1718.8, 1733.7],
    [1718.8, 1588.6],
    [1718.8, 1447.8]
], dtype=np.float32)

H, status = cv.findHomography(
    src_pts,
    dst_pts
)


class NavigatorController:

    def __init__(self):

        rclpy.init()

        self.navigator = BasicNavigator()

        print("\nWaiting for Nav2...")

        self.navigator.waitUntilNav2Active()

        print("Nav2 Active")

    def create_goal(self, x, y):

        goal = PoseStamped()

        goal.header.frame_id = "map"

        goal.header.stamp = (
            self.navigator.get_clock()
            .now()
            .to_msg()
        )

        goal.pose.position.x = float(x)

        goal.pose.position.y = float(y)

        goal.pose.orientation.w = 1.0

        return goal

    def follow_waypoints(self, goals):

        self.navigator.followWaypoints(
            goals
        )

    def wait_until_complete(self):

        while not self.navigator.isTaskComplete():

            rclpy.spin_once(
                self.navigator,
                timeout_sec=0.1
            )

        result = (
            self.navigator.getResult()
        )

        print(
            f"\nNavigation Result: "
            f"{result}"
        )

    def shutdown(self):

        rclpy.shutdown()


def main():

    pd = PointDataset("points.txt")

    pd.apply_homography(H)

    print("\nAvailable Locations:\n")

    pd.print_real_world_coords()

    requested_locations = sys.argv[1:]

    if len(requested_locations) == 0:

        print(
            "\nUsage:\n"
            "python3 main.py Office3509 Office3511"
        )

        return

    navigator_controller = (
        NavigatorController()
    )

    goals = []

    for name in requested_locations:

        if name not in pd.lookup:

            print(
                f"\nNo location named "
                f"{name}"
            )

            continue

        point = pd.lookup[name]

        px, py = point.get_coords()

        map_x, map_y = (
            pd.pixel_to_map(px, py)
        )

        print(
            f"\n{name}"
            f"\npixel = ({px:.2f}, {py:.2f})"
            f"\nmap    = ({map_x:.2f}, {map_y:.2f})"
        )

        goal = (
            navigator_controller
            .create_goal(
                map_x,
                map_y
            )
        )

        goals.append(goal)

    if len(goals) == 0:

        print("\nNo valid goals")

        navigator_controller.shutdown()

        return

    print("\nSending Waypoints...\n")

    navigator_controller.follow_waypoints(
        goals
    )

    navigator_controller.wait_until_complete()

    navigator_controller.shutdown()


if __name__ == "__main__":

    main()