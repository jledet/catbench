#!/usr/bin/env python2

import cPickle as pickle
import sys
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec

colors = {'alice': "#f57900", 'bob': "#cc0000", 'charlie': "#3465a4", 'dave': "#73d216"}
nodes = {
        'alice': '00:72:cf:28:19:1a',
        'bob': '00:72:cf:28:19:16',
        'charlie': '00:72:cf:28:19:a4',
        'dave': '00:72:cf:28:19:88',
        'relay': '00:72:cf:28:19:da',
        }

def end_nodes(data):
    nodes = []
    for node in data['coding']['nodes']:
        if node in data['coding']['slaves']:
            nodes.append(node)

    return sorted(nodes)

def speeds(data, coding, node):
    speeds = []
    for speed in data[coding]['nodes'][node]:
        speeds.append(speed)

    return sorted(speeds)

def tests(data, coding, node, speed):
    tests = []
    for test in data[coding]['nodes'][node][speed]:
        tests.append(test)

    return tests

def read_tq(test, nexthop):
    tqs = []
    for sample in test:
        tqs.append(int(sample['origs'][nexthop][1]))
    return np.mean(tqs)

def plot(node, speeds, meas):
    plt.plot(speeds, meas, label=node.title(), linewidth=2, color=colors[node])

def bar(node, speeds, meas, btm=None):
    if not btm:
        btm = [0]*len(speeds)
    w = (speeds[1] - speeds[0])*0.33
    speeds = np.array(speeds) - w
    return plt.bar(speeds, meas, width=w, bottom=btm, color=colors[node])[0]

def avg(data, coding, node, nexthop):
    out_speeds = []
    out_tqs = []
    for speed in speeds(data, coding, node):
        speed_tq = []
        for test in tests(data, coding, node, speed):
            speed_tq.append(read_tq(test, nexthop))
        out_tqs.append(np.mean(speed_tq))
        out_speeds.append(speed)

    return out_speeds,out_tqs

def avg_node(data, coding, node, nexthop, ingoing=True):
    if ingoing:
        s,t = avg(data, coding, node, nodes[nexthop])
    else:
        s,t = avg(data, coding, nexthop, nodes[node])
    s = np.array(s)*len(end_nodes(data))
    plot(nexthop, s, t)

def avg_nodes(data, coding):
    relay = 'relay'
    c = 'with coding' if coding == 'coding' else 'without coding'
    fig = plt.figure()
    gs = gridspec.GridSpec(3, 1, height_ratios=[.9,.1,.9])

    ax = fig.add_subplot(gs[0])
    ax.grid(True)
    ax.set_title('From nodes to {} {}'.format(relay, c))
    ax.set_xlabel("Offered load [kbit/s]")
    ax.set_ylabel("Link TQ (#/255)")
    ax.set_ylim(0,255)
    for node in end_nodes(data):
        avg_node(data, coding, relay, node, ingoing=True)

    leg = plt.legend(prop=dict(size=10), numpoints=1)
    #for t in leg.get_texts():
    #    t.set_fontsize('small')    # the legend text fontsize

    ax = fig.add_subplot(gs[2])
    ax.grid(True)
    ax.set_title('From {} to nodes {}'.format(relay, c))
    ax.set_xlabel("Offered load [kbit/s]")
    ax.set_ylabel("Link TQ (#/255)")
    ax.set_ylim(0,255)
    for node in end_nodes(data):
        avg_node(data, coding, relay, node, ingoing=False)

def main():
    if len(sys.argv) < 2:
        print("usage: {} <in> [<out>]".format(sys.argv[0]))
        sys.exit(1)

    p = pickle.load(open(sys.argv[1], "rb"))
    data = p['data']

    # With network coding
    avg_nodes(data, 'coding')
    if len(sys.argv) > 2:
        plt.savefig("coding_{}".format(sys.argv[2]), bbox_inches='tight', pad_inches=0.05)

    # Without network coding
    avg_nodes(data, 'nocoding')
    if len(sys.argv) > 2:
        plt.savefig("nocoding_{}".format(sys.argv[2]), bbox_inches='tight', pad_inches=0.05)
    plt.show()

if __name__ == "__main__":
    main()
