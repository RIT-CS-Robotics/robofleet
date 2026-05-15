import math
import rclpy
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator
from tf_transformations import quaternion_from_euler

MAP_IMAGE = 'golisano3hi.png'

RESOLUTION = 0.0388

ORIGIN_X = 0.0
ORIGIN_Y = 0.0

clicked_points = []
current_point = None
navigation_started = False

image = mpimg.imread(MAP_IMAGE)

image_height = image.shape[0]

rclpy.init()

navigator = BasicNavigator()

print("Waiting for Nav2...")

navigator.waitUntilNav2Active()

print("Nav2 Active")

def onclick(event):
    global current_point

    if navigation_started:
        return

    if event.xdata is None or event.ydata is None:
        return

    px = event.xdata
    py = event.ydata

    current_point = [px, py, 0.0, 0.0]

    idx = len(clicked_points)

    print(f"Waypoint {idx}: pixel ({px:.1f}, {py:.1f})")

    ax.plot(px, py, 'ro')

    ax.text(
        px,
        py,
        str(idx),
        color='white',
        fontsize=12
    )

    fig.canvas.draw()

def onrelease(event):
    global current_point
    global clicked_points

    if current_point is None:
        return

    if event.xdata is None or event.ydata is None:
        return

    dx = event.xdata
    dy = event.ydata

    current_point[2] = dx
    current_point[3] = dy

    clicked_points.append((current_point[0], current_point[1], current_point[2], current_point[3]))

def onkey(event):

    global navigation_started
    global clicked_points

    if event.key == 'enter':

        if len(clicked_points) == 0:
            print("No waypoints selected")
            return

        print("\nStarting Navigation")

        navigation_started = True

        goals = []

        for px, py, dx, dy in clicked_points:

            map_x = px * RESOLUTION + ORIGIN_X

            map_y = (
                (image_height - py) * RESOLUTION
                + ORIGIN_Y
            )

            print(
                f"Map coordinate: "
                f"({map_x:.2f}, {map_y:.2f})"
            )

            goal = PoseStamped()

            goal.header.frame_id = 'map'

            goal.header.stamp = (
                navigator.get_clock()
                .now()
                .to_msg()
            )

            goal.pose.position.x = map_x
            goal.pose.position.y = map_y
            
            diff_x = dx-px
            diff_y = dy-py
            if abs(diff_x) < 1e-6 and abs(diff_y) < 1e-6:
                angle = 0.0
            else:
                angle = math.atan2(diff_y, diff_x)
            # angle = math.atan2(diff_y, diff_x)

            qx, qy, qz, qw = quaternion_from_euler(0, 0, angle)

            goal.pose.orientation.x = qx
            goal.pose.orientation.y = qy
            goal.pose.orientation.z = qz
            goal.pose.orientation.w = qw

            goals.append(goal)

        navigator.followWaypoints(goals)

    elif event.key == 'c':
        global current_point
        current_point = None
        clicked_points.clear()
        ax.clear()
        ax.imshow(image)
        fig.canvas.draw()

        print("Waypoints cleared")

fig, ax = plt.subplots()

ax.imshow(image)

fig.canvas.mpl_connect(
    'button_press_event',
    onclick
)

fig.canvas.mpl_connect(
    'button_release_event',
    onrelease
)

fig.canvas.mpl_connect(
    'key_press_event',
    onkey
)

plt.ion()

while plt.fignum_exists(fig.number):

    plt.pause(0.1)

    rclpy.spin_once(navigator, timeout_sec=0.01)

    if navigation_started:

        if navigator.isTaskComplete():

            result = navigator.getResult()

            print(f"\nNavigation Result: {result}")

            navigation_started = False

rclpy.shutdown()
