# robofleet
Code that runs on the fleet robots

To use this repo, it must be on a laptop with:
* ROS Jazzy with nav2
* RosAria2
* Pioneer P3DX drivers
and attached to one of our robots.

Other repos in the overall project are:
* robofleet-server for the server that displays robot status and allows people to upload code
* robofleet-api for the code that users build on to control robots

Eventual contents will include:
* Navigation code including maps of the building (visual and semantic)
* Listener/executor to get code from the server and run it
* Status monitor with GUI (to be seen on the robot's laptop)
* Reporter sending status back to the server (may be part of the monitor)
