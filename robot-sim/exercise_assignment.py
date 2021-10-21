from __future__ import print_function

import time

import numpy

from sr.robot import *

# Run with: $ python run.py exercise_assignment.py

a_th = 2.0 # float: Threshold for the control of the linear distance.

d_th = 0.4 # float: Threshold for the control of the orientation.

R = Robot() # Instance of the class Robot.

d_br = 1.2 # float: Alert distance for avoiding obstacles, distance break.

nsect = 12 #int: Number of sectors in which the space around the robot is divided.
# nsect Must be even to enshure simmetry.

def drive(speed, seconds):
    """
    Function for setting a linear velocity.
    
    Args: 
    speed (int): the speed of the wheels.
	seconds (int): the time interval.
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

def turn(speed, seconds):
    """
    Function for setting an angular velocity.
    
    Args:
    speed (int): the speed of the wheels.
	seconds (int): the time interval.
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = -speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

def find_silver_token():
    """
    Function to find the closest silver token.

    Returns:
	dist (float): distance of the closest silver token (-1 if no silver token is detected).
	rot_y (float): angle between the robot and the silver token (-1 if no silver token is detected).
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
    Function to find the closest golden token.

    Returns:
    dist (float): distance of the closest golden token (-1 if no golden token is detected).
    rot_y (float): angle between the robot and the golden token (-1 if no golden token is detected).
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
    """
    Function to search a good orientation for the robot, it returns when the robot is well aligned.

    """
    while (1):
        dist_scan = scanSector( R.see() ) # Calls the scanning function.

        # Prints the distance in [m] from the obstacle in sector 0 (front of the robot).
        print("Obstacle in:", dist_scan[0])

        if dist_scan[0] >= d_br: # The obstacle in sector 0 is far away, so the robot can go forward.

            # To avoid being too close to an obstacle with the side of the robot, checks if sector 1
            # and sector -1 (very near sectors of sector 0) are free from obstacles. If they are
            # not, then turns just a little bit.
            if dist_scan[1] <= d_br:
                print("Turn a little left...")
                turn(-4, 0.6)
            if dist_scan[-1] <= d_br:
                print("Turn a little right...")
                turn(4, 0.6)

            return True # The robot is well aligned!
            
        else: # There is an obstacle in front of the robot, it must turns to find a better way.

            # Finds the free-from-obstacles sector closest to sector 0.
            searching = 1
            for j in range(nsect/2):

                if dist_scan[-j] >= d_br: # First looks left.
                    print("Turn left...")
                    turn(-4, 1.2)
                    break # Starts again the while cycle.

                elif dist_scan[j] >= d_br: # Then looks right.
                    print("Turn right...")
                    turn(4, 1.2)
                    break # Starts again the while cycle.
                if j is nsect/2:
                    return False


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