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

def main():
    parser = argparse.ArgumentParser(description="CATWOMAN benchmark program.")
    parser.add_argument("--output", dest="outfile", default="test.pickle", help="Output test data to FILE", metavar="FILE")
    parser.add_argument("--config", dest="config", default="ab", help="Used configuration. Must be either 'ab' or 'x'")
    parser.add_argument("--tests", type=int, dest="tests", default=1, help="Number of test runs")
    parser.add_argument("--duration", type=int, dest="duration", default=60, help="Duration of each test in seconds")
    parser.add_argument("--min", type=int, dest="speed_min", default=200, help="Minimum speed to kbit/s test")
    parser.add_argument("--max", type=int, dest="speed_max", default=750, help="Maximum speed in kbit/s to test")
    parser.add_argument("--step", type=int, dest="speed_step", default=50, help="Speed steps in kbit/s")
    parser.add_argument("--interval", type=int, dest="interval", default=1, help="Probing interval in seconds for periodic stats")
    parser.add_argument("--sleep", type=int, dest="sleep", default=30, help="Sleep time between tests in seconds")
    parser.add_argument("--hold", type=str, dest="hold", default="30", help="Hold time when coding in ms")
    parser.add_argument("--disable-rts", action="store_false", dest="rts", default=True, help="Disbable IEEE 802.11 RTS/CTS")
    parser.add_argument("--rate", type=str, dest="rate", default="2", help="Wireless bitrate in Mbit/s. Use 'auto' for autoconfiguration")
    parser.add_argument("--penalty", type=str, dest="hop", default="250", help="The hop penalty for end-nodes. Relay nodes are set to zero.")
    args = parser.parse_args()

    if args.config == "ab":
        import ab as setup
        atexit.register(setup.stop_slaves)
    if args.config == "x":
        import x as setup
        atexit.register(setup.stop_slaves)
    else:
        print("Invalid setup")
        sys.exit(-1)

    speeds = range(args.speed_min, args.speed_max+args.speed_step, args.speed_step)
    overhead = 10
    test_time = (args.duration + overhead)
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
    setup.configure_nodes(args.hold, args.rts, args.rate, args.hop)

    stat_file = "stats_{}".format(args.outfile)
    stats.create(setup.nodes, args.interval, stat_file)
    atexit.register(stats.shutdown)

    output = prepare_output(setup.slaves, setup.nodes, speeds, args)
    atexit.register(save_output, output=output, filename=args.outfile)
    for test in range(args.tests):
        for i in range(len(speeds)):
            speed = speeds[i]
            setup.configure_slaves(speed, args.duration, args.interval)

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

def prepare_output(slaves, nodes, speeds, args):
    output = {'param': args, 'data': {}}
    output['data'] = {
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
        if not slave.flow:
            continue

        output['data']['coding']['slaves'][slave.name] = {}
        output['data']['nocoding']['slaves'][slave.name] = {}
        for speed in speeds:
            output['data']['coding']['slaves'][slave.name][speed] = []
            output['data']['nocoding']['slaves'][slave.name][speed] = []

    for node in nodes:
        output['data']['coding']['nodes'][node.name] = {}
        output['data']['nocoding']['nodes'][node.name] = {}
        for speed in speeds:
            output['data']['coding']['nodes'][node.name][speed] = []
            output['data']['nocoding']['nodes'][node.name][speed] = []


    return output

def append_output(output, coding, slave, speed, sample):
    c = 'coding' if coding else 'nocoding'
    output['data'][c][slave.group][slave.name][speed].append(sample)

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
    if not stats.stop():
        print("Direct path detected. Sleeping")
        time.sleep(sleep)
        return False

    # Restart iperf server to avoid time skew
    setup.restart_iperf_slaves()

    if not ret:
        return False

    if not setup.check_slave_times():
        print("Slave time differs; restarting")
        return False

    res = stats.results()
    for r in res:
        node = r[0]
        stat = r[1]
        append_output(output, coding, node, speed, stat)

    res = setup.result_slaves()
    for r in res:
        slave = r.pop('slave')
        append_output(output, coding, slave, speed, r)
        print("{:10s} {throughput:5.1f} kb/s | {jitter:4.1f} ms | {lost:4d}/{total:4d} ({pl:4.1f}%)".format(slave.name.title(), **r))

    print
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
