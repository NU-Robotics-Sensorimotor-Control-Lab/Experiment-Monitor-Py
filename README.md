# Experiment-Monitor-Py

Internal Python Code to replace the C# .NET code used in May's setup at the Northwestern Robotics Sensorimotor Control Lab. Uses Pyglet for graphics. Accepts data over UDP, intended to be used in conjunction with the act4d Simulink model.

Creates circles describing the range and produced torques, and a line that shows the amount of force, like the C#/ .NET code

See Notes below for more details

## Notes:
EMonitorPyglet.py is the original EMonitor, and is an accurate port of the .NET code.
EMonitorPyglet_v2.py is a slightly altered EMonitor, and showes either images or a blank screen when in state zero. An altered ACT4D needs to be used, to transmit the current state
The images directory holds the images that may be displayed

## Bash Script
- The two bash scripts should serve to move into the correct environment and launch the file, to eliminate the need to open VS code. However, if the environment is altered, these will break. 

## Instructions
 1. Ensure that testingenv is running (contains the needed libraries)
 2. Run the Python code using the bash script or VS Code 
 3. Close the EMonitor with `esc` key
 4. Note the Ethernet IP printed out, and the port (port should be 5005)
 5. Check the connection IP address in the simulink model, and fill in the IP and port accordingly (IP:port)
 6. Run the EMonitor using the bash script or VS code again, and everything should work!
 7. Press `esc` when done to exit