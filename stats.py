#!/usr/bin/env python2

import argparse
import time
import cmd

class Stats:
    def __init__(self):
        self.args = self.get_args()
        self.prepare_file()
        self.run()

    def get_args(self):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('-n', dest='node', required=True)
        parser.add_argument('-f', dest='path', default='stats.csv')
        parser.add_argument('-i', dest='interval', default=1)
        return parser.parse_args()

    def prepare_file(self):
        stats = self.read_meas()
        stats = self.parse_meas(stats)

        line = "#" + ",".join(stats[0]) + "\n"
        self.f = open(self.args.path, 'w')
        self.f.write(line)
        self.f.close()

    def run(self):
        try:
            while True:
                stats = self.read_meas()
                cpu = self.read_cpu()
                print cpu
                stats = self.parse_meas(stats)
                self.write_meas(stats)

                time.sleep(self.args.interval)

        except KeyboardInterrupt:
            return

    def read_meas(self):
        sock = cmd.connect(self.args.node)
        stats = cmd.read_cmd(sock, cmd.stats_path)
        sock.close()
        return stats

    def read_cpu(self):
        sock = cmd.connect(self.args.node)
        cpu = cmd.read_cmd(sock, cmd.cpu_path)
        sock.close()
        return cpu.split("\n")[0]

    def parse_meas(self, meas):
        out = [[], []]
        out[0].append('Timestamp')
        out[1].append(str(int(time.time())))

        for line in meas.split('\n'):
            if ':' not in line:
                continue
            (stat, val) = line.split(':')
            out[0].append(stat)
            out[1].append(str(int(val)))

        return out

    def write_meas(self, meas):
        line = ",".join(meas[1]) + "\n"
        self.f = open(self.args.path, 'a')
        self.f.write(line)
        self.f.close()

if __name__ == "__main__":
    s = Stats()
