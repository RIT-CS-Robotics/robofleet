Installation instructions:

* Be running Ubuntu 24.04

* Install ROS2 Jazzy (see [here](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html))

* Install Nav2 (see [here](https://docs.nav2.org/getting_started/index.html))

* Make a `ros2_ws` directory and clone this repo into it as `src`:

  `git clone https://github.com/RIT-CS-Robotics/robofleet src`

* Run `colcon build`

* Don't forget to add these to the `.bashrc`

  `source /opt/ros/jazzy/setup.bash`
  `source ~/ros2_ws/install/local_setup.bash`

* Add the robofleet user to the `dialout` group so that it can talk to the robot: `sudo usermod -a -G dialout robofleet`
