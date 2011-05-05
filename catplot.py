#!/usr/bin/env python2

import sys
import numpy
import pylab
import argparse
import operator

colors = {
    "scarlet_red":    "#cc0000",
    "sky_blue_light": "#729fcf",
    "sky_blue_dark":  "#204a87",
    "chameleon":      "#73d216",
    "plum":           "#75507b",
    "orange":         "#f57900",
    "butter":         "#edd400"
}

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
    set_style('default')

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--without-nc", required=True, dest="without_nc")
    parser.add_argument("--with-nc", required=True, dest="with_nc")
    args = parser.parse_args()

    legends = []
    pylab.hold('on')

    for filename in (args.with_nc, args.without_nc):
        title = "Unknown"
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
                    speed, test, tx_speed, tx_delay, tx_lost, tx_total, tx_pl, rx_speed, rx_delay, rx_lost, rx_total, rx_pl = line.split(",")
                    if not speed in meas.keys(): meas[speed] = []
                    meas[speed].append((test, tx_speed, tx_delay, tx_lost, tx_total, tx_pl, rx_speed, rx_delay, rx_lost, rx_total, rx_pl))
                elif "Title" in line:
                    title = line.split(":")[1].strip()
                    legends.append(title)

            y = []
            for i in meas.keys():
                j = map(lambda k: float(k[1]), meas[i])
                y.append(sum(j)/len(j))
            x = map(lambda l: int(l), meas.keys())
            x,y = zip(*sorted(zip(x,y)))
            if filename == args.with_nc:
                y_nc = y
            elif filename == args.without_nc:
                y_no_nc = y

    coding_gain = map(operator.sub, y_nc, y_no_nc)
    legends.append("Coding gain")
    pylab.plot(x, y_nc, color=colors["chameleon"], linewidth=2)
    pylab.plot(x, y_no_nc, color=colors["sky_blue_dark"], linewidth=2)
    pylab.plot(x, coding_gain, color=colors["scarlet_red"], linewidth=2)
    pylab.plot(x, x, color="#000000", linestyle="--")
    pylab.title("Transmit vs. Receive speed")
    pylab.xlabel("Transmit speed [kb/s]")
    pylab.ylabel("Receive speed [kb/s]")
    pylab.legend(legends, loc='upper left', shadow=True)
    pylab.grid('on')
    pylab.show()

if __name__ == "__main__":
    main()
