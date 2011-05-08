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

legends = []

def avg_value(samples, coding, slave, type, speed, field):
    s = samples[coding][type][slave][speed]
    values = map(lambda vls: vls[field], s)
    avg = float(sum(values))/len(values)
    print(avg)
    print(numpy.mean(values))
    return avg

def slaves_throughput(samples, coding, slave):
    sample = samples[coding]['slaves'][slave]
    speeds = sorted(sample.keys())
    throughputs = []
    for speed in speeds:
        avg = avg_value(samples, coding, slave, "slaves", speed, 'throughput')
        throughputs.append(avg)
    return speeds,throughputs

def plot_throughput(samples, slave, coding):
    speeds, throughputs = slaves_throughput(samples, coding, slave)
    legends.append("{}{}".format(slave.title(), " with Network Coding" if coding == "coding" else ""))
    #pylab.plot(speeds, throughputs, linewidth=2)
    return speeds, throughputs

def plot_coding_gain(slave, speed, gain):
    legends.append("Coding Gain for {}".format(slave.title()))
    pylab.plot(speed, gain, linewidth=2)

def plot_sum_throughputs(coding, throughputs, speeds):
    # Calculate and plot average throughput
    #pylab.figure()
    avg = numpy.mean(throughputs, axis=0)
    pylab.plot(speeds, avg, linewidth=2)

    gain = numpy.array(avg) - numpy.array(avg)
    plot_coding_gain("", speeds, gain)

#    # Calculate and plot coding gain
#    for slave in samples['coding']['slaves']:
#        coding_gain[slave] = map(operator.sub, throughput_agg['coding'][slave], throughput_agg['nocoding'][slave]) 
#        plot_coding_gain(slave, speeds, coding_gain[slave])
   
    #theo_max = speeds if mx == 0 else map(lambda num: num if int(num) < mx else mx, speeds)
    #pylab.plot(speeds, theo_max, color="#000000", linestyle="--")

    pylab.title("Throughput vs. Load")
    pylab.xlabel("Transmit speed [kb/s]")
    pylab.ylabel("Receive speed [kb/s]")
    pylab.grid('on')
    pylab.legend(legends, loc='upper left', shadow=True)

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--data", dest="data", default=None)
    parser.add_argument("--max", dest="max", default=0)
    args = parser.parse_args()

    if not args.data:
        data = dummy.dummy
    else:
        data = cPickle.load(open(args.data, "rb"))
        print("Unpickled {}".format(args.data))

    for coding in data:
        throughput_agg = []
        for slave in data[coding]['slaves']:
            speeds, throughputs = plot_throughput(data, slave, coding)
            throughput_agg.append(throughputs)
        plot_sum_throughputs(coding, throughput_agg, speeds)


    pylab.show()

if __name__ == "__main__":
    main()
