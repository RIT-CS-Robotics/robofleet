import rclpy
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator

MAP_IMAGE = 'golisano3hi.png'

RESOLUTION = 0.0388

ORIGIN_X = 0.0
ORIGIN_Y = 0.0

clicked_points = []
navigation_started = False

image = mpimg.imread(MAP_IMAGE)

image_height = image.shape[0]

rclpy.init()

navigator = BasicNavigator()

print("Waiting for Nav2...")

navigator.waitUntilNav2Active()

print("Nav2 Active")

def onclick(event):

    global clicked_points

    if navigation_started:
        return

    if event.xdata is None or event.ydata is None:
        return

    px = event.xdata
    py = event.ydata

    clicked_points.append((px, py))

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

        for px, py in clicked_points:

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

            goal.pose.orientation.w = 1.0

            goals.append(goal)

        navigator.followWaypoints(goals)

    elif event.key == 'c':
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
