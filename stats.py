#!/usr/bin/env python2

import argparse
import time
import cmd
import threading
import serial
import re
import slave

stats = []
signal = threading.Event()

class Stats(threading.Thread):
    def __init__(self, node, interval, gun=None):
        super(Stats, self).__init__(None)
        self.host = "{}:{}".format(node.forward_ip, node.port)
        self.group = node.group
        self.name = node.name
        self.node = node
        self.interval = interval
        self.gun = gun

        self.speed = "0"
        self.test = "0"
        self.stats = []
        self.total_cpu = None
        self.total_idle = None
        self.error = False

        if node.serial:
            self.serial = serial.Serial(node.serial_path, node.serial_bitrate, timeout=1)

        self.view = False
        self.stop = False
        self.daemon = True
        self.start()

    def quit(self):
        self.stop = True
        if not self.gun.is_set():
            self.gun.set()
        self.serial.close()

    def run(self):
        try:
            while True:
                if self.gun:
                    self.gun.wait()
                if self.stop:
                    break

                try:
                    cpu = self.read_cpu()
                    ath = self.read_ath()
                    pwr = self.read_power()
                    if cpu:
                        self.origs = self.read_origs()
                        stats = self.read_meas()
                        stats = self.parse_meas(stats, cpu, self.origs, ath, pwr)
                        self.append_stats(stats)
                except Exception as e:
                    print("Stats failed for {} ({})".format(self.node.name, e))
                    self.error = True

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
        self.error = False

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

        return out

    def read_origs(self):
        sock = cmd.connect(self.host)
        inp = cmd.read_cmd(sock, cmd.orig_path)
        sock.close()
        origs = re.findall("([0-9a-fA-F:]{17}) +\d+\.\d+s +\(( *\d+)\) ([0-9a-fA-F:]{17})", inp)
        out = {}
        for nexthop in origs:
            out[nexthop[0]] = (nexthop[2], nexthop[1])

        #self.check_origs(out)

        return out

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

    def read_power(self):
        if not self.node.serial:
            return None

        line = self.serial.readline().strip()
        (timestamp, power) = line.split()
        return power

    def parse_meas(self, meas, cpu, origs, ath, pwr):
        out = {}
        out['cpu'] = cpu
        out['test'] = self.test
        out['origs'] = origs
        out['ath'] = ath
        out['timestamp'] = int(time.time())
        out['power'] = pwr

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

    def check_origs(self, origs):
        for route in self.node.routes:
            if not origs.has_key(route[0]):
                print("Route not found at {}: {} -> {}".format(self.node.name, route[0], route[1]))
                self.error = True
                self.gun.clear()
                return False

            if origs[route[0]][0] != route[1]:
                print("Wrong link detected at {}: {} -> {}".format(self.node.name, route[0], origs[route[0]][0]))
                self.error = True
                self.gun.clear()
                return False

        return True

        if not self.node.endnode:
            return
        for node in slave.nodes:
            if not node.endnode:
                continue
            if not origs.has_key(node.mac):
                continue
            if origs[node.mac][0] == node.mac:
                self.error = True


def create(nodes, interval, filename):
    for node in nodes:
        stat = Stats(node, interval, signal)
        stats.append(stat)

def results():
    res = []
    for stat in stats:
        res.append([stat, stat.stats])
    return res

def start(test):
    for stat in stats:
        stat.clear_stats()
        stat.test = test
    signal.set()

def stop():
    signal.clear()
    for stat in stats:
        if stat.error:
            return False

    return True

def shutdown():
    for stat in stats:
        stat.quit()

def get_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-n', dest='node', required=True)
    parser.add_argument('-f', dest='path', default='stats.csv')
    parser.add_argument('-i', dest='interval', default=1)
    parser.add_argument('-p', dest='port', default=9988)
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    import slave
    node = slave.Node(args.node)
    node.ip = args.node
    node.forward_ip = args.node
    node.port = args.port
    node.group = 'nodes'
    node.mac = "00:72:cf:28:19:da"
    node.endnode = False

    try:
        s = Stats(node, args.interval)
        s.view = True
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
