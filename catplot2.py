#!/usr/bin/env python2
import pylab
import argparse
import operator
import cPickle
import dummy

legends = []

def avg_value(samples, coding, slave, type, speed, field):
    s = samples[coding][type][slave][speed]
    values = map(lambda vls: vls[field], s)
    avg = float(sum(values))/len(values)
    return avg

def slaves_throughput(samples, coding, slave):
    sample = samples[coding]['slaves'][slave]
    speeds = sorted(sample.keys())
    throughputs = []
    for speed in speeds:
        avg = avg_value(samples, coding, slave, "slaves", speed, 'throughput')
        throughputs.append(avg)
    return speeds,throughputs

def plot_throughput(slave, coding, speed, throughput):
    legends.append("{}{}".format(slave.title(), " with Network Coding" if coding == "coding" else ""))
    pylab.plot(speed, throughput, linewidth=2)

def plot_throughputs(samples, averaged):
    # Aggregated througputs used for coding gain calculation
    throughput_agg = {}
    coding_gain    = {}

    # Loop over coding and no coding
    for coding in samples:
        if not coding in throughput_agg:
            throughput_agg[coding] = {}
        # For all slaves
        for slave in samples[coding]['slaves']:
            # Calculate average throughput
            speeds, throughputs = slaves_throughput(samples, coding, slave)
            throughput_agg[coding][slave] = throughputs

            plot_throughput(slave, coding, speeds, throughputs)

    #map(operator.add, throughput_coding, throughputs)
    print(throughput_agg)

    # Calculate coding gain
    for slave in samples['coding']['slaves']:
        coding_gain[slave] = map(operator.sub, throughput_agg['coding'][slave], throughput_agg['nocoding'][slave]) 

    print(coding_gain)

    pylab.plot(speeds, speeds, color="#000000", linestyle="--")
    pylab.title("Throughput vs. Load")
    pylab.xlabel("Transmit speed [kb/s]")
    pylab.ylabel("Receive speed [kb/s]")
    pylab.grid('on')
    pylab.legend(legends, loc='upper left', shadow=True)

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--data", dest="data", default=None)
    parser.add_argument("--averaged", action="store_true", dest="averaged")
    args = parser.parse_args()

    if not args.data:
        data = dummy.dummy
    else:
        data = cPickle.load(open(args.data, "rb"))
        print("Unpickled {}".format(args.data))

    plot_throughputs(data, args.averaged)
    pylab.show()

if __name__ == "__main__":
    main()
