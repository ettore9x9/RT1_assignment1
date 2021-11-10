Python Robotics Simulator
================================

This is a simple, portable robot simulator developed by [Student Robotics](https://studentrobotics.org).
Some of the arenas and the exercises have been modified for the Research Track I course.

Installing and running
----------------------

The simulator requires a Python 2.7 installation, the [pygame](http://pygame.org/) library, [PyPyBox2D](https://pypi.python.org/pypi/pypybox2d/2.1-r331), and [PyYAML](https://pypi.python.org/pypi/PyYAML/).

Once the dependencies are installed, simply run the `test.py` script to test out the simulator.

Assignment
----------

You can run the program with:

```bash
$ python run.py ex_roam.py
```

The objective of the assignment is to make the robot wander in the circuit, avoiding obstacles (golden tokens) and moving behind itself the silver tokens found along its way.

To achieve this goal, five functions were developed:
* `searchRoad()`
* `findRoad(dist_scan)`
* `scanSectors(token_list)`
* `searchSilver()`
* `moveSilver()`

The robot can divide the surrounding space into sectors, and find the nearest obstacle in each one. The number of sectors is specified in the variable nsect (default value = 12); changing this parameter can compromise the operation. Sectors are numbered as shown:

<p align="center">
<img src="https://github.com/ettore9x9/RT1_assignment1/blob/master/robot-sim/sr/sectors.jpg" width=30% height=30%>
</p>

Meaning that sector 0 is always in front of the robot, while right-side sectors have negative numbers and left-side sectors positive ones.

The main code has the following flowchart:
 
<p align="center">
<img src="https://github.com/ettore9x9/RT1_assignment1/blob/master/robot-sim/sr/flowchart_main.jpg" width=50% height=50%>
</p>

### searchRoad ###

Let us focus on the function `searchRoad`. This function aims to search for a good orientation for the robot, choosing whether to turn it or not, depending on the distance from the obstacles in each sector.

Choices made:
* If an obstacle is found to be near in both sectors +1 and -1, i.e., the road is too narrow, it calls the function `findRoad`.
* Otherwise, provided that there are no obstacles in sector 0, it moves the robot further.
* Furthermore, to avoid the robot's side getting too close to an obstacle, `searchRoad` checks if sectors +1 or -1 are obstacle-free. If one of them is not, then it turns a little bit.
* If there is an obstacle in sector 0, the robot must turn to find a better way, so the `findRoad` function is called.

The `searchRoad` function has the following flowchart:

<p align="center">
<img src="https://github.com/ettore9x9/RT1_assignment1/blob/master/robot-sim/sr/flowchart_searchRoad.jpg" width=50% height=50%>
</p>

### findRoad ###

The function `findRoad` aims at finding an obstacle-free road to orient the robot that way. To do so, it looks both right-side (negative numbers) and left-side (positive numbers), symmetrically and sequentially, and stops when it finds the nearest obstacle-free sector.
Specifically, for each pair of sectors (e.g., +1 and -1), the function selects the one with the further obstacle and checks whether the obstacle's distance is acceptable. If so, the sector is considered obstacle-free. Otherwise, the search continues.

<p align="center">
<img src="https://github.com/ettore9x9/RT1_assignment1/blob/master/robot-sim/sr/findroad_image.jpg" width=60%>
</p>

### scanSectors ###

The `scanSector` function is used to search for the closest gold token in each sector. Its argument is the list of tokens provided by the `R.see` method, and it returns a float array in which the j-th element is the smallest distance from a golden token detected in the j-th sector.

### searchSilver ###

The function `searchSilver` aims to search for the closest silver token to make the robot collect it. First, it turns the robot, then it drives the robot near the silver token to finally grab it. Lastly, it calls the `moveSilver` function.

### moveSilver ###

The `moveSilver` function can move the grabbed silver token behind the robot, looking around for obstacles to decide if it's better to turn left or right. Thanks to this, it avoids the robot hurting obstacles during the turning operation.

<p align="center">
<img src="https://github.com/ettore9x9/RT1_assignment1/blob/master/robot-sim/sr/movesilver_image.jpg" width=60%>
</p>

In conclusion, this is the robot's behaviour:
<figure class="video_container">
    <video controls="true" allowfullscreen="true" poster="https://github.com/ettore9x9/RT1_assignment1/blob/master/robot-sim/sr/findroad_image.jpg">
        <source src="https://github.com/ettore9x9/RT1_assignment1/blob/master/robot-sim/sr/robot_behaviour.mp4" type="video/mp4">
    </video>
</figure>

Robot API
---------

The API for controlling a simulated robot is designed to be as similar as possible to the [SR API][sr-api].

### Motors ###

The simulated robot has two motors configured for skid steering, connected to a two-output [Motor Board](https://studentrobotics.org/docs/kit/motor_board). The left motor is connected to output `0` and the right motor to output `1`.

The Motor Board API is identical to [that of the SR API](https://studentrobotics.org/docs/programming/sr/motors/), except that motor boards cannot be addressed by serial number. So, to turn on the spot at one quarter of full power, one might write the following:

```python
R.motors[0].m0.power = 25
R.motors[0].m1.power = -25
```

### The Grabber ###

The robot is equipped with a grabber, capable of picking up a token which is in front of the robot and within 0.4 metres of the robot's centre. To pick up a token, call the `R.grab` method:

```python
success = R.grab()
```

The `R.grab` function returns `True` if a token was successfully picked up, or `False` otherwise. If the robot is already holding a token, it will throw an `AlreadyHoldingSomethingException`.

To drop the token, call the `R.release` method.

Cable-tie flails are not implemented.

### Vision ###

To help the robot find tokens and navigate, each token has markers stuck to it, as does each wall. The `R.see` method returns a list of all the markers the robot can see, as `Marker` objects. The robot can only see markers which it is facing towards.

Each `Marker` object has the following attributes:

* `info`: a `MarkerInfo` object describing the marker itself. Has the following attributes:
  * `code`: the numeric code of the marker.
  * `marker_type`: the type of object the marker is attached to (either `MARKER_TOKEN_GOLD`, `MARKER_TOKEN_SILVER` or `MARKER_ARENA`).
  * `offset`: offset of the numeric code of the marker from the lowest numbered marker of its type. For example, token number 3 has the code 43, but offset 3.
  * `size`: the size that the marker would be in the real game, for compatibility with the SR API.
* `centre`: the location of the marker in polar coordinates, as a `PolarCoord` object. Has the following attributes:
  * `length`: the distance from the centre of the robot to the object (in metres).
  * `rot_y`: rotation about the Y axis in degrees.
* `dist`: an alias for `centre.length`
* `res`: the value of the `res` parameter of `R.see`, for compatibility with the SR API.
* `rot_y`: an alias for `centre.rot_y`
* `timestamp`: the time at which the marker was seen (when `R.see` was called).

For example, the following code lists all of the markers the robot can see:

```python
markers = R.see()
print "I can see", len(markers), "markers:"

for m in markers:
    if m.info.marker_type in (MARKER_TOKEN_GOLD, MARKER_TOKEN_SILVER):
        print " - Token {0} is {1} metres away".format( m.info.offset, m.dist )
    elif m.info.marker_type == MARKER_ARENA:
        print " - Arena marker {0} is {1} metres away".format( m.info.offset, m.dist )
```

[sr-api]: https://studentrobotics.org/docs/programming/sr/

Possible improvements
------------

* Make the robot move more fluently.
* Make the robot turn exactly in the correct sector.
* Optimize the trajectory of the robot.
