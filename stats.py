#!/usr/bin/env python2

import argparse
import time
import cmd
import threading

stats = []
signal = threading.Event()

class Stats(threading.Thread):
    def __init__(self, node, interval, gun=None):
        super(Stats, self).__init__(None)
        self.host = "{}:{}".format(node.forward_ip, node.port)
        self.name = node.name
        self.group = node.group
        self.interval = interval
        self.gun = gun

        self.speed = "0"
        self.test = "0"
        self.stats = []
        self.total_cpu = None
        self.total_idle = None

        self.view = False
        self.stop = False
        self.daemon = True
        self.start()

    def quit(self):
        self.stop = True
        if not self.gun.is_set():
            self.gun.set()

    def run(self):
        try:
            while True:
                if self.gun:
                    self.gun.wait()
                if self.stop:
                    break

                cpu = self.read_cpu()
                if cpu:
                    stats = self.read_meas()
                    stats = self.parse_meas(stats, cpu)
                    self.append_stats(stats)

                time.sleep(self.interval)

        except KeyboardInterrupt:
            return

    def clear_stats(self):
        sock = cmd.connect(self.host)
        stats = cmd.read_cmd(sock, cmd.clear_path)
        sock.close()

    def read_meas(self):
        sock = cmd.connect(self.host)
        stats = cmd.read_cmd(sock, cmd.stats_path)
        sock.close()
        return stats

    def read_cpu(self):
        last_cpu = self.total_cpu
        last_idle = self.total_idle

        sock = cmd.connect(self.host)
        cpu = cmd.read_cmd(sock, cmd.cpu_path)
        sock.close()
        line = cpu.split("\n")[0]
        self.total_cpu = sum(map(lambda x: float(x), line.split()[1:]))
        self.total_idle = float(line.split()[4])
        if not last_cpu:
            return None
        else:
            total = self.total_cpu - last_cpu
            idle = self.total_idle - last_idle
            return int(100*(total - idle)/total)

    def parse_meas(self, meas, cpu):
        out = {}
        out['timestamp'] = int(time.time())
        out['cpu'] = cpu
        out['test'] = self.test

        for line in meas.split('\n'):
            if ':' not in line:
                continue
            (stat, val) = line.split(':')
            out[stat.lower()] = int(val)

        return out

    def append_stats(self, meas):
        if self.view:
            self.print_stats(meas)
        else:
            self.stats.append(meas)

    def print_stats(self, meas):
        for stat in meas:
            print("{}: {}".format(stat, meas[stat]))
        print

def create(nodes, interval, filename):
    for node in nodes:
        stat = Stats(node, interval, signal)
        stats.append(stat)

def results():
    res = []
    for stat in stats:
        res.append([stat, stat.stats])

    return res

def last_result(name):
    for stat in stats:
        if stat.name == name:
            return stat.stats[-1]

def start(test):
    for stat in stats:
        stat.test = test
        stat.stats = []
        stat.total_cpu = None
        stat.total_idle = None
    signal.set()

def stop():
    signal.clear()

def get_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-n', dest='node', required=True)
    parser.add_argument('-f', dest='path', default='stats.csv')
    parser.add_argument('-i', dest='interval', default=1)
    parser.add_argument('-p', dest='port', default=8899)
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    import config
    node = config.Node(args.node)
    node.ip = args.node
    node.forward_ip = args.node
    node.port = args.port

    try:
        s = Stats(node, args.interval)
        s.view = True
        s.join()
    except KeyboardInterrupt:
        pass
