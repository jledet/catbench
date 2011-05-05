#!/usr/bin/env python2

import sys
import argparse
import time
import datetime
import subprocess
import re
import math

nw = datetime.datetime.now().isoformat(" ")

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--output", dest="outfile", default="test.csv")
    parser.add_argument("--title", dest="title", default=nw)
    parser.add_argument("--host", dest="host", default="10.10.0.8")
    parser.add_argument("--tests", type=int, dest="tests", default=1)
    parser.add_argument("--duration", type=int, dest="duration", default=60)
    parser.add_argument("--min", type=int, dest="speed_min", default=100)
    parser.add_argument("--max", type=int, dest="speed_max", default=500)
    parser.add_argument("--step", type=int, dest="speed_step", default=50)
    args = parser.parse_args()

    try:
        f = open(args.outfile, "w")
        f.write("# CATWOMAN bench\n")
        f.write("# Test started {}\n".format(nw))
        f.write("# Title: {}\n".format(args.title))
    except:
        print("Failed to open {}".format(args.outfile))

    print("Testing from {} to {} kb/s in {} kb/s steps".format(args.speed_min, args.speed_max, args.speed_step))
    start = time.time()
    speeds = range(args.speed_min, args.speed_max+args.speed_step, args.speed_step)
    for i in range(len(speeds)):
        speed = speeds[i]
        print("############ {} kbps ############".format(speed))
        for test in range(args.tests):
            print("Test {}:".format(test))
            try:
                output = subprocess.check_output(["iperf", "-c", args.host, "-u", "-d", "-b", "{}k".format(speed), "-t", str(args.duration)])
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

                    res = [str(speed), str(test), tx_speed, tx_delay, tx_lost, tx_total, tx_pl, rx_speed, rx_delay, rx_lost, rx_total, rx_pl]
                    print(" TX: {} kb/s | {} ms | {}/{} ({}%)".format(tx_speed, tx_delay, tx_lost, tx_total, tx_pl))
                    print(" RX: {} kb/s | {} ms | {}/{} ({}%)".format(rx_speed, rx_delay, rx_lost, rx_total, rx_pl))
                    f.write(",".join(res)+"\n")

    end = time.time()
    print("Test finished in {} seconds".format(math.floor(end-start)))
    f.close()

if __name__ == "__main__":
    main()
