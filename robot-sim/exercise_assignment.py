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

d_br = 1
""" float: distance for break """

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
        print("Distance from obstacle:", dist_scan[0])

        if dist_scan[0] >= 2*d_br:
            return True

        elif dist_scan[0] >= d_br:
            if dist_scan[1] > dist_scan[0]:
                turn(4, 1)
                return True
            elif dist_scan[5] > dist_scan[0]:
                turn(-4, 1)
                return True
            else:
                return True

        else:
            if dist_scan[1] >= d_br or dist_scan[5] >= d_br:
                if dist_scan[1] >= dist_scan[5]:
                    turn(4, 1)
                else:
                    turn(-4, 1)

            elif dist_scan[2] >= d_br or dist_scan[4] >= d_br:
                if dist_scan[2] >= dist_scan[4]:
                    turn(4, 2)
                else:
                    turn(-4, 2)

            elif dist_scan[3] >= d_br:
                turn(4, 4)

            else:
                turn(2, 1)

def scanSector(tokenList):
    dist_scan = 100*numpy.ones(6)
    sector = None
    for token in tokenList:

        if token.rot_y >= -30 and token.rot_y <= 30:
            sector = 0

        elif token.rot_y > 30 and token.rot_y <= 90:
            sector = 1

        elif token.rot_y > 90 and token.rot_y <= 150:
            sector = 2

        elif token.rot_y > 150 or token.rot_y < -150:
            sector = 3

        elif token.rot_y >= -150 and token.rot_y < -90:
            sector = 4

        elif token.rot_y >= -90 and token.rot_y < -30:
            sector = 5

        else:
            exit("No sector found")

        if token.info.marker_type is MARKER_TOKEN_GOLD:
            if token.dist < dist_scan[sector]:
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



