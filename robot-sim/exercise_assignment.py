from __future__ import print_function

import time

import numpy

from sr.robot import *

"""

	When done, run with:
	$ python run.py solutions/exercise3_solution.py

"""


a_th = 2.0
""" float: Threshold for the control of the linear distance"""

d_th = 0.4
""" float: Threshold for the control of the orientation"""

R = Robot()
""" instance of the class Robot"""

d_br = 1.2
""" float: distance for break """

nsect = 12
# int: number of sectors in which I divide the space around me.
# It must be even to enshure simmetry.

def drive(speed, seconds):
    """
    Function for setting a linear velocity
    
    Args: speed (int): the speed of the wheels
	  seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

def turn(speed, seconds):
    """
    Function for setting an angular velocity
    
    Args: speed (int): the speed of the wheels
	  seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = -speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

def find_silver_token():
    """
    Function to find the closest silver token

    Returns:
	dist (float): distance of the closest silver token (-1 if no silver token is detected)
	rot_y (float): angle between the robot and the silver token (-1 if no silver token is detected)
    """
    dist=100
    for token in R.see():
        if token.dist < dist and token.info.marker_type is MARKER_TOKEN_SILVER:
            dist=token.dist
	    rot_y=token.rot_y
    if dist==100:
	   return -1, -1
    else:
   	    return dist, rot_y

def find_golden_token():
    """
    Function to find the closest golden token

    Returns:
    dist (float): distance of the closest golden token (-1 if no golden token is detected)
    rot_y (float): angle between the robot and the golden token (-1 if no golden token is detected)
    """
    dist=100
    for token in R.see():
        if token.dist < dist and token.info.marker_type is MARKER_TOKEN_GOLD:
            dist=token.dist
        rot_y=token.rot_y
    if dist==100:
       return -1, -1
    else:
        return dist, rot_y

def searchRoad():

    while (1):
        dist_scan = scanSector( R.see() )
        print("Obstacle in:", dist_scan[0], " m")

        if dist_scan[0] >= d_br:
            if dist_scan[1] <= d_br:
                print("Turn a little left...")
                turn(-4, 0.6)
            if dist_scan[-1] <= d_br:
                print("Turn a little right...")
                turn(4, 0.6)

            return True
        else:
            for j in range(nsect/2):
                if dist_scan[j] >= d_br:
                    print("Turn right...")
                    turn(4, 1.2)
                    return True
                if dist_scan[-j] >= d_br:
                    print("Turn left...")
                    turn(-4, 1.2)
                    return True


def scanSector(token_list):

    sector_angle = 360/nsect
    semisector = sector_angle/2
    dist_scan = 100*numpy.ones(nsect)

    for token in token_list:
        if token.rot_y >= 0:
            sector = int((token.rot_y + semisector)/sector_angle)
        else:
            sector = int((token.rot_y - semisector)/sector_angle)

        if token.info.marker_type is MARKER_TOKEN_GOLD and token.dist < dist_scan[sector]:
            dist_scan[sector] = token.dist

    return dist_scan

def moveSilver():

    print("Grabbed! Let's move it...")
    turn(30, 2)
    drive(20, 1)
    R.release()
    drive(-20, 1)
    turn(-30, 2)

def main():

    while(1):
        searchRoad()
        dist, rot_y = find_silver_token()
        if R.grab() is True:
            moveSilver()

        else:
            drive(20, 0.3)

main()