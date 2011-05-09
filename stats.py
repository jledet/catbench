#!/usr/bin/env python2

import argparse
import time
import cmd
import threading
import re

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
        self.last_ath = None

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
                ath = self.read_ath()
                if cpu:
                    self.origs = self.read_origs()
                    stats = self.read_meas()
                    stats = self.parse_meas(stats, cpu, self.origs, ath)
                    self.append_stats(stats)

                time.sleep(self.interval)

        except KeyboardInterrupt:
            return

    def clear_stats(self):
        sock = cmd.connect(self.host)
        stats = cmd.read_cmd(sock, cmd.clear_path)
        sock.close()
        self.stats = []
        self.total_cpu = None
        self.total_idle = None
        self.last_ath = None

    def read_ath(self):
        sock = cmd.connect(self.host)
        ath = cmd.exec_cmd(sock, cmd.ath_cmd)
        sock.close()

        out = {}
        out['tx_management'] = int(re.findall("(\d+) tx management frames", ath)[0])
        out['tx_failed'] = int(re.findall("(\d+) tx failed due to too many retries", ath)[0])
        out['tx_short_retries'] = int(re.findall("(\d+) short on-chip tx retries", ath)[0])
        out['tx_long_retries'] = int(re.findall("(\d+) long on-chip tx retries", ath)[0])
        out['tx_noack'] = int(re.findall("(\d+) tx frames with no ack marked", ath)[0])
        out['tx_rts'] = int(re.findall("(\d+) tx frames with rts enabled", ath)[0])
        out['tx_short'] = int(re.findall("(\d+) tx frames with short preamble", ath)[0])
        out['rx_bad_crc'] = int(re.findall("(\d+) rx failed due to bad CRC", ath)[0])
        out['rx_too_short'] = int(re.findall("(\d+) rx failed due to frame too short", ath)[0])
        out['rx_phy_err'] = int(re.findall("(\d+) PHY errors", ath)[0])
        out['rx'] = sum(map(lambda x: int(x), re.findall(" rx +(\d+)", ath)))
        out['tx'] = sum(map(lambda x: int(x), re.findall(" tx +(\d+)", ath)))

        if not self.last_ath:
            self.last_ath = out
            return None

        ath = {}
        for key in out:
            ath[key] = out[key] - self.last_ath[key]

        self.last_ath = out

        return ath

    def read_origs(self):
        sock = cmd.connect(self.host)
        origs = cmd.read_cmd(sock, cmd.orig_path)
        sock.close()
        return re.findall("([0-9a-fA-F:]{17}) +\d\.\d+s +\((\d+)\) ([0-9a-fA-F:]{17})", origs)

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

    def parse_meas(self, meas, cpu, origs, ath):
        out = {}
        out['cpu'] = cpu
        out['test'] = self.test
        out['origs'] = origs
        out['ath'] = ath
        out['timestamp'] = int(time.time())

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

def nexthops(node):
    origs = {}
    for stat in stats:
        if stat.name == node.name:
            for orig in stat.origs:
                origs[orig[0]] = orig[2]
                break

    return origs

def start(test):
    for stat in stats:
        stat.clear_stats()
        stat.test = test
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
    node.group = 'nodes'

    try:
        s = Stats(node, args.interval)
        s.view = True
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
