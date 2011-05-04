#!/usr/bin/env python2

import sys
import subprocess
import re

# Server host
server = "localhost"

# Iterations per test
tests = 2

# Length of each test in sec
tlength = 10

# kbps
speed_min  = 100
speed_max  = 500
speed_step = 50

# Output file
fname = "test.csv"

try:
    f = open(fname, "w")
except:
    print("Failed to open {}".format(fname))

for speed in range(speed_min, speed_max+speed_step, speed_step):
    print("###### SPEED {} kbps ######".format(speed))
    for test in range(0, tests):
	print("-- Test {} --".format(test))
	try:
	    output = subprocess.check_output(["iperf", "-c", server, "-u", "-d", "-b", "{}k".format(speed), "-t", str(tlength)])
	except:
	    print("Test failed!")
	    sys.exit(-1)
	else:
	    lines = filter(lambda x: re.search("\(.+%\)$", x), output.split("\n"))
	    if not len(lines) == 2:
		print("Incorrect output format")
		sys.exit(-1)
	    else:
		tx = lines[0].split()
		rx = lines[1].split()

		tx_speed = tx[6]
		tx_delay = tx[8]
		tx_lost  = tx[10].replace("/", "")
		tx_total = tx[11]
		tx_pl    = tx[12].replace("%", "").replace("(", "").replace(")", "")

		rx_speed = rx[6]
		rx_delay = rx[8]
		rx_lost  = rx[10].replace("/", "")
		rx_total = rx[11]
		rx_pl    = rx[12].replace("%", "").replace("(", "").replace(")", "")

		res = [str(test), str(speed), tx_speed, tx_delay, tx_lost, tx_total, tx_pl, rx_speed, rx_delay, rx_lost, rx_total, rx_pl]
		print(",".join(res))
		f.write(",".join(res)+"\n")
