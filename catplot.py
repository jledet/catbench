#!/usr/bin/env python2
import sys
import os
import os.path
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

figures = {}

def get_tx_color(field, coding):
    if coding == "coding":
        if field == "tx_short_retries":
            return c['skyblue1']
        elif field == "tx_long_retries":
            return c['plum3']
        else:
            return c['scarletred2']
    else:
        if field == "tx_short_retries":
            return c['chameleon2']
        elif field == "tx_long_retries":
            return c['aluminium4']
        else:
            return c['orange2']


def get_slave_color(coding, err):
    if coding == "coding":

        return c['skyblue1'] if err else c['skyblue2']
    else:
        return c['chameleon1'] if err else c['chameleon2']

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
        avg_coded,var_coded,std_coded = values(samples, coding, node, "nodes", speed, 'coded')
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
    ax.grid(True)

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
    
    figures['{}_tput'.format(slave)] = fig
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
    ax.grid(True)

    ax.plot(agg_speeds, agg['nocoding'], linewidth=2, label="Without Network Coding", color=get_slave_color('nocoding', False))
    ax.plot(agg_speeds, agg['coding'], linewidth=2, label="With Network Coding", color=get_slave_color('coding', False))

    ax_gain = ax.twinx()
    ax_gain.plot(agg_speeds, agg['gain'], linewidth=2, label="Coding Gain", color=c['scarletred2'])
    ax_gain.plot(agg_speeds, [0]*len(agg_speeds), "k")
    ax_gain.set_ylabel("Coding Gain")
    ax_gain.set_ylim(ymin=-0.10, ymax=1)
    ax.legend(loc='upper left', shadow=True)
    #ax.plot(agg_speeds, agg_speeds, color="#000000", linestyle="--")
   
    figures["agg_tput"] = fig

def plot_coding_forward(data, node):
    speeds,forwarded,coded = nodes_forwarded_coded(data, "coding", node)
    speeds = 2 * numpy.array(speeds)

    # Normalize
    total = numpy.add.reduce((forwarded, numpy.array(coded)*2))
    forwarded_norm = numpy.true_divide(forwarded, total)
    coded_norm = numpy.true_divide(coded, total)
    total_norm = forwarded_norm + coded_norm

    fig = pylab.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel("Offered Load [kb/s]")
    ax.set_ylabel("Packets Ratio")
    ax.set_title("Packets Forwarded/Coded")
    ax.grid(True)
    ax.plot(speeds, forwarded_norm, linewidth=2, color=c['chameleon2'])
    ax.plot(speeds, coded_norm, linewidth=2, color=c['skyblue2'])
    ax.plot(speeds, total_norm, linewidth=2, color=c['plum2'])
    ax.legend(("Forwarded", "Coded", "Total"), loc='upper left', shadow=True)

    figures["{}_fw_coded".format(node)] = fig

def plot_ath_stats(data, node):
    fig = pylab.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel("Offered Load [kbit/s]")
    ax.set_ylabel("Frames")
    ax.set_title("Frame Transmission Errors for {}".format(node.title()))
    ax.grid(True)
    
    fields = ['tx_failed', 'tx_short_retries', 'tx_long_retries']
    field_name = {'tx_failed': "Failed Transmissions", 'tx_short_retries': "RTS Retransmissions", 'tx_long_retries': "Frame Retransmission"}
    for field in fields:
        for coding in data:
            tx = {'tx_failed': [], 'tx_short_retries': [], 'tx_long_retries': []}
            label = field_name[field] + (" With Network Coding" if coding == "coding" else " Without Network Coding")
            sample = data[coding]['nodes'][node]
            speeds = sorted(sample.keys())
            for speed in speeds:
                stats = sample[speed]
                t  = map(lambda val: val[-1]['ath'][field] - val[0]['ath'][field], stats)
                tx[field].append(numpy.mean(t))
            ax.plot(speeds, tx[field], linewidth=2, label=label, color=get_tx_color(field, coding))
    ax.legend(loc='upper left', shadow=True)

    figures["{}_tx_err".format(node)] = fig

def plot_coding_queue(data, node):
    fig = pylab.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel("Offered Load [kbit/s]")
    ax.set_ylabel("Packets")
    ax.set_title("Hold Queue Length for {}".format(node.title()))
    ax.grid(True)

    for coding in data:
        label = "With Network Coding" if coding == "coding" else "Without Network Coding"
        sample = data[coding]['nodes'][node]
        speeds = sorted(sample.keys())
        queue_len = []
        for speed in speeds:
            v = values(data, coding, node, "nodes", speed, "coding packets")
            queue_len.append(numpy.mean(v))
        ax.plot(speeds, queue_len, linewidth=2, label=label, color=get_slave_color(coding, False))
    ax.legend(loc='upper left', shadow=True)

    figures["{}_coding_queue".format(node)] = fig

def plot_avg_delay(data, slave):
    fig = pylab.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel("Offered Load [kbit/s]")
    ax.set_ylabel("Delay [ms]")
    ax.set_title("Average Delay for {}".format(slave.title()))
    ax.grid(True)
    
    for coding in data:
        label = "With Network Coding" if coding == "coding" else "Without Network Coding"
        sample = data[coding]['slaves'][slave]
        speeds = sorted(sample.keys())
        avg_delay = []
        for speed in speeds:
            stats = sample[speed]
            ad = numpy.mean(map(lambda val: float(val['delay_avg']), stats))
            avg_delay.append(numpy.mean(ad))
        ax.plot(speeds, avg_delay, linewidth=2, label=label, color=get_slave_color(coding, False))
    ax.legend(loc='upper left', shadow=True)

    figures["{}_delay".format(slave)] = fig

def plot_node_cpu(data, node):
    fig = pylab.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel("Offered Load [kbit/s]")
    ax.set_ylabel("Total CPU Utilization [%]")
    ax.set_title("CPU Utilization for {}".format(node.title()))
    ax.grid(True)

    for coding in data:
        label = "With Network Coding" if coding == "coding" else "Without Network Coding"
        sample = data[coding]['nodes'][node]
        speeds = sorted(sample.keys())
        cpu = []
        for speed in speeds:
            cpu.append(numpy.mean(values(data, coding, node, "nodes", speed, "cpu")))
        ax.plot(speeds, cpu, linewidth=2, label=label, color=get_slave_color(coding, False))
    ax.legend(loc='upper left', shadow=True)

    figures["{}_cpu".format(node)] = fig

def main():
    parser = argparse.ArgumentParser(description="CATWOMAN test plotting tool.")
    parser.add_argument("--data", dest="data", default=None, help="Pickled data file. If no file is given, dummy data is used.")
    parser.add_argument("--max", dest="max", default=0, help="Maximum value of theoretical limit throughput line")
    parser.add_argument("--show", dest="show", action="store_true", help="Show generated plots")
    parser.add_argument("--out", dest="out", help="Output directory of figures")
    parser.add_argument("--no-out", dest="noout", action="store_true", help="Disable pdf generation")
    parser.add_argument("--no-throughput", dest="notput", action="store_true", help="Disable throughput plots")
    parser.add_argument("--no-ath-stats", dest="noath", action="store_true", help="Disable Atheros driver stats plots")
    parser.add_argument("--no-cpu", dest="nocpu", action="store_true", help="Disable CPU utilization plots")
    parser.add_argument("--no-queue", dest="noqueue", action="store_true", help="Disable Coding Queue plots")
    parser.add_argument("--no-forward", dest="noforward", action="store_true", help="Disable Coding/Forward plots")
    parser.add_argument("--no-delay", dest="nodelay", action="store_true", help="Disable Delay plots")
    args = parser.parse_args()

    # Read in pickled data
    if not args.data:
        data = dummy.dummy['data']
        param = dummy.dummy['param']
        outdir = None
    else:
        try:
            data = cPickle.load(open(args.data, "rb"))
            if 'data' in data:
                data = data['data']
        except Exception as e:
            print("Failed to unpickle {} ({})".format(args.data, e))
            sys.exit(1)
        else:
            if not args.noout:
                outdir = args.out if not args.out == None else os.path.dirname(args.data)
            else:
                outdir = None

    # Plot slave throughputs and aggregated throughtput
    throughput_agg = {'coding': [], 'nocoding': []}
    for slave in data['coding']['slaves']:
        if not args.nodelay:
            plot_avg_delay(data, slave)
        if not args.notput:
            speeds, throughputs_avg, throughputs_var, throughputs_std = plot_slave_throughput(data, slave)
            for coding in data:
                throughput_agg[coding].append(throughputs_avg[coding])
    if not args.notput:
        plot_total_throughputs(throughput_agg, speeds)

    # Plot node forward/code counters
    for node in data['coding']['nodes']:
        if not args.noath:
            plot_ath_stats(data, node)
        if not args.nocpu:
            plot_node_cpu(data, node)
        if not node in data['coding']['slaves']:
            if not args.noqueue:
                plot_coding_queue(data, node)
            if not args.noforward:
                plot_coding_forward(data, node)

    # Save figures to outdir
    if not outdir == None:
        test_name = os.path.basename(args.data).split(".pickle")[0]
        outdir = "{}/{}".format(outdir, test_name)
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        for figure in figures:
            figures[figure].savefig("{}/{}_{}.pdf".format(outdir, test_name, figure))

    # Show figures
    if args.show:
        pylab.show()

if __name__ == "__main__":
    main()
