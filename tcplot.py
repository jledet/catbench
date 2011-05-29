#!/usr/bin/env python2

import sys
import numpy as np
from matplotlib import pyplot

c = {
    "aluminium1":   "#eeeeec",
    "aluminium2":   "#d3d7cf",
    "aluminium3":   "#babdb6",
    "aluminium4":   "#888a85",
    "aluminium5":   "#555753",
    "aluminium6":   "#2e3436",
    "butter1":      "#fce94f",
    "butter2":      "#edd400",
    "butter3":      "#c4a000",
    "chameleon1":   "#8ae234",
    "chameleon2":   "#73d216",
    "chameleon3":   "#4e9a06",
    "chocolate1":   "#e9b96e",
    "chocolate2":   "#c17d11",
    "chocolate3":   "#8f5902",
    "orange1":      "#fcaf3e",
    "orange2":      "#f57900",
    "orange3":      "#ce5c00",
    "plum1":        "#ad7fa8",
    "plum2":        "#75507b",
    "plum3":        "#5c3566",
    "scarletred1":  "#ef2929",
    "scarletred2":  "#cc0000",
    "scarletred3":  "#a40000",
    "skyblue1":     "#729fcf",
    "skyblue2":     "#3465a4",
    "skyblue3":     "#204a87",
}

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
                'westwood': {
                    'alice': [],
                    'bob': []
                    },
                'veno': {
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
                'westwood': {
                    'alice': [],
                    'bob': []
                    },
                'veno': {
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
                'westwood': {
                    'alice': [],
                    'bob': []
                    },
                'veno': {
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
        elif "westwood" in line:
            control = "westwood"
        elif "veno" in line:
            control = "veno"

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

def errorbars(tests):
    return (np.std(tests, ddof=1)/np.sqrt(len(tests)))*2

def gain(a, b):
    mean = lambda z: np.mean([a[z], b[z]])
    tq = mean(0)
    random = mean(1)
    nocoding = mean(2)
    return tq/nocoding,random/nocoding

def plot_results_ab(results):
    bars_a_cubic = []
    bars_a_vegas = []
    bars_a_veno = []
    bars_a_ww = []
    bars_b_cubic = []
    bars_b_vegas = []
    bars_b_veno = []
    bars_b_ww = []
    errs_a_cubic = []
    errs_a_vegas = []
    errs_a_veno = []
    errs_a_ww = []
    errs_b_cubic = []
    errs_b_vegas = []
    errs_b_veno = []
    errs_b_ww = []
    labels = []

    node = 'alice'
    bars_a_vegas.append(np.mean(results['tq']['vegas'][node]))
    bars_a_cubic.append(np.mean(results['tq']['cubic'][node]))
    bars_a_veno.append(np.mean(results['tq']['veno'][node]))
    bars_a_ww.append(np.mean(results['tq']['westwood'][node]))
    bars_a_vegas.append(np.mean(results['random']['vegas'][node]))
    bars_a_cubic.append(np.mean(results['random']['cubic'][node]))
    bars_a_veno.append(np.mean(results['random']['veno'][node]))
    bars_a_ww.append(np.mean(results['random']['westwood'][node]))
    bars_a_vegas.append(np.mean(results['nocoding']['vegas'][node]))
    bars_a_cubic.append(np.mean(results['nocoding']['cubic'][node]))
    bars_a_veno.append(np.mean(results['nocoding']['veno'][node]))
    bars_a_ww.append(np.mean(results['nocoding']['westwood'][node]))
    errs_a_vegas.append(errorbars(results['tq']['vegas'][node]))
    errs_a_cubic.append(errorbars(results['tq']['cubic'][node]))
    errs_a_veno.append(errorbars(results['tq']['veno'][node]))
    errs_a_ww.append(errorbars(results['tq']['westwood'][node]))
    errs_a_vegas.append(errorbars(results['random']['vegas'][node]))
    errs_a_cubic.append(errorbars(results['random']['cubic'][node]))
    errs_a_veno.append(errorbars(results['random']['veno'][node]))
    errs_a_ww.append(errorbars(results['random']['westwood'][node]))
    errs_a_vegas.append(errorbars(results['nocoding']['vegas'][node]))
    errs_a_cubic.append(errorbars(results['nocoding']['cubic'][node]))
    errs_a_veno.append(errorbars(results['nocoding']['veno'][node]))
    errs_a_ww.append(errorbars(results['nocoding']['westwood'][node]))

    node = 'bob'
    bars_b_vegas.append(np.mean(results['tq']['vegas'][node]))
    bars_b_cubic.append(np.mean(results['tq']['cubic'][node]))
    bars_b_veno.append(np.mean(results['tq']['veno'][node]))
    bars_b_ww.append(np.mean(results['tq']['westwood'][node]))
    bars_b_vegas.append(np.mean(results['random']['vegas'][node]))
    bars_b_cubic.append(np.mean(results['random']['cubic'][node]))
    bars_b_veno.append(np.mean(results['random']['veno'][node]))
    bars_b_ww.append(np.mean(results['random']['westwood'][node]))
    bars_b_vegas.append(np.mean(results['nocoding']['vegas'][node]))
    bars_b_cubic.append(np.mean(results['nocoding']['cubic'][node]))
    bars_b_veno.append(np.mean(results['nocoding']['veno'][node]))
    bars_b_ww.append(np.mean(results['nocoding']['westwood'][node]))
    errs_b_vegas.append(errorbars(results['tq']['vegas'][node]))
    errs_b_cubic.append(errorbars(results['tq']['cubic'][node]))
    errs_b_veno.append(errorbars(results['tq']['veno'][node]))
    errs_b_ww.append(errorbars(results['tq']['westwood'][node]))
    errs_b_vegas.append(errorbars(results['random']['vegas'][node]))
    errs_b_cubic.append(errorbars(results['random']['cubic'][node]))
    errs_b_veno.append(errorbars(results['random']['veno'][node]))
    errs_b_ww.append(errorbars(results['random']['westwood'][node]))
    errs_b_vegas.append(errorbars(results['nocoding']['vegas'][node]))
    errs_b_cubic.append(errorbars(results['nocoding']['cubic'][node]))
    errs_b_veno.append(errorbars(results['nocoding']['veno'][node]))
    errs_b_ww.append(errorbars(results['nocoding']['westwood'][node]))

    labels.append("TQ Selection")
    labels.append("Weighted TQ Selection")
    labels.append("No Network Coding")

    xavegas = [2, 7, 12]
    xacubic = [1, 6, 11]
    xaww = [3, 8, 13]
    xaveno = [4, 9, 14]
    labels_x = [2.7,7.8,12.8]
    width = .4

    fig = pyplot.figure()
    ax = fig.add_subplot(1,1,1)
    ax.set_title("TCP Throughput with Unidirectional Flows")
    ax.set_ylabel("Throughput [kbit/s]")
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)
    pacubic = pyplot.bar(xacubic, bars_a_cubic, width, yerr=errs_a_cubic, color=c['skyblue2'], ecolor='black')
    pbcubic = pyplot.bar(np.array(xacubic)+width, bars_b_cubic, width, yerr=errs_b_cubic, color=c['skyblue3'], ecolor='black')

    pavegas = pyplot.bar(xavegas, bars_a_vegas, width, yerr=errs_a_vegas, color=c['chameleon2'], ecolor='black')
    pbvegas = pyplot.bar(np.array(xavegas)+width, bars_b_vegas, width, yerr=errs_b_vegas, color=c['chameleon3'], ecolor='black')

    paveno = pyplot.bar(xaveno, bars_a_veno, width, yerr=errs_a_veno, color=c['scarletred2'], ecolor='black')
    pbveno = pyplot.bar(np.array(xaveno)+width, bars_b_veno, width, yerr=errs_b_veno, color=c['scarletred3'], ecolor='black')

    paww = pyplot.bar(xaww, bars_a_ww, width, yerr=errs_a_ww, color=c['orange2'], ecolor='black')
    pbww = pyplot.bar(np.array(xaww)+width, bars_b_ww, width, yerr=errs_b_ww, color=c['orange3'], ecolor='black')

    print("                 TQ    Random")
    print("   Cubic gain:  {:4.2f}    {:4.2f}".format(*gain(bars_a_cubic, bars_b_cubic)))
    print("   Vegas gain:  {:4.2f}    {:4.2f}".format(*gain(bars_a_vegas, bars_b_vegas)))
    print("    Veno gain:  {:4.2f}    {:4.2f}".format(*gain(bars_a_veno, bars_b_veno)))
    print("Westwood gain:  {:4.2f}    {:4.2f}".format(*gain(bars_a_ww, bars_b_ww)))

    pyplot.xticks(labels_x, labels)
    pyplot.legend((pacubic[0],pavegas[0],paww[0],paveno), ('Cubic','Vegas','Westwood','Veno'), shadow=True, loc='lower right')


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: {} <in> [<out>]".format(sys.argv[0]))
        sys.exit(0)

    filename = sys.argv[1]
    results = parse_file(filename)
    plot_results_ab(results)
    #plot_results(results,'bob')
    #plot_diffs_ab(results)
    if len(sys.argv) > 2:
        pyplot.savefig(sys.argv[2], bbox_inches='tight', pad_inches=0.05)
    pyplot.show()
