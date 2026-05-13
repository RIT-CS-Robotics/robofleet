Individual robot startup:

* Make sure robot and lidar are plugged into laptop

* Make sure robot and laptop are unplugged from power

* Turn on the robot

* In a terminal run `ros2 launch robofleet_bringup robofleet.launch.xml`

* For now: `ros2 launch p3dx_navigation amcl_fleet.launch.xml`
** this will eventually get folded into the main bringup

Robot shutdown:

* Ctrl-C in the terminal

* Turn off robot

* Plug robot and laptop into power
