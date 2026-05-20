import sys
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore
import cv2

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped


image_path = "golisano3hi.png"

img = cv2.imread(image_path)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

height, width, _ = img.shape

# From your YAML file
resolution = 0.388
origin_x = 0.0
origin_y = 0.0


class BotPositionNode(Node):
    def __init__(self):
        super().__init__("bot_position_viewer")

        self.bot_x = 0.0
        self.bot_y = 0.0

        self.goal_x = None
        self.goal_y = None

        self.odom_sub = self.create_subscription(
            Odometry,
            "/rosaria/odom",   # change to "/odom" if needed
            self.odom_callback,
            10
        )

        self.goal_sub = self.create_subscription(
            PoseStamped,
            "/goal_pose",
            self.goal_callback,
            10
        )

    def odom_callback(self, msg):
        self.bot_x = msg.pose.pose.position.x
        self.bot_y = msg.pose.pose.position.y

    def goal_callback(self, msg):
        self.goal_x = msg.pose.position.x
        self.goal_y = msg.pose.position.y


def ros_to_pixel(ros_x, ros_y):
    pixel_x = (ros_x - origin_x) / resolution
    pixel_y = height - ((ros_y - origin_y) / resolution)
    return pixel_x, pixel_y


rclpy.init()
ros_node = BotPositionNode()

app = QtWidgets.QApplication(sys.argv)

main_win = QtWidgets.QMainWindow()
main_win.setWindowTitle("ROS2 Bot and Goal Map Viewer")

central_widget = QtWidgets.QWidget()
main_win.setCentralWidget(central_widget)

layout = QtWidgets.QHBoxLayout()
central_widget.setLayout(layout)

# ---------------- LEFT INFO PANEL ----------------
info_panel = QtWidgets.QWidget()
info_layout = QtWidgets.QVBoxLayout()
info_panel.setLayout(info_layout)

title_label = QtWidgets.QLabel("Current Run Information")
title_label.setStyleSheet("font-size: 18px; font-weight: bold;")

bot_position_label = QtWidgets.QLabel()
goal_position_label = QtWidgets.QLabel()
zoom_label = QtWidgets.QLabel()

zoom_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
zoom_slider.setMinimum(50)
zoom_slider.setMaximum(1000)
zoom_slider.setValue(300)

info_layout.addWidget(title_label)
info_layout.addWidget(bot_position_label)
info_layout.addWidget(goal_position_label)
info_layout.addWidget(zoom_label)
info_layout.addWidget(QtWidgets.QLabel("Area shown around bot"))
info_layout.addWidget(zoom_slider)
info_layout.addStretch()

layout.addWidget(info_panel, stretch=1)

# ---------------- RIGHT MAP PANEL ----------------
graph_widget = pg.GraphicsLayoutWidget()
layout.addWidget(graph_widget, stretch=1)

view = graph_widget.addViewBox()
view.setAspectLocked(True)

img_item = pg.ImageItem(img)
view.addItem(img_item)

# Bot marker
bot_marker = QtWidgets.QGraphicsEllipseItem(-5, -5, 10, 10)
bot_marker.setPen(pg.mkPen("r", width=0))
bot_marker.setBrush(pg.mkBrush(255, 0, 0, 120))
view.addItem(bot_marker)

# Goal marker
goal_marker = QtWidgets.QGraphicsEllipseItem(-7, -7, 14, 14)
goal_marker.setPen(pg.mkPen("g", width=2))
goal_marker.setBrush(pg.mkBrush(0, 255, 0, 120))
goal_marker.setVisible(False)
view.addItem(goal_marker)


def update_gui():
    rclpy.spin_once(ros_node, timeout_sec=0)

    bot_px, bot_py = ros_to_pixel(ros_node.bot_x, ros_node.bot_y)
    bot_marker.setPos(bot_px, bot_py)

    if ros_node.goal_x is not None and ros_node.goal_y is not None:
        goal_px, goal_py = ros_to_pixel(ros_node.goal_x, ros_node.goal_y)
        goal_marker.setPos(goal_px, goal_py)
        goal_marker.setVisible(True)

        goal_position_label.setText(
            f"Goal Position:\n"
            f"x = {ros_node.goal_x:.2f} m\n"
            f"y = {ros_node.goal_y:.2f} m\n\n"
            f"Goal Pixel:\n"
            f"x = {goal_px:.1f}\n"
            f"y = {goal_py:.1f}"
        )
    else:
        goal_position_label.setText("Goal Position:\nNo goal received yet")

    area = zoom_slider.value()

    view.setRange(
        xRange=(bot_px - area, bot_px + area),
        yRange=(bot_py - area, bot_py + area),
        padding=0
    )

    bot_position_label.setText(
        f"Bot Position:\n"
        f"x = {ros_node.bot_x:.2f} m\n"
        f"y = {ros_node.bot_y:.2f} m\n\n"
        f"Bot Pixel:\n"
        f"x = {bot_px:.1f}\n"
        f"y = {bot_py:.1f}"
    )

    zoom_label.setText(f"Area shown: {area}px")


timer = QtCore.QTimer()
timer.timeout.connect(update_gui)
timer.start(50)

main_win.resize(1200, 700)
main_win.show()

exit_code = app.exec()

ros_node.destroy_node()
rclpy.shutdown()

sys.exit(exit_code)