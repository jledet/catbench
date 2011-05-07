#!/usr/bin/env python2

import argparse
import time
import cmd
import threading

stats = []
signal = threading.Event()
stat_file = None

class Stats(threading.Thread):
    def __init__(self, node, interval, gun=None):
        super(Stats, self).__init__(None)
        self.host = "{}:{}".format(node.forward_ip, node.port)
        self.name = node.name
        self.interval = interval
        self.gun = gun

        self.speed = "0"
        self.test = "0"
        self.stats = ""
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
        out = [[], []]
        out[0].extend(['Timestamp', 'Node', 'Speed', 'Test'])
        out[1].extend([str(int(time.time())), self.name, self.speed, self.test])

        for line in meas.split('\n'):
            if ':' not in line:
                continue
            (stat, val) = line.split(':')
            out[0].append(stat)
            out[1].append(str(int(val)))

        out[0].extend(["CPU", "Last"])
        out[1].extend([str(cpu), "0"])

        return out

    def append_stats(self, meas):
        if self.view:
            self.print_stats(meas)
        else:
            line = ",".join(meas[1]) + "\n"
            self.stats += line

    def print_stats(self, meas):
        i = 4
        for stat in meas[0][i:15]:
            print("{}: {}".format(stat, meas[1][i]))
            i += 1
        print

def create(nodes, interval, filename):
    global stat_file
    stat_file = open(filename, 'w')
    for node in nodes:
        stat = Stats(node, interval, signal)
        stats.append(stat)

    prepare_file()

def prepare_file():
    global stat_file
    stat = stats[0]
    meas = stat.read_meas()
    cpu = stat.read_cpu()
    meas = stat.parse_meas(meas, cpu)
    line = "#" + ",".join(meas[0]) + "\n"
    stat_file.write(line)
    stat_file.flush()

def configure(speed, test):
    for stat in stats:
        stat.clear_stats()
        stat.speed = str(speed)
        stat.test = str(test)
        stat.total_cpu = None
        stat.total_idle = None

def start():
    signal.set()

def stop():
    signal.clear()
    write()

def write():
    global stat_file
    for stat in stats:
        string = stat.stats[:-2] + "1\n"
        stat_file.write(string)
        stat_file.flush()
        stat.stats = ""

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
