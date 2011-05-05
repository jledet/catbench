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

nw = datetime.datetime.now().isoformat(" ")

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--output", dest="outfile", default="test.csv")
    parser.add_argument("--title", dest="title", default=nw)
    parser.add_argument("--config", dest="config", default="alice")
    parser.add_argument("--tests", type=int, dest="tests", default=1)
    parser.add_argument("--duration", type=int, dest="duration", default=60)
    parser.add_argument("--min", type=int, dest="speed_min", default=100)
    parser.add_argument("--max", type=int, dest="speed_max", default=500)
    parser.add_argument("--step", type=int, dest="speed_step", default=50)
    args = parser.parse_args()

    if args.config == "alice":
        import ab as setup
        atexit.register(setup.stop_slaves)
    else:
        print("Invalid setup")
        sys.exit(-1)

    # Configure slaves and nodes
    signal = threading.Event()
    setup.start_slaves()
    #setup.start_nodes()
    setup.prepare_slaves(signal)

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
        # Start tests
        setup.configure_slaves(speed, args.duration)
        
        for test in range(args.tests):
            signal.set()
            signal.clear()
            setup.wait_slaves()

            res = setup.result_slaves()
            
            for r in res:
                r["test"] = test
                print("{speed} kb/s | {delay} ms | {lost}/{total} ({pl}%)".format(**r))
                f.write("{slave},{test},{speed},{delay},{lost},{total},{pl}\n".format(**r))

    end = time.time()
    print("Test finished in {} seconds".format(math.floor(end-start)))
    f.close()

if __name__ == "__main__":
    main()
