import sys
import math
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore
import cv2

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import LaserScan

import tf2_ros
from tf2_ros import TransformException


image_path = "golisano3hi.png"

img = cv2.imread(image_path)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

height, width, _ = img.shape

# From your YAML file
resolution = 0.388
origin_x = 0.0
origin_y = 0.0


class GuiListener(Node):
    def __init__(self):
        super().__init__("gui_listener")

        self.bot_x = 0.0
        self.bot_y = 0.0
        self.has_tf = False

        self.goal_x = None
        self.goal_y = None

        self.scan_x = []
        self.scan_y = []

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        self.goal_sub = self.create_subscription(
            PoseStamped,
            "/goal_pose",
            self.goal_callback,
            10
        )

        self.scan_sub = self.create_subscription(
            LaserScan,
            "/scan",
            self.scan_callback,
            10
        )

    def goal_callback(self, msg):
        self.goal_x = msg.pose.position.x
        self.goal_y = msg.pose.position.y

    def scan_callback(self, msg):
        xs = []
        ys = []

        angle = msg.angle_min

        for r in msg.ranges:
            if math.isfinite(r) and msg.range_min <= r <= msg.range_max:
                xs.append(r * math.cos(angle))
                ys.append(r * math.sin(angle))

            angle += msg.angle_increment

        self.scan_x = xs
        self.scan_y = ys

    def update_bot_pose_from_tf(self):
        try:
            transform = self.tf_buffer.lookup_transform(
                "map",
                "base_link",
                rclpy.time.Time()
            )

            self.bot_x = transform.transform.translation.x
            self.bot_y = transform.transform.translation.y
            self.has_tf = True

        except TransformException:
            self.has_tf = False


def ros_to_pixel(ros_x, ros_y):
    pixel_x = (ros_x - origin_x) / resolution
    pixel_y = (ros_y - origin_y) / resolution
    return pixel_x, pixel_y


rclpy.init()
ros_node = GuiListener()

app = QtWidgets.QApplication(sys.argv)

main_win = QtWidgets.QMainWindow()
main_win.setWindowTitle("ROS2 TF Bot, Goal, and Laser Scan Viewer")

central_widget = QtWidgets.QWidget()
main_win.setCentralWidget(central_widget)

layout = QtWidgets.QHBoxLayout()
central_widget.setLayout(layout)

# ---------------- LEFT INFO PANEL ----------------
info_panel = QtWidgets.QWidget()
info_panel.setFixedWidth(340)

info_layout = QtWidgets.QVBoxLayout()
info_panel.setLayout(info_layout)

title_label = QtWidgets.QLabel("Current Run Information")
title_label.setStyleSheet("font-size: 18px; font-weight: bold;")

bot_position_label = QtWidgets.QLabel()
goal_position_label = QtWidgets.QLabel()
tf_status_label = QtWidgets.QLabel()
zoom_label = QtWidgets.QLabel()

zoom_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
zoom_slider.setMinimum(50)
zoom_slider.setMaximum(1000)
zoom_slider.setValue(300)

full_size_checkbox = QtWidgets.QCheckBox("Show full map")

# Small laser scan plot
scan_plot = pg.PlotWidget()
scan_plot.setFixedHeight(220)
scan_plot.setAspectLocked(True)
scan_plot.showGrid(x=True, y=True)
scan_plot.setXRange(-5, 5)
scan_plot.setYRange(-5, 5)
scan_plot.setTitle("Laser Scan")

scan_points = scan_plot.plot(
    [],
    [],
    pen=None,
    symbol="o",
    symbolSize=3
)

info_layout.addWidget(title_label)
info_layout.addWidget(tf_status_label)
info_layout.addWidget(bot_position_label)
info_layout.addWidget(goal_position_label)
info_layout.addWidget(zoom_label)
info_layout.addWidget(QtWidgets.QLabel("Area shown around bot"))
info_layout.addWidget(zoom_slider)
info_layout.addWidget(full_size_checkbox)
info_layout.addWidget(scan_plot)
info_layout.addStretch()

layout.addWidget(info_panel)

# ---------------- RIGHT MAP PANEL ----------------
graph_widget = pg.GraphicsLayoutWidget()
layout.addWidget(graph_widget, stretch=1)

view = graph_widget.addViewBox()
view.setAspectLocked(True)

img_item = pg.ImageItem(img)
img_item.setRect(QtCore.QRectF(0, 0, width, height))

view.addItem(img_item)

view.invertY(True)

bot_marker = pg.ScatterPlotItem(
    size=14,
    brush=pg.mkBrush(255, 0, 0, 180),
    pen=pg.mkPen(None)
)

goal_marker = pg.ScatterPlotItem(
    size=14,
    brush=pg.mkBrush(0, 255, 0, 180),
    pen=pg.mkPen("g", width=2)
)

view.addItem(bot_marker)
view.addItem(goal_marker)

def update_map_view(bot_px=None, bot_py=None):
    if full_size_checkbox.isChecked():
        view.setRange(
            xRange=(0, width),
            yRange=(0, height),
            padding=0
        )
        zoom_slider.setEnabled(False)
        zoom_label.setText("View: full map")
    else:
        zoom_slider.setEnabled(True)

        if bot_px is not None and bot_py is not None:
            area = zoom_slider.value()

            view.setRange(
                xRange=(bot_px - area, bot_px + area),
                yRange=(bot_py - area, bot_py + area),
                padding=0
            )

            zoom_label.setText(f"Area shown: {area}px")


def update_gui():
    rclpy.spin_once(ros_node, timeout_sec=0)

    ros_node.update_bot_pose_from_tf()

    bot_px = None
    bot_py = None

    if ros_node.has_tf:
        tf_status_label.setText("TF Status: map → base_link received")

        bot_px, bot_py = ros_to_pixel(ros_node.bot_x, ros_node.bot_y)
        bot_marker.setData([bot_px], [bot_py])

        bot_position_label.setText(
            f"Bot TF Position in map frame:\n"
            f"x = {ros_node.bot_x:.3f} m\n"
            f"y = {ros_node.bot_y:.3f} m\n\n"
            f"Bot Pixel:\n"
            f"x = {bot_px:.1f}\n"
            f"y = {bot_py:.1f}"
        )
    else:
        tf_status_label.setText("TF Status: waiting for map → base_link")
        bot_position_label.setText("Bot TF Position:\nNo transform received yet")

    if ros_node.goal_x is not None and ros_node.goal_y is not None:
        goal_px, goal_py = ros_to_pixel(ros_node.goal_x, ros_node.goal_y)
        goal_marker.setData([goal_px], [goal_py])

        goal_position_label.setText(
            f"Goal Position:\n"
            f"x = {ros_node.goal_x:.3f} m\n"
            f"y = {ros_node.goal_y:.3f} m\n\n"
            f"Goal Pixel:\n"
            f"x = {goal_px:.1f}\n"
            f"y = {goal_py:.1f}"
        )
    else:
        goal_position_label.setText("Goal Position:\nNo goal received yet")

    scan_points.setData(ros_node.scan_x, ros_node.scan_y)

    update_map_view(bot_px, bot_py)


zoom_slider.valueChanged.connect(lambda: update_map_view())
full_size_checkbox.stateChanged.connect(lambda: update_map_view())

timer = QtCore.QTimer()
timer.timeout.connect(update_gui)
timer.start(50)

update_map_view()

main_win.resize(1500, 800)
main_win.show()

exit_code = app.exec()

ros_node.destroy_node()
rclpy.shutdown()

sys.exit(exit_code)
