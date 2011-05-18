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
param = None

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

    # Some speeds don't contain data (e.g. if the benchmark is interrupted)
    if len(s) == 0:
        return None, None, None

    # Read the (last if node stats) sample for each test in the given speed
    values = map(lambda vls: vls[-1][field] if type == "nodes" else vls[field], s)

    return numpy.mean(values),numpy.var(values, ddof=1),numpy.std(values, ddof=1)

def read_slaves_throughput(samples, coding, slave):
    sample = samples[coding]['slaves'][slave]
    speeds = sorted(sample.keys())
    speeds_out      = []
    throughputs_avg = []
    throughputs_var = []
    throughputs_std = []

    # Read measurements for each speed
    for speed in speeds:
        avg,var,std = values(samples, coding, slave, "slaves", speed, 'throughput')
        if avg == None:
            continue

        # The speed contains measurements, so add data
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

    # Read measurements for each speed
    for speed in speeds:
        avg_forwarded,var_forwarded,std_forwarded = values(samples, coding, node, "nodes", speed, 'forwarded')
        if avg_forwarded == None:
            continue

        # The speed contains measurements, so read and add data
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
    ax.set_title("Throughput vs. Offered Load for {} (hold: {} ms)".format(slave.title(), param.hold))
    ax.grid(True)

    # Plot for with and without network coding enabled
    for coding in samples:
        # Read averaged measurements
        speeds, throughputs_avg[coding], throughputs_var[coding], throughputs_std[coding] = read_slaves_throughput(samples, coding, slave)
        label = "With Network Coding" if coding == "coding" else "Without Network Coding"
        ax.plot(speeds, throughputs_avg[coding], linewidth=2, label=label, color=get_slave_color(coding, False))
        ax.errorbar(speeds, throughputs_avg[coding], yerr=throughputs_std[coding], fmt=None, label='_nolegend_', ecolor=get_slave_color(coding, True))

    # Add coding gain to plot with y-axis to the right
    ax_gain = ax.twinx()
    gain = numpy.true_divide(numpy.array(throughputs_avg['coding']), numpy.array(throughputs_avg['nocoding'])) - 1
    gain_std = numpy.true_divide(numpy.sqrt(numpy.array(throughputs_var['coding']) + numpy.array(throughputs_var['nocoding'])), numpy.array(throughputs_avg['nocoding']))
    print(gain_std)
    ax_gain.plot(speeds, gain, linewidth=2, label="Coding Gain", color=c['scarletred2'])
    #ax_gain.errorbar(speeds, gain, yerr=gain_std, fmt=None, label='_nolegend_', ecolor=c['scarletred1'])
    ax_gain.plot(speeds, [0]*len(speeds), "k")
    ax_gain.set_ylabel("Coding Gain")
    ax_gain.set_ylim(ymin=-0.10, ymax=1)

    ax.legend(loc='upper left', shadow=True)
    ax_gain.legend(loc='upper right', shadow=True)

    # Add figure to list of created figures
    figures['{}_tput'.format(slave)] = fig
    return speeds,throughputs_avg,throughputs_var,throughputs_std

def plot_total_throughputs(throughputs, speeds):
    # Calculate and plot average throughput
    agg = {}
    agg['coding']   = numpy.add.reduce(throughputs['coding'])
    agg['nocoding'] = numpy.add.reduce(throughputs['nocoding'])
    agg['gain']     = numpy.true_divide(agg['coding'], agg['nocoding']) - 1
    agg_speeds = numpy.array(speeds) * len(throughputs['coding'])

    # Create and setup a new figure
    fig = pylab.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel("Offered Load [kb/s]")
    ax.set_ylabel("Throughput [kb/s]")
    ax.set_title("Aggregated Throughput vs. Offered Load (hold: {})".format(param.hold))
    ax.grid(True)

    # Plot data
    ax.plot(agg_speeds, agg['nocoding'], linewidth=2, label="Without Network Coding", color=get_slave_color('nocoding', False))
    ax.plot(agg_speeds, agg['coding'], linewidth=2, label="With Network Coding", color=get_slave_color('coding', False))

    # Add coding gain to plot with y-axis to the right
    ax_gain = ax.twinx()
    ax_gain.plot(agg_speeds, agg['gain'], linewidth=2, label="Coding Gain", color=c['scarletred2'])
    ax_gain.plot(agg_speeds, [0]*len(agg_speeds), "k")
    ax_gain.set_ylabel("Coding Gain")
    ax_gain.set_ylim(ymin=-0.10, ymax=1)
    ax.legend(loc='upper left', shadow=True)

    # Add figure to list of created figures
    figures["agg_tput"] = fig

def plot_total_delays(delays, speeds):
    # Create and setup a new figure
    fig = pylab.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel("Offered Load [kb/s]")
    ax.set_ylabel("Delay [ms]")
    ax.set_title("Average Delay vs. Offered Load (hold: {})".format(param.hold))
    ax.grid(True)

    # Calculate the average delay
    avg = {}
    for coding in delays:
        label = " With Network Coding" if coding == "coding" else " Without Network Coding"
        summed = numpy.add.reduce(delays[coding])
        avg = numpy.true_divide(summed, len(delays[coding]))
        ax.plot(speeds, avg, linewidth=2, label=label, color=get_slave_color(coding, False))

    # Add figure to list of created figures
    figures["avg_delay"] = fig

def plot_coding_forward(data, node):
    speeds,forwarded,coded = nodes_forwarded_coded(data, "coding", node)
    speeds = 2 * numpy.array(speeds)

    # Normalize
    total = numpy.add.reduce((forwarded, numpy.array(coded)*2))
    forwarded_norm = numpy.true_divide(forwarded, total)
    coded_norm = numpy.true_divide(coded, total)
    total_norm = forwarded_norm + coded_norm

    # Create and setup a new figure
    fig = pylab.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel("Offered Load [kb/s]")
    ax.set_ylabel("Packets Ratio")
    ax.set_title("Packets Forwarded/Coded (hold: {})".format(param.hold))
    ax.grid(True)

    # Plot data
    ax.plot(speeds, forwarded_norm, linewidth=2, color=c['chameleon2'])
    ax.plot(speeds, coded_norm, linewidth=2, color=c['skyblue2'])
    ax.plot(speeds, total_norm, linewidth=2, color=c['plum2'])
    ax.legend(("Forwarded", "Coded", "Total"), loc='upper left', shadow=True)

    # Add figure to list of created figures
    figures["{}_fw_coded".format(node)] = fig

def plot_ath_stats(data, node):
    # Create and setup a new figure
    fig = pylab.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel("Offered Load [kbit/s]")
    ax.set_ylabel("Frames")
    ax.set_title("Frame Transmission Errors for {} (hold: {})".format(node.title(), param.hold))
    ax.grid(True)

    # Fields to read from measurements
    #fields = ['tx_failed', 'tx_short_retries', 'tx_long_retries']
    fields = ['tx_short_retries', 'tx_long_retries']
    #field_name = {'tx_failed': "Failed Transmissions", 'tx_short_retries': "RTS Retransmissions", 'tx_long_retries': "Frame Retransmission"}
    field_name = {'tx_short_retries': "RTS Retransmissions", 'tx_long_retries': "Frame Retransmission"}

    # Read out each field and add to plot
    for field in fields:
        # Do it with and without network coding
        for coding in data:
            #tx = {'tx_failed': [], 'tx_short_retries': [], 'tx_long_retries': []}
            tx = {'tx_short_retries': [], 'tx_long_retries': []}
            label = field_name[field] + (" With Network Coding" if coding == "coding" else " Without Network Coding")
            sample = data[coding]['nodes'][node]
            speeds = sorted(sample.keys())

            # Read measurements for each speed
            for speed in speeds:
                stats = sample[speed]
                # Measurements are incremental, so we need the difference of first and last sample
                t  = map(lambda val: val[-1]['ath'][field] - val[0]['ath'][field], stats)
                tx[field].append(numpy.mean(t))

            ax.plot(speeds, tx[field], linewidth=2, label=label, color=get_tx_color(field, coding))

    ax.legend(loc='upper left', shadow=True)

    # Add figure to list of created figures
    figures["{}_tx_err".format(node)] = fig

    return speeds,tx

def plot_coding_queue(data, node):
    # Create and setup a new figure
    fig = pylab.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel("Offered Load [kbit/s]")
    ax.set_ylabel("Packets")
    ax.set_title("Hold Queue Length for {} (hold: {})".format(node.title(), param.hold))
    ax.grid(True)

    # Read data for with and without network coding
    for coding in data:
        label = "With Network Coding" if coding == "coding" else "Without Network Coding"
        sample = data[coding]['nodes'][node]
        speeds = sorted(sample.keys())
        queue_len = []

        # Read measurements for each speed
        for speed in speeds:
            v = values(data, coding, node, "nodes", speed, "coding packets")
            queue_len.append(numpy.mean(v))

        ax.plot(speeds, queue_len, linewidth=2, label=label, color=get_slave_color(coding, False))

    ax.legend(loc='upper left', shadow=True)

    # Add figure to list of created figures
    figures["{}_coding_queue".format(node)] = fig

def plot_avg_delay(data, slave):
    # Create and setup a new figure
    fig = pylab.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel("Offered Load [kbit/s]")
    ax.set_ylabel("Delay [ms]")
    ax.set_title("Average Delay for {} (hold: {})".format(slave.title(), param.hold))
    ax.grid(True)

    # Read data for with and without network coding
    delays = {}
    for coding in data:
        label = "With Network Coding" if coding == "coding" else "Without Network Coding"
        sample = data[coding]['slaves'][slave]
        speeds = sorted(sample.keys())
        avg_delay = []

        # Read measurements for each speed
        for speed in speeds:
            stats = sample[speed]
            ad = numpy.mean(map(lambda val: float(val['delay_avg']), stats))
            avg_delay.append(numpy.mean(ad))

        delays[coding] = avg_delay
        ax.plot(speeds, avg_delay, linewidth=2, label=label, color=get_slave_color(coding, False))

    ax.legend(loc='upper left', shadow=True)

    # Add figure to list of created figures
    figures["{}_delay".format(slave)] = fig

    return speeds,delays

def plot_node_cpu(data, node):
    # Create and setup a new figure
    fig = pylab.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel("Offered Load [kbit/s]")
    ax.set_ylabel("Total CPU Utilization [%]")
    ax.set_title("CPU Utilization for {} (hold: {})".format(node.title(), param.hold))
    ax.grid(True)

    # Read data for with and without network coding
    for coding in data:
        label = "With Network Coding" if coding == "coding" else "Without Network Coding"
        sample = data[coding]['nodes'][node]
        speeds = sorted(sample.keys())
        cpu = []

        # Read measurements for each speed
        for speed in speeds:
            cpu.append(numpy.mean(values(data, coding, node, "nodes", speed, "cpu")))

        ax.plot(speeds, cpu, linewidth=2, label=label, color=get_slave_color(coding, False))

    ax.legend(loc='upper left', shadow=True)

    # Add figure to list of created figures
    figures["{}_cpu".format(node)] = fig

def read_pickle(filename):
    try:
        p = cPickle.load(open(filename, "rb"))
        param = p['param']
        data = p['data']
    except Exception as e:
        print("Failed to unpickle {} ({})".format(filename, e))
        sys.exit(1)

    return param,data

def save_figs(outdir, filename):
    # Save figures to outdir
    test_name = os.path.basename(filename).split(".pickle")[0]
    outdir = "{}/{}".format(outdir, test_name)
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    for figure in figures:
        figures[figure].savefig("{}/{}_{}.pdf".format(outdir, test_name, figure))

def remove_figs(data, args):
    for slave in data['coding']['slaves']:
        if not args.tput:
            pylab.close(figures.pop("{}_tput".format(slave)))
        if not args.delay:
            pylab.close(figures.pop("{}_delay".format(slave)))

    for node in data['coding']['nodes']:
        if not args.cpu:
            pylab.close(figures.pop("{}_cpu".format(node)))

        #if not args.ath:
        #    pylab.close(figures.pop("{}_tx_err".format(node)))

        if not node in data['coding']['slaves']:
            if not args.queue:
                pylab.close(figures.pop("{}_coding_queue".format(node)))


def main():
    parser = argparse.ArgumentParser(description="CATWOMAN test plotting tool.")
    parser.add_argument("--data", dest="data", default=None, help="Pickled data file. If no file is given, dummy data is used.")
    parser.add_argument("--out", dest="out", help="Output directory of figures")
    parser.add_argument("--throughput", dest="tput", action="store_true", help="Show all throughput plots")
    parser.add_argument("--ath-stats", dest="ath", action="store_true", help="Show all Atheros driver stats plots")
    parser.add_argument("--cpu", dest="cpu", action="store_true", help="Show all CPU utilization plots")
    parser.add_argument("--queue", dest="queue", action="store_true", help="Show all Coding Queue plots")
    parser.add_argument("--delay", dest="delay", action="store_true", help="Show all Delay plots")
    #parser.add_argument("--forward", dest="forward", action="store_true", help="Show all Coding/Forward plots")
    parser.add_argument("--all", dest="all", action="store_true", help="Show all plots!")
    args = parser.parse_args()

    global param
    param,data = read_pickle(args.data)

    # Throughputs and delays
    throughput_agg = {'coding': [], 'nocoding': []}
    delay_agg = {'coding': [], 'nocoding': []}
    for slave in data['coding']['slaves']:
            # Read/plot slave throughputs and delays
            speeds,throughputs_avg,throughputs_var,throughputs_std = plot_slave_throughput(data, slave)
            speed,delays = plot_avg_delay(data, slave)

            # Add data for later aggregation
            for coding in data:
                throughput_agg[coding].append(throughputs_avg[coding])
                delay_agg[coding].append(delays[coding])

    # Plot the mean throughput and delay for all slaves
    plot_total_throughputs(throughput_agg, speeds)
    plot_total_delays(delay_agg, speeds)

    # Plot node forward/code counters
    for node in data['coding']['nodes']:
        #plot_ath_stats(data, node)
        plot_node_cpu(data, node)

        # Forwards/codings and coding queue is only relevant for relay nodes
        if not node in data['coding']['slaves']:
            plot_coding_forward(data, node)
            plot_coding_queue(data, node)

    # Save figures if not told otherwise
    if args.out:
        save_figs(args.out, args.data)

    if not args.all:
        remove_figs(data, args)

    pylab.show()

if __name__ == "__main__":
    main()
