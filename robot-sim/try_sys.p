import sys
import time

for i in range(10):
	sys.stdout.write("\rObstacle in: {1}".format(i))
	sys.stdout.flush()
	time.sleep(0.5)