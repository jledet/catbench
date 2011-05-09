#!/usr/bin/env python2
import sys
import numpy
import pylab
import argparse
import operator
import random
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

def get_slave_color(coding, err):
    if coding == "coding":
        return c['skyblue1'] if err else c['skyblue2']
    else:
        return c['chameleon1'] if err else c['chameleon2']
    #else:
    #    return c[random.choice(list(c.keys()))]


def values(samples, coding, device, type, speed, field):
    s = samples[coding][type][device][speed]
    if len(s) == 0:
        return None, None, None
    values = map(lambda vls: vls[-1][field] if type == "nodes" else vls[field], s)
    
    return numpy.mean(values),numpy.var(values),numpy.std(values)

def slaves_throughput(samples, coding, slave):
    sample = samples[coding]['slaves'][slave]
    speeds = sorted(sample.keys())
    speeds_out      = []
    throughputs_avg = []
    throughputs_var = []
    throughputs_std = []
    for speed in speeds:
        avg,var,std = values(samples, coding, slave, "slaves", speed, 'throughput')
        if avg == None:
            continue

        speeds_out.append(speed)
        throughputs_avg.append(avg)
        throughputs_var.append(var)
        throughputs_std.append(std)

    return speeds_out,throughputs_avg,throughputs_var,throughputs_std

def nodes_forwarded_coded(samples, coding, node):
    sample = samples[coding]['nodes'][node]
    speeds = sorted(sample.keys())
    speeds_out = []
    forwarded  = []
    coded      = []
    for speed in speeds:
        avg_forwarded,var_forwarded,std_forwarded = values(samples, coding, node, "nodes", speed, 'forwarded')
        if avg_forwarded == None:
            continue
        avg_coded,var_coded,std_coded             = values(samples, coding, node, "nodes", speed, 'coded')
        speeds_out.append(speed)
        forwarded.append(avg_forwarded)
        coded.append(avg_coded)
    return speeds_out,forwarded,coded

def plot_slave_throughput(samples, slave):
    throughputs_avg = {} 
    throughputs_var = {} 
    throughputs_std = {}
    fig = pylab.figure()
    ax = fig.add_subplot(111)

    ax.set_xlabel("Offered Load [kb/s]")
    ax.set_ylabel("Throughput [kb/s]")
    ax.set_title("Throughput vs. Offered Load for {}".format(slave.title()))

    for coding in samples:
        label = "With Network Coding" if coding == "coding" else "Without Network Coding"
        speeds, throughputs_avg[coding], throughputs_var[coding], throughputs_std[coding] = slaves_throughput(samples, coding, slave)
        ax.plot(speeds, throughputs_avg[coding], linewidth=2, label=label, color=get_slave_color(coding, False))
        ax.errorbar(speeds, throughputs_avg[coding], yerr=throughputs_std[coding], fmt=None, label='_nolegend_', ecolor=get_slave_color(coding, True))

    ax_gain = ax.twinx()
    gain = numpy.true_divide(numpy.array(throughputs_avg['coding']), numpy.array(throughputs_avg['nocoding'])) - 1
    ax_gain.plot(speeds, gain, linewidth=2, label="Coding Gain", color=c['scarletred2'])
    ax_gain.plot(speeds, [0]*len(speeds), "k")
    ax_gain.set_ylabel("Coding Gain")
    ax_gain.set_ylim(ymin=-0.10, ymax=1)
    
    ax.legend(loc='upper left', shadow=True)
    ax_gain.legend(loc='upper right', shadow=True)
    #ax.plot(speeds, speeds, color="#000000", linestyle="--")

    return speeds,throughputs_avg,throughputs_var,throughputs_std

def plot_total_throughputs(throughputs, speeds):
    # Calculate and plot average throughput
    agg = {}
    agg['coding']   = numpy.add.reduce(throughputs['coding'])
    agg['nocoding'] = numpy.add.reduce(throughputs['nocoding'])
    agg['gain']     = numpy.true_divide(agg['coding'], agg['nocoding']) - 1
    agg_speeds = numpy.array(speeds) * len(throughputs['coding'])

    fig = pylab.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel("Offered Load [kb/s]")
    ax.set_ylabel("Throughput [kb/s]")
    ax.set_title("Aggregated Throughput vs. Offered Load")

    ax.plot(agg_speeds, agg['nocoding'], linewidth=2, label="Without Network Coding", color=get_slave_color('nocoding', False))
    ax.plot(agg_speeds, agg['coding'], linewidth=2, label="With Network Coding", color=get_slave_color('coding', False))

    ax_gain = ax.twinx()
    ax_gain.plot(agg_speeds, agg['gain'], linewidth=2, label="Coding Gain", color=c['scarletred2'])
    ax_gain.plot(agg_speeds, [0]*len(agg_speeds), "k")
    ax_gain.set_ylabel("Coding Gain")
    ax_gain.set_ylim(ymin=-0.10, ymax=1)
    #ax.plot(agg_speeds, agg_speeds, color="#000000", linestyle="--")
    ax.legend(loc='upper left', shadow=True)

def plot_coding_forward(data, node):
    speeds,forwarded,coded = nodes_forwarded_coded(data, "coding", node)
    speeds = 2 * numpy.array(speeds)

    # Normalize
    total = numpy.add.reduce((forwarded, numpy.array(coded)*2))
    forwarded_norm = numpy.true_divide(forwarded, total)
    coded_norm = numpy.true_divide(coded, total)

    fig = pylab.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel("Offered Load [kb/s]")
    ax.set_ylabel("Packets Ratio")
    ax.set_title("Packets Forwarded/Coded")
    ax.plot(speeds, forwarded_norm, linewidth=2, color=c['chameleon2'])
    ax.plot(speeds, coded_norm, linewidth=2, color=c['skyblue2'])
    ax.legend(("Forwarded", "Coded"), loc='upper left', shadow=True)

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--data", dest="data", default=None)
    parser.add_argument("--max", dest="max", default=0)
    args = parser.parse_args()

    # Read in pickled data
    if not args.data:
        data = dummy.dummy['data']
        param = dummy.dummy['param']
    else:
        try:
            data = cPickle.load(open(args.data, "rb"))
            if 'data' in data:
                data = data['data']
        except Exception as e:
            print("Failed to unpickle {} ({})".format(args.data, e))
            sys.exit(1)

    # Plot slave throughputs and aggregated throughtput
    throughput_agg = {'coding': [], 'nocoding': []}
    for slave in data['coding']['slaves']:
        speeds, throughputs_avg, throughputs_var, throughputs_std = plot_slave_throughput(data, slave)
        for coding in data:
            throughput_agg[coding].append(throughputs_avg[coding])
    plot_total_throughputs(throughput_agg, speeds)

    # Plot node forward/code counters
    for node in data['coding']['nodes']:
        if not node in data['coding']['slaves']:
            plot_coding_forward(data, node)

    pylab.show()

if __name__ == "__main__":
    main()
