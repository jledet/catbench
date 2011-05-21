#!/usr/bin/env python2

import sys
import numpy as np
from matplotlib import pyplot

nodes = {'10.10.0.8': 'bob', '10.10.0.9': 'alice'}

timestamp = 0
node1 = 1
port1 = 2
node2 = 3
port2 = 4
nodeid = 5
duration = 6
amount = 7
result = 8

def parse_file(filename):
    results = {
            'nocoding': {
                'vegas': {
                    'alice': [],
                    'bob': []
                    },
                'cubic': {
                    'alice': [],
                    'bob': []
                    },
                },
            'random': {
                'vegas': {
                    'alice': [],
                    'bob': []
                    },
                'cubic': {
                    'alice': [],
                    'bob': []
                    },
                },
            'tq': {
                'vegas': {
                    'alice': [],
                    'bob': []
                    },
                'cubic': {
                    'alice': [],
                    'bob': []
                    },
                }
            }

    f = open(filename)
    for line in f:
        # Toggle control algorithm
        if "vegas" in line:
            control = "vegas"
        elif "cubic" in line:
            control = "cubic"

        # Toggle random tq
        elif "tq" in line and "False" in line:
            tq = "tq"
        elif "tq" in line and "True" in line:
            tq = "random"

        # Toggle network coding
        elif "Coding" in line and "False" in line:
            tq = "nocoding"

        # Read results
        elif "," in line:
            node,throughput = parse_line(line)
            #print tq,control,node,throughput
            results[tq][control][node].append(int(throughput)/1000)

    return results

def parse_line(line):
    tokens = line.strip().split(',')
    if tokens[port1] == "5001":
        return nodes[tokens[node2]],tokens[result]
    elif tokens[port2] == "5001":
        return nodes[tokens[node1]],tokens[result]

def plot_results(results):
    bars_a = []
    bars_b = []
    labels = []

    bars_a.append(np.mean(results['tq']['vegas']['alice']))
    bars_b.append(np.mean(results['tq']['vegas']['bob']))

    bars_a.append(np.mean(results['tq']['cubic']['alice']))
    bars_b.append(np.mean(results['tq']['cubic']['bob']))
    labels.append("TQ Selection")

    bars_a.append(np.mean(results['random']['vegas']['alice']))
    bars_b.append(np.mean(results['random']['vegas']['bob']))

    bars_a.append(np.mean(results['random']['cubic']['alice']))
    bars_b.append(np.mean(results['random']['cubic']['bob']))
    labels.append("Random TQ Selection")

    bars_a.append(np.mean(results['nocoding']['vegas']['alice']))
    bars_b.append(np.mean(results['nocoding']['vegas']['bob']))

    bars_a.append(np.mean(results['nocoding']['cubic']['alice']))
    bars_b.append(np.mean(results['nocoding']['cubic']['bob']))
    labels.append("No Network Coding")

    x = [1,2, 4,5, 7,8]
    labels_x = [2,5,8]
    width = .75

    pyplot.figure()
    pa = pyplot.bar(x, bars_a, width, color='r')
    pb = pyplot.bar(x, bars_b, width, color='b', bottom=bars_a)
    pyplot.ylim(ymax=2500)
    pyplot.xticks(labels_x, labels)
    pyplot.legend((pa[0],pb[0]), ('Alice','Bob'))

def plot_diffs(results):
    bars = []
    labels = []

    bars.append(get_diff(results, 'tq', 'vegas'))
    bars.append(get_diff(results, 'tq', 'cubic'))
    labels.append("TQ")

    bars.append(get_diff(results, 'random', 'vegas'))
    bars.append(get_diff(results, 'random', 'cubic'))
    labels.append("Random")

    bars.append(get_diff(results, 'nocoding', 'vegas'))
    bars.append(get_diff(results, 'nocoding', 'cubic'))
    labels.append("No Coding")

    x = [1,2, 4,5, 7,8]
    lx = [2,5,8]
    width = .75

    pyplot.figure()
    pyplot.bar(x, bars, width)
    pyplot.xticks(lx, labels)

def get_diff(results, tq, control):
    alice = results[tq][control]['alice']
    bob = results[tq][control]['bob']
    diff = np.absolute(np.subtract(alice, bob))
    return np.mean(diff)

if __name__ == "__main__":
    filename = sys.argv[1]
    results = parse_file(filename)
    plot_results(results)
    plot_diffs(results)
    pyplot.show()
