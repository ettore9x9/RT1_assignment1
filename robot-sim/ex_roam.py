from __future__ import print_function

import time

import sys

import numpy as np

from sr.robot import *

# Run with: $ python2 run.py ex_roam.py

a_th = 2.0 # float: Threshold for the control of the orientation.

d_th = 0.4 # float: Threshold for the control of the linear distance.

R = Robot() # Instance of the class Robot.

d_br = 1.2 # float: Alert distance for avoiding obstacles, distance break.

nsect = 12 # int: Number of sectors in which the space around the robot is divided.
# nsect Must be even to enshure simmetry.

sector_angle = 360/nsect # float: Angle of every sector.

semisector = sector_angle/2 # float: Semiangle of every sector.

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
    Function to search a good orientation for the robot.

    Returns:
    0 when the robot is well aligned,
    1 if the robot is not already aligned
    -1 if no free road is detected.

    """
    dist_scan = scanSectors( R.see() ) # Calls the scanning function.

    # Prints the distance in [m] from the obstacle in sector 0 (front of the robot).
    sys.stdout.write("\rObstacle in: {0}".format(round(dist_scan[0], 3)))
    sys.stdout.flush()

    if dist_scan[1] <= d_br and dist_scan[-1] <= d_br: # The robot is trapped, it finds another way.
        if findRoad(dist_scan) is True:
            return 1
        else:
            return -1 # No road found.


    elif dist_scan[0] >= d_br: # The obstacle in sector 0 is far away, so the robot can go forward.

        # To avoid the robot's side getting too close to an obstacle, searchRoad checks if sectors
        # +1 or -1 are obstacle-free. If one of them is not, then it turns a little bit.
        if dist_scan[1] <= d_br:
            turn(-10, 0.2)
        if dist_scan[-1] <= d_br:
            turn(10, 0.2)

        return 0 # The robot is well aligned!
        
    # There is an obstacle in front of the robot, it must turn to find a better way.
    elif findRoad (dist_scan) is True: 
        return 1

    return -1 # No road found.

def findRoad (dist_scan):
    """
    Function to turn the robot in order to find an obstacle-free road.

    Returns:
    True when it finds a good road.
    False when it doesn't find any road.

    """
    print("\n \nSearching a road...\n")
    for j in range(nsect/2 - 1): # Looks in all sectors without sector 0.

        if dist_scan[-j-1] >= 1.5*d_br and dist_scan[-j-1] >= dist_scan[j+1]: # First looks left.
            turn(-20, 0.2)
            return True

        elif dist_scan[j+1] >= 1.5*d_br and dist_scan[j+1] >= dist_scan[-j-1]: # Then looks right.
            turn(20, 0.2)
            return True

    return False # No road found.

def scanSectors(token_list):
    """
    Function to search for the closest gold token in each sector.

    Return:
    dist_scan: float array, every element j is the smallest distance from a golden token
               detected in j-th sector.
    """

    dist_scan = 100*np.ones(nsect) # Preallocates the array.

    for token in token_list:

        # Finds the correct sector for every token.
        if token.rot_y >= 0: # For positive sectors.
            sector = int((token.rot_y + semisector)/sector_angle)

        else: # For negative sectors.
            sector = int((token.rot_y - semisector)/sector_angle)

        # If it finds a closest token, than update the dist_scan array.
        if token.info.marker_type is MARKER_TOKEN_GOLD and token.dist < dist_scan[sector]:
            dist_scan[sector] = token.dist

    return dist_scan

def searchSilver():
    """
    Function to search the closest silver token and to make the robot moves close to it.

    Returns when the silver token is moved behind the robot whith the function moveSilver.
    """

    while (1):
        dist, rot_y = find_silver_token()

        #Writes distance from silver token on screen, refreshing the value.
        sys.stdout.write("\rSilver token in: {0}".format(round(dist, 3)))
        sys.stdout.flush()

        if rot_y < -a_th:
            turn(-2, 0.4)

        elif rot_y > a_th:
            turn(2, 0.4)

        elif dist > d_th: #The robot is well aligned, so it can approach the silver token.
            drive(20, 0.5)

        elif R.grab() == True: # Grabs the silver token.
            print("\n \nGrabbed! Let's move it...\n")
            moveSilver()
            return 0

        else: # The grabber did not work well, try again to approach the silver token.
            drive(-10, 0.5)
            turn(2,0.3)

def moveSilver():
    """
    Function to move the grabbed silver token, it decides if it's better to turn left or right.

    Returns when the silver token is moved behind the robot.
    """
    dist_scan = scanSectors( R.see() )
    min_dist_sector = 0
    min_val = 100

    # Finds the sector with the closest golden token, in order to turn on the other side.
    for j in range(nsect):
        if dist_scan[j] < min_val:
            min_val = dist_scan[j]
            min_dist_sector = j

    if min_dist_sector <= nsect/2: # The sector with the minimum distance is on the right.
        turn(-30, 2) # So turns on the left.
        drive(20, 1)
        R.release()
        drive(-20, 1)
        turn(30, 2)

    else: # The sector with the minimum distance is on the left.
        turn(30, 2) # So turns on the right.
        drive(20, 1)
        R.release()
        drive(-20, 1)
        turn(-30, 2)

def main():

    print("\n \n ### Let's start! ### \n \n")

    while(1):
        rf = searchRoad() # Road found
        if rf is 0: # There are no obstacles in front of the robot.
            dist, rot_y = find_silver_token() # Find the closest silver token.

            if abs(rot_y) <= 1.5*sector_angle and dist <= d_br: # If the silver token is in front of the robot.
                print("\n \nI see a silver token!\n \nApproaching...\n")
                searchSilver()

            else: # There's no silver token in front of the robot, it can go forward.
                drive(40, 0.5)

        elif rf is 1: # The road is not already found, so it explores a little bit
            drive(20, 0.2)

        else: # No road exists, so an error occours.
            print("No road found. Try to search with little sectors (increase nsect).")
            return -1

main()