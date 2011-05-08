#!/usr/bin/env python2

import sys
import argparse
import time
import datetime
import subprocess
import re
import math
import socket
import pickle
import atexit
import cmd
import stats
import cPickle as pickle

nw = datetime.datetime.now().isoformat(" ")

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--output", dest="outfile", default="test.csv")
    parser.add_argument("--title", dest="title", default=nw)
    parser.add_argument("--config", dest="config", default="ab")
    parser.add_argument("--tests", type=int, dest="tests", default=1)
    parser.add_argument("--duration", type=int, dest="duration", default=60)
    parser.add_argument("--min", type=int, dest="speed_min", default=200)
    parser.add_argument("--max", type=int, dest="speed_max", default=750)
    parser.add_argument("--step", type=int, dest="speed_step", default=50)
    parser.add_argument("--interval", type=int, dest="interval", default=1)
    parser.add_argument("--sleep", type=int, dest="sleep", default=10)
    args = parser.parse_args()

    if args.config == "ab":
        import ab as setup
        atexit.register(setup.stop_slaves)
    else:
        print("Invalid setup")
        sys.exit(-1)

    speeds = range(args.speed_min, args.speed_max+args.speed_step, args.speed_step)
    overhead = 8
    test_time = (args.duration + args.sleep + overhead)
    eta = test_time * args.tests * len(speeds) * 2

    start = time.time()
    iso_time = time.strftime("%H:%M:%S", time.localtime(start + eta))
    print("Testing from {} to {} kb/s in {} kb/s steps".format(args.speed_min, args.speed_max, args.speed_step))
    print("{} tests per speed, duration is {} s".format(args.tests, args.duration))
    print("ETA: {}".format(iso_time))
    print

    # Configure slaves and nodes
    setup.start_slaves()
    setup.prepare_slaves()

    stat_file = "stats_{}".format(args.outfile)
    stats.create(setup.nodes, args.interval, stat_file)

    output = prepare_output(setup.slaves, setup.nodes, speeds)
    atexit.register(save_output, output=output, filename=args.outfile)
    for i in range(len(speeds)):
        speed = speeds[i]
        # Start testing
        setup.configure_slaves(speed, args.duration, args.interval)

        for test in range(args.tests):
            # Run test with network coding
            while not run_test(setup, stats, output, True, speed, test, eta, args.sleep):
                pass
            eta -= test_time

            # Run test without network coding
            while not run_test(setup, stats, output, False, speed, test, eta, args.sleep):
                pass
            eta -= test_time

    end = time.time()
    print("Test finished in {} seconds".format(math.floor(end-start)))

def prepare_output(slaves, nodes, speeds):
    output = {
            'coding': {
                'slaves': {},
                'nodes': {}
                },
            'nocoding': {
                'slaves': {},
                'nodes': {}
                }
            }

    for slave in slaves:
        output['coding']['slaves'][slave.name] = {}
        output['nocoding']['slaves'][slave.name] = {}
        for speed in speeds:
            output['coding']['slaves'][slave.name][speed] = []
            output['nocoding']['slaves'][slave.name][speed] = []

    for node in nodes:
        output['coding']['nodes'][node.name] = {}
        output['nocoding']['nodes'][node.name] = {}
        for speed in speeds:
            output['coding']['nodes'][node.name][speed] = []
            output['nocoding']['nodes'][node.name][speed] = []


    return output

def append_output(output, coding, slave, speed, sample):
    c = 'coding' if coding else 'nocoding'
    output[c][slave.group][slave.name][speed].append(sample)

def save_output(output, filename):
    try:
        f = open(filename, 'wb')
        fn = filename
    except:
        print("Failed to open output file, saving to /tmp/backup.pickle")
        fn = "/tmp/backup.pickle"
        f = open(fn , 'wb')

    pickle.dump(output, f, pickle.HIGHEST_PROTOCOL)
    f.close()
    print("Data saved to {}".format(fn))

def run_test(setup, stats, output, coding, speed, test, eta, sleep):
    verb = "with" if coding else "without"
    iso_time = time.strftime("%H:%M:%S", time.gmtime(eta))
    print("# {} kbps test {} {} network coding (ETA: {})".format(speed, test, verb, iso_time))
    setup.set_coding_nodes(coding)

    # Record stats from each node
    stats.start(test)

    # Start iperf on all slaves
    setup.signal_slaves(test)

    # Wait for iperf to finish
    ret = setup.wait_slaves()

    # Stop recording stats
    stats.stop()

    # Restart iperf server to avoid time skew
    setup.restart_iperf_slaves()

    if not ret:
        return False

    if not setup.check_slave_times():
        print("Slave time differs; restarting")
        return False

    if not setup.check_node_paths(stats):
        # Sleep to let batman-adv restore links
        print("Direct path detected, sleeping {} seconds".format(sleep))
        time.sleep(sleep)
        return False

    res = stats.results()
    for r in res:
        node = r.pop(0)
        append_output(output, coding, node, speed, r)

    res = setup.result_slaves()
    for r in res:
        slave = r.pop('slave')
        append_output(output, coding, slave, speed, r)

    print
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
