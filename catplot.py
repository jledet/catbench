#!/usr/bin/env python2

import sys
import numpy
import pylab
import argparse
import operator

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

colors_nc = [c["chameleon2"], c["plum2"], c["aluminium5"]]
colors_no_nc = [c["skyblue3"], c["skyblue1"]]
colors_cg = [c["scarletred1"], c["scarletred2"], c["orange2"], c["scarletred3"], c["orange3"]]

paper = {
    'backend': 'eps',
    'lines.markersize': 8,
    'lines.linewidth': 2,
    'font.size': 14,
    'xtick.direction': 'out',
    'xtick.minor.size': 1,
    'ytick.direction': 'out',
    'ytick.minor.size': 2,
    'axes.linewidth' : 1,
    'text.usetex': True,
    'text.latex.unicode': True,
    'figure.subplot.right': .98,
    'figure.subplot.left': 0.11,
    'figure.subplot.top': .98,
    'figure.subplot.bottom': .09
}

big_fonts = {
    'lines.markersize': 12,
    'font.size': 21,
    'figure.subplot.right': .96,
    'figure.subplot.left': 0.13,
    'figure.subplot.top': .96,
    'figure.subplot.bottom': .13
}

#          'text.usetex': True}
#          'axes.labelsize': 10,
#          'text.fontsize': 10,
#          'xtick.labelsize': 10,
#          'ytick.labelsize': 10,
#          'legend.pad': 10,    # empty space around the legend box
#          'legend.fontsize': 10,

def set_style(mode):
    if mode == 'paper':
        pylab.rcParams.update(paper)
    elif mode == 'paper3rd':
        pylab.rcParams.update(paper)
        pylab.rcParams.update(big_fonts)
    elif mode == 'default':
        pylab.rcParams.setdefault
        print 'default set'
    else:
        print "warning: no such setting, using default"
        change('default')

def main():
    last_color_nc = 0
    last_color_no_nc = 0
    last_color_cg = 0
    set_style('default')

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--without-nc", required=True, dest="without_nc", default=None)
    parser.add_argument("--with-nc", required=True, dest="with_nc", default=None)
    args = parser.parse_args()

    for filename in (args.with_nc, args.without_nc):
        if not filename: continue
        meas = {}
        try:
            f = open(filename)
        except:
            print("Failed to open {}".format(f))
            sys.exit(-1)
        else:
            # Read in all measurements
            for line in f:
                if not line.startswith("#"):
                    slave,test_speed,test,speed,delay,lost,total,pl = line.split(",")
                    if not slave in meas:
                        meas[slave] = []
                    meas[slave].append((test_speed,test,speed,delay,lost,total,pl))

            y = {}
            x = {}
            for i in meas:
                slave_speeds = {}
                for m in meas[i]:
                    ts = m[0] # Read test_speed
                    s =  m[2] # Read speed
                    if not ts in slave_speeds: slave_speeds[ts] = []
                    slave_speeds[ts].append(float(s))
                print(slave_speeds)
                x[i] = map(lambda l: int(l), slave_speeds)
                y[i] = map(lambda j: sum(slave_speeds[j])/len(slave_speeds[j]), slave_speeds)
                x[i],y[i] = zip(*sorted(zip(x[i],y[i]))) # Sort x and y based on x
                print(x)
                print(y)

            if filename == args.with_nc:
                y_nc = y
                x_nc = x
            elif filename == args.without_nc:
                y_no_nc = y
                x_no_nc = x

    legends = []
    coding_gain = {}
    pylab.hold('on')
    for slave in y_nc:
        legends.append(slave.title() + ", CATWOMAN")
        pylab.plot(x_nc[slave], y_nc[slave], color=colors_nc[last_color_nc], linewidth=2)
        last_color_nc += 1
        legends.append(slave.title() + ", No CATWOMAN")
        pylab.plot(x_no_nc[slave], y_no_nc[slave], color=colors_no_nc[last_color_no_nc], linewidth=2)
        last_color_no_nc += 1
        coding_gain[slave] = map(operator.sub, y_nc[slave], y_no_nc[slave])
        pylab.plot(x_no_nc[slave], coding_gain[slave], color=colors_cg[last_color_cg], linewidth=2)
        last_color_cg += 1
        legends.append(slave.title() + " coding gain")

    pylab.plot(x[x.keys()[0]], x[x.keys()[0]], color="#000000", linestyle="--")
    legends.append("Theoretical limit")
    pylab.title("Transmit vs. Receive speed")
    pylab.xlabel("Transmit speed [kb/s]")
    pylab.ylabel("Receive speed [kb/s]")
    pylab.legend(legends, loc='upper left', shadow=True)
    pylab.grid('on')
    pylab.show()

if __name__ == "__main__":
    main()
