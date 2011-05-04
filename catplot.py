#!/usr/bin/env python2

import sys
import pylab

pylab.hold('on')

meas = {}

for filename in sys.argv[1:]:
    try:
        f = open(filename)
    except:
        print("Failed to open {}".format(f))
        sys.exit(-1)
    else:
        # Read in all measurements
        for line in f:
            if not line.startswith("#"):
                test, speed, tx_speed, tx_delay, tx_lost, tx_total, tx_pl, rx_speed, rx_delay, rx_lost, rx_total, rx_pl = line.split(",")
                if not speed in meas.keys():
                    meas[speed] = []
                meas[speed].append((test, tx_speed, tx_delay, tx_lost, tx_total, tx_pl, rx_speed, rx_delay, rx_lost, rx_total, rx_pl))

        y = []
        for i in meas.keys():
            j = map(lambda k: float(k[1]), meas[i])
            y.append(sum(j)/len(j))
        x = map(lambda l: int(l), meas.keys())
        x,y = zip(*sorted(zip(x,y)))
        pylab.plot(x, y)

pylab.title("Performance")
pylab.xlabel("Transmit speed [kb/s]")
pylab.ylabel("Receive speed [kb/s]")
pylab.grid('on')
pylab.show()
