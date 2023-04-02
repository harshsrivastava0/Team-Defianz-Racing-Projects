#!/usr/bin/env python3

import rospy
import math
from sensor_msgs.msg import LaserScan
from race.msg import pid_input

# Some useful variable declarations.
angle_range = 240	# Hokuyo 4LX has 240 degrees FoV for scan
forward_projection = 1.0	# distance (in m) that we project the car forward for correcting the error. You have to adjust this.
desired_distance = 0.8	# distance from the wall (in m). (defaults to right wall)
vel = 15 		# this vel variable is not really used here.
error = 0.0		# initialize the error
car_length = 0.50 # Traxxas Rally is 20 inches or 0.5 meters

# Handle to the publisher that will publish on the error topic, messages of the type 'pid_input'
pub = rospy.Publisher('/error', pid_input, queue_size=10)


def getRange(data,angle):
	# data: single message from topic /scan
    # angle: between -30 to 210 degrees, where 0 degrees is directly to the right, and 90 degrees is directly in front
    # Outputs length in meters to object with angle in lidar scan field of view
    # Make sure to take care of NaNs etc.
    #TODO: implement
	index = (30+angle)*(len(data.ranges)/240)
	index = int(index)
	return data.ranges[index]


def callback(data):
	global forward_projection
	theta = 45 # you need to try different values for theta
	a = getRange(data,theta) # obtain the ray distance for theta
	b = getRange(data,0)	# obtain the ray distance for 0 degrees (i.e. directly to the right of the car)
	c = getRange(data, 90)
	swing = math.radians(theta)

	## Your code goes here to determine the error as per the alrorithm 
	# Compute Alpha, AB, and CD..and finally the error.
	# TODO: implement
	Alpha = math.atan((a*(math.cos(swing)) - b)/a*math.sin(swing))
	AB = b*math.cos(Alpha)
	CD = AB + (forward_projection*math.sin(Alpha))
	error = desired_distance - CD


	msg = pid_input()	# An empty msg is created of the type pid_input
	# this is the error that you want to send to the PID for steering correction.
	msg.pid_error = error	
	msg.pid_vel = c	# sending the distance from the front wall via pid_vel
	
	pub.publish(msg)


if __name__ == '__main__':
	print("Hokuyo LIDAR node started")
	rospy.init_node('dist_finder',anonymous = True)
	# TODO: Make sure you are subscribing to the correct car_x/scan topic on your racecar
	rospy.Subscriber("/scan",LaserScan,callback)
	rospy.spin()
