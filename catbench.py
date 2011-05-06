#!/usr/bin/env python2

import sys
import argparse
import time
import datetime
import subprocess
import re
import math
import threading
import socket
import pickle
import atexit
import cmd
import stats

nw = datetime.datetime.now().isoformat(" ")

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--output", dest="outfile", default="test.csv")
    parser.add_argument("--title", dest="title", default=nw)
    parser.add_argument("--config", dest="config", default="ab")
    parser.add_argument("--tests", type=int, dest="tests", default=1)
    parser.add_argument("--duration", type=int, dest="duration", default=60)
    parser.add_argument("--min", type=int, dest="speed_min", default=100)
    parser.add_argument("--max", type=int, dest="speed_max", default=500)
    parser.add_argument("--step", type=int, dest="speed_step", default=50)
    parser.add_argument("--coding", dest="coding", default="enabled")
    parser.add_argument("--interval", type=int, dest="interval", default=1)
    args = parser.parse_args()

    if args.config == "ab":
        import ab as setup
        atexit.register(setup.stop_slaves)
    else:
        print("Invalid setup")
        sys.exit(-1)

    # Configure slaves and nodes
    print("Starting slaves")
    signal = threading.Event()
    setup.start_slaves()
    print("Starting nodes")
    setup.start_nodes(args.coding)
    setup.prepare_slaves(signal)

    print("Starting stats")
    stat_signal = threading.Event()
    stat_file = "stats_{}".format(args.outfile)
    stats.create(setup.nodes, args.interval, stat_signal, stat_file)

    try:
        f = open(args.outfile, "w")
        f.write("# CATWOMAN bench\n")
        f.write("# Test started {}\n".format(nw))
        f.write("# Title: {}\n".format(args.title))
    except:
        print("Failed to open {}".format(args.outfile))

    print
    print("Testing from {} to {} kb/s in {} kb/s steps".format(args.speed_min, args.speed_max, args.speed_step))
    print("{} tests per speed, duration is {} s, coding is {}".format(args.tests, args.duration, args.coding))
    print

    start = time.time()
    speeds = range(args.speed_min, args.speed_max+args.speed_step, args.speed_step)
    for i in range(len(speeds)):
        speed = speeds[i]
        print("############ {} kbps ############".format(speed))
        # Start tests
        setup.configure_slaves(speed, args.duration)

        for test in range(args.tests):
            # Record stats from each node
            stats.configure(speed, test)
            stat_signal.set()

            # Start iperf on all slaves
            signal.set()
            signal.clear()

            # Wait for iperf to finish
            ret = setup.wait_slaves()

            # Stop recording stats
            stat_signal.clear()
            stats.write()

            if not ret:
                print("Slave failed")
                return

            res = setup.result_slaves()

            for r in res:
                r["test"] = test
                r["test_speed"] = speed
                print("{speed} kb/s | {delay} ms | {lost}/{total} ({pl}%)".format(**r))
                f.write("{slave},{test_speed},{test},{speed},{delay},{lost},{total},{pl}\n".format(**r))
                f.flush()

            print
            # Restart iperf server to avoid time skew
            setup.restart_iperf_slaves()

    end = time.time()
    print("Test finished in {} seconds".format(math.floor(end-start)))
    print
    print
    f.close()

if __name__ == "__main__":
    main()
