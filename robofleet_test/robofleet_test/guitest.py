import sys
import math
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore
import cv2

image_path = "golisano3hi.png"

img = cv2.imread(image_path)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

height, width, _ = img.shape

resolution = 0.388
origin_x = 0.0
origin_y = 0.0


def ros_to_pixel(ros_x, ros_y):
    pixel_x = (ros_x - origin_x) / resolution
    pixel_y = height - ((ros_y - origin_y) / resolution)
    return pixel_x, pixel_y


app = QtWidgets.QApplication(sys.argv)

main_win = QtWidgets.QMainWindow()
main_win.setWindowTitle("Map Coordinate Test Viewer")

central_widget = QtWidgets.QWidget()
main_win.setCentralWidget(central_widget)

layout = QtWidgets.QHBoxLayout()
central_widget.setLayout(layout)

# ---------------- LEFT PANEL ----------------
info_panel = QtWidgets.QWidget()
info_panel.setFixedWidth(360)

info_layout = QtWidgets.QVBoxLayout()
info_panel.setLayout(info_layout)

title_label = QtWidgets.QLabel("Map Coordinate Tester")
title_label.setStyleSheet("font-size: 18px; font-weight: bold;")

position_label = QtWidgets.QLabel()
debug_label = QtWidgets.QLabel()

zoom_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
zoom_slider.setMinimum(50)
zoom_slider.setMaximum(1000)
zoom_slider.setValue(300)

full_size_checkbox = QtWidgets.QCheckBox("Show full map")
full_size_checkbox.setChecked(True)

test_origin_button = QtWidgets.QPushButton("Test map point (0, 0)")
test_x_button = QtWidgets.QPushButton("Test map point (10, 0)")
test_y_button = QtWidgets.QPushButton("Test map point (0, 10)")
test_middle_button = QtWidgets.QPushButton("Test middle of map")
test_goal_button = QtWidgets.QPushButton("Test goal (90, 60)")
test_custom_button = QtWidgets.QPushButton("Test custom point")

info_layout.addWidget(title_label)
info_layout.addWidget(position_label)
info_layout.addWidget(debug_label)
info_layout.addWidget(QtWidgets.QLabel("Area shown around point"))
info_layout.addWidget(zoom_slider)
info_layout.addWidget(full_size_checkbox)
info_layout.addWidget(test_origin_button)
info_layout.addWidget(test_x_button)
info_layout.addWidget(test_y_button)
info_layout.addWidget(test_middle_button)
info_layout.addWidget(test_goal_button)
info_layout.addWidget(test_custom_button)
info_layout.addStretch()

layout.addWidget(info_panel)

# ---------------- RIGHT MAP ----------------
graph_widget = pg.GraphicsLayoutWidget()
layout.addWidget(graph_widget, stretch=1)

view = graph_widget.addViewBox()
view.setAspectLocked(True)

img_item = pg.ImageItem(img)
view.addItem(img_item)

marker = pg.ScatterPlotItem(
    size=16,
    brush=pg.mkBrush(255, 0, 0, 180),
    pen=pg.mkPen("r", width=2)
)

view.addItem(marker)

test_x = 500.0
test_y = 500.0


def update_map_view(px=None, py=None):
    if full_size_checkbox.isChecked():
        view.setRange(
            xRange=(0, width),
            yRange=(0, height),
            padding=0
        )
        zoom_slider.setEnabled(False)
    else:
        zoom_slider.setEnabled(True)

        if px is not None and py is not None:
            area = zoom_slider.value()
            view.setRange(
                xRange=(px - area, px + area),
                yRange=(py - area, py + area),
                padding=0
            )


def set_test_point(x, y):
    global test_x, test_y

    test_x = x
    test_y = y

    px, py = ros_to_pixel(test_x, test_y)

    marker.setData([px], [py])

    inside = 0 <= px <= width and 0 <= py <= height

    position_label.setText(
        f"Map Coordinate:\n"
        f"x = {test_x:.3f} m\n"
        f"y = {test_y:.3f} m\n\n"
        f"Pixel Coordinate:\n"
        f"x = {px:.1f} / width {width}\n"
        f"y = {py:.1f} / height {height}"
    )

    debug_label.setText(
        f"Inside image: {inside}\n"
        f"Resolution: {resolution}\n"
        f"Origin: ({origin_x}, {origin_y})"
    )

    update_map_view(px, py)


def test_origin():
    set_test_point(0.0, 0.0)


def test_x_axis():
    set_test_point(10.0, 0.0)


def test_y_axis():
    set_test_point(0.0, 10.0)


def test_middle():
    map_width_m = width * resolution
    map_height_m = height * resolution

    set_test_point(map_width_m / 2.0, map_height_m / 2.0)


def test_goal():
    set_test_point(90.0, 60.0)


def test_custom():
    set_test_point(test_x, test_y)


test_origin_button.clicked.connect(test_origin)
test_x_button.clicked.connect(test_x_axis)
test_y_button.clicked.connect(test_y_axis)
test_middle_button.clicked.connect(test_middle)
test_goal_button.clicked.connect(test_goal)
test_custom_button.clicked.connect(test_custom)

zoom_slider.valueChanged.connect(lambda: set_test_point(test_x, test_y))
full_size_checkbox.stateChanged.connect(lambda: set_test_point(test_x, test_y))

# Start at test_x/test_y instead of forcing origin
set_test_point(test_x, test_y)

main_win.resize(1500, 800)
main_win.show()

sys.exit(app.exec())

