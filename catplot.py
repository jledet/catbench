#!/usr/bin/env python2

import sys
import pylab
import argparse
import operator

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--without-nc", required=True, dest="without_nc")
parser.add_argument("--with-nc", required=True, dest="with_nc")
args = parser.parse_args()

legends = []
pylab.hold('on')

for filename in (args.with_nc, args.without_nc):
    title = "Unknown"
    meas = {}
    try:
        f = open(filename)
    except:
        print("Failed to open {}".format(f))
        sys.exit(-1)
    else:
        # Read in all measurements
        for line in f:
            if not line.startswith("#"):
                speed, test, tx_speed, tx_delay, tx_lost, tx_total, tx_pl, rx_speed, rx_delay, rx_lost, rx_total, rx_pl = line.split(",")
                if not speed in meas.keys(): meas[speed] = []
                meas[speed].append((test, tx_speed, tx_delay, tx_lost, tx_total, tx_pl, rx_speed, rx_delay, rx_lost, rx_total, rx_pl))
            elif "Title" in line:
                title = line.split(":")[1].strip()
                legends.append(title)

        y = []
        for i in meas.keys():
            j = map(lambda k: float(k[1]), meas[i])
            y.append(sum(j)/len(j))
        x = map(lambda l: int(l), meas.keys())
        x,y = zip(*sorted(zip(x,y)))
        if filename == args.with_nc:
            y_nc = y
        elif filename == args.without_nc:
            y_no_nc = y

coding_gain = map(operator.sub, y_nc, y_no_nc)
legends.append("Coding gain")
pylab.plot(x, y_nc, "g-", x, y_no_nc, "b-", x, coding_gain, "r-")
pylab.plot(x, x, "k--")
pylab.title("Transmit vs. Receive speed")
pylab.xlabel("Transmit speed [kb/s]")
pylab.ylabel("Receive speed [kb/s]")
pylab.legend(legends, loc='upper left', shadow=True, fancybox=True)
pylab.grid('on')
pylab.show()
