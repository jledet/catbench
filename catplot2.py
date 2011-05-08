#!/usr/bin/env python2
import numpy
import pylab
import argparse
import operator
import cPickle
import dummy

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

def avg_value(samples, coding, device, type, speed, field):
    s = samples[coding][type][device][speed]
    values = map(lambda vls: vls[-1][field] if type == "nodes" else vls[field], s)
    return numpy.mean(values)

def slaves_throughput(samples, coding, slave):
    sample = samples[coding]['slaves'][slave]
    speeds = sorted(sample.keys())
    throughputs = []
    for speed in speeds:
        avg = avg_value(samples, coding, slave, "slaves", speed, 'throughput')
        throughputs.append(avg)
    return speeds,throughputs

def nodes_forwarded_coded(samples, coding, node):
    sample = samples[coding]['nodes'][node]
    speeds = sorted(sample.keys())
    forwarded = []
    coded     = []
    for speed in speeds:
        avg_forwarded = avg_value(samples, coding, node, "nodes", speed, 'forwarded')
        avg_coded     = avg_value(samples, coding, node, "nodes", speed, 'coded')
        forwarded.append(avg_forwarded)
        coded.append(avg_coded)
    return speeds,forwarded,coded

def plot_slave_throughput(samples, slave):
    legends = []
    throughputs = {} 
    fig = pylab.figure()
    ax = fig.add_subplot(111)

    ax.set_xlabel("Transmit speed [kb/s]")
    ax.set_ylabel("Receive speed [kb/s]")
    ax.set_title("Node {} Throughput vs. Load".format(slave.title()))
    ax.grid('on')

    for coding in samples:
        speeds, throughputs[coding] = slaves_throughput(samples, coding, slave)
        legends.append("With Network Coding" if coding == "coding" else "Without Network Coding")
        ax.plot(speeds, throughputs[coding], linewidth=2)
    gain = numpy.array(throughputs['coding']) - numpy.array(throughputs['nocoding'])
    ax.plot(speeds, gain, linewidth=2)
    legends.append("Coding Gain")
    ax.legend(legends, loc='upper left', shadow=True)
    ax.plot(speeds, speeds, color="#000000", linestyle="--")

    return speeds, throughputs

def plot_total_throughputs(throughputs, speeds):
    # Calculate and plot average throughput
    agg = {}
    agg['coding']   = numpy.add.reduce(throughputs['coding'])
    agg['nocoding'] = numpy.add.reduce(throughputs['nocoding'])
    agg['gain']     = agg['coding'] - agg['nocoding']
    agg_speeds = numpy.array(speeds) * len(throughputs['coding'])

    fig = pylab.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel("Transmit speed [kb/s]")
    ax.set_ylabel("Receive speed [kb/s]")
    ax.set_title("Aggregated Throughput vs. Load")
    ax.grid('on')

    ax.plot(agg_speeds, agg['nocoding'], linewidth=2)
    ax.plot(agg_speeds, agg['coding'], linewidth=2)
    ax.plot(agg_speeds, agg['gain'], linewidth=2)
    ax.legend(("Without Network Coding", "With Network Coding", "Coding Gain"), loc='upper left', shadow=True)

    ax.plot(agg_speeds, agg_speeds, color="#000000", linestyle="--")

def plot_coding_forward(data, node):
    speeds,forwarded,coded = nodes_forwarded_coded(data, "coding", node)

    fig = pylab.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel("Transmit Speed [kb/s]")
    ax.set_ylabel("Packets")
    ax.set_title("Packets Forwarded/Coded")
    ax.grid('on')
    ax.plot(speeds, forwarded, linewidth=2)
    ax.plot(speeds, coded, linewidth=2)
    ax.legend(("Forwarded", "Coded"), loc='upper left', shadow=True)

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--data", dest="data", default=None)
    parser.add_argument("--max", dest="max", default=0)
    args = parser.parse_args()

    # Read in pickled data
    if not args.data:
        data = dummy.dummy
    else:
        data = cPickle.load(open(args.data, "rb"))
        print("Unpickled {}".format(args.data))

    # Plot slave throughputs and aggregated throughtput
    throughput_agg = {'coding': [], 'nocoding': []}
    for slave in data['coding']['slaves']:
        speeds, throughputs = plot_slave_throughput(data, slave)
        for coding in data:
            throughput_agg[coding].append(throughputs[coding])
    plot_total_throughputs(throughput_agg, speeds)

    # Plot node forward/code counters
    for node in data['coding']['nodes']:
        if not node in data['coding']['slaves']:
            plot_coding_forward(data, node)

    pylab.show()

if __name__ == "__main__":
    main()
