# Soccer Robot
A robot that is able to play soccer. It will find a ball (of a certain colour) and move towards it. After it has caught up with it, it will look for a green circle and move towards that.

## Components
- Jetson Nano
- L298N DC motor controller
- 4 DC motors with wheels
- An acrylic base or something of the sort
- A jetson nano camera or webcam
- Jumper wires
- A power supply or power bank
- A cardboard holder for the ball
- A ball and some sort of box with a circle on it (serves as the net)

## Pinout
![image](https://user-images.githubusercontent.com/128321399/226220555-3bb9eb95-44c1-4fae-9193-90a4571caa8e.png)

## Files
There are 5 files in the repository:
- motor.py: library to control the 4 DC motors.
- wheels.py: the client for the PC to Jetson Nano communication (allows you to control the Nano from your PC). Use this program on the Nano.
- robot_control.py: the server for the PC to Jetson Nano communication (allows you to control the Nano from your PC). Use this program on the PC.
- ball_tracking_final.py: program to track the ball and move towards it.
- soccer_bot.py: program to track the ball and move towards it. Once it has caugth up with the ball, it will start moving towards a green circle (net).

## Credits

Made by Matteo Giovanni
