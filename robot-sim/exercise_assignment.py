from __future__ import print_function

import time
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
        tokenList = R.see()
        if scanSector(0, tokenList) is True:
            print("Sector 0")
            return True

        elif scanSector(1, tokenList) is True:
            print("Sector 1")
            turn(-2, 1)

        elif scanSector(2, tokenList) is True:
            print("Sector 2")
            turn(-2, 2)

        elif scanSector(3, tokenList) is True:
            print("Sector 3")
            turn(-2, 4)

        elif scanSector(4, tokenList) is True:
            print("Sector 4")
            turn(2, 2)

        elif scanSector(5, tokenList) is True:
            print("Sector 5")
            turn(2, 1)

        else:
            exit("No road found")

def scanSector(sector_number, tokenList):
    print("Begin scanning sector", sector_number)
    dist = 100
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

        if sector is sector_number and token.info.marker_type is MARKER_TOKEN_GOLD:
            if token.dist < dist:
                dist = token.dist

    print(dist)

    if dist >= 0.75:
        return True

    else:
        return False


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



