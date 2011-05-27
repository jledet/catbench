#!/usr/bin/env python2

import cPickle as pickle
import sys
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec

colors = ["#f57900", "#a40000", "#3465a4"]

def color():
    return colors.pop()

def end_nodes(data):
    nodes = []
    for node in data['coding']['nodes']:
        if node in data['coding']['slaves']:
            nodes.append(node)

    return nodes

def speeds(data, node):
    speeds = []
    for speed in data['coding']['nodes'][node]:
        speeds.append(speed)

    return sorted(speeds)

def tests(data, node, speed):
    tests = []
    for test in data['coding']['nodes'][node][speed]:
        tests.append(test)

    return tests

def read_field(test, field):
        return test[-1][field]

def plot(node, speeds, meas):
    plt.plot(speeds, meas, label=node, linewidth=2, color=color())

def bar(node, speeds, meas, btm=None):
    if not btm:
        btm = [0]*len(speeds)
    w = (speeds[1] - speeds[0])*0.33
    speeds = np.array(speeds) - w
    return plt.bar(speeds, meas, width=w, bottom=btm, color=color())[0]

def avg(data, node, field):
    speed_meas = []
    speed_rates = []
    for speed in speeds(data, node):
        test_meas = []
        for test in tests(data, node, speed):
            test_meas.append(read_field(test, field))
        speed_meas.append(np.mean(test_meas))
        speed_rates.append(int(speed))
    return speed_rates,speed_meas

def avg_nodes(data):
    fig = plt.figure()
    gs = gridspec.GridSpec(2, 1, height_ratios=[2,1])
    a1 = fig.add_subplot(gs[0])

    s,m = avg(data, 'relay', 'coded_x')
    s.insert(0,0), m.insert(0,0)
    plot('Coded (Relay)', s, m)
    plt.legend()
    a1.grid(True)
    a1.set_title("Decoding Failures Compared to Coded Packets")
    a1.set_xlabel("Offered Load [kbit/s]")
    a1.set_ylabel("Packets")

    a2 = fig.add_subplot(gs[1])
    a2.set_xlabel("Offered Load [kbit/s]")
    a2.set_ylabel("Packets")
    a2.yaxis.grid(True)
    btm = None
    bars = []
    for node in end_nodes(data):
        s,m= avg(data, node, 'failed')
        bars.append(bar(node, s, m, btm))
        btm = m

    plt.legend(bars, map(lambda x: "Failed ({})".format(x.title()), end_nodes(data)))


def main():
    if len(sys.argv) < 2:
        print("usage: {} <in> [<out>]".format(sys.argv[0]))
        sys.exit(1)

    p = pickle.load(open(sys.argv[1], "rb"))
    data = p['data']
    avg_nodes(data)
    if len(sys.argv) > 2:
        plt.savefig(sys.argv[2], bbox_inches='tight', pad_inches=0.05)
    plt.show()

if __name__ == "__main__":
    main()
