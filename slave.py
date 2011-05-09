import subprocess
import os
import threading
import time
import sys
import re
import cmd

slaves = []
nodes = []
signal = threading.Event()

next_port = 59000

def get_port():
    global next_port
    next_port += 1
    return next_port

class Slave(threading.Thread):
    def __init__(self, name):
        super(Slave, self).__init__(None)
        self.name = name
        self.group = 'slaves'
        self.ip = None
        self.node = Node(self.name)
        self.flow = None
        slaves.append(self)
        self.stopped = False
        self.error = False
        self.timestamp = None
        self.finish = threading.Event()
        self.daemon = True

    def set_ip(self, ip, bat_ip):
        self.ip = ip
        self.bat_ip = bat_ip

    def set_node_ip(self, ip, mac):
        self.node.set_ip(ip, mac)
        self.node.set_local()

    def set_flow(self, flow):
        self.flow = flow

    def run_command(self, command):
        return subprocess.check_output(["ssh", "-o", "PasswordAuthentication=no", "catwoman@{}".format(self.ip), command], stderr=subprocess.STDOUT)

    def stop_iperf(self):
        self.run_command("killall -9 iperf || true")

    def start_iperf(self):
        self.stop_iperf()
        self.run_command("iperf -s -u &> /dev/null &")

    def stop_tunnel(self):
        os.system("ps aux | grep ssh | grep catwoman@{} | awk '{{print $2}}' | xargs kill".format(self.ip))

    def start_tunnel(self):
        self.stop_tunnel()
        os.system("ssh -o PasswordAuthentication=no -fNL {}:{}:9988 catwoman@{}".format(self.node.port, self.node.ip, self.ip))

    def wait_finish(self):
        self.finish.wait()

    def stop(self):
        self.stopped = True

    def run(self):
        while not self.stopped:
            # Wait for start signal
            signal.wait()

            try:
                command = "iperf -c {} -u -fk -b{}k -t{} -i{}".format(self.flow.bat_ip, self.speed, self.duration, self.interval)
                output = self.run_command(command)

                r       = re.findall("(\d*\.?\d*) *Kbits/sec *(\d+\.\d+)+ ms *(\d+)/ *(\d+) *\((\d*\.?\d+)\%\)", output)[0]
                speeds  = re.findall("([0-9]+) Kbits/sec\n", output)[0]

                self.res = {
                        "slave": self,
                        "test": self.test,
                        "throughput": float(r[0]),
                        "jitter": float(r[1]),
                        "lost": int(r[2]),
                        "total": int(r[3]),
                        "pl": float(r[4])
                        }
                print("{:10s} {throughput:5.1f} kb/s | {jitter:4.1f} ms | {lost:4d}/{total:4d} ({pl:4.1f}%)".format(self.name.title(), **self.res))
                self.timestamp = time.time()
                self.finish.set()
            except Exception as e:
                print("Test failed for {}! ({})".format(self.name, e))
                self.error = True
                self.finish.set()

class Node():
    def __init__(self, name):
        self.name = name
        self.group = 'nodes'
        self.ip = None
        self.forward_ip = None
        self.port = 9988
        nodes.append(self)
        self.endnode = False

    def set_ip(self, ip, mac):
        self.ip = ip
        self.forward_ip = ip
        self.mac = mac

    def set_local(self):
        self.forward_ip = "localhost"
        self.endnode = True
        self.port = get_port()

def start_slaves():
    for slave in slaves:
        slave.start_iperf()
        slave.start_tunnel()

def stop_slaves():
    print("Cleaning up")
    for slave in slaves:
        slave.stop_iperf()
        slave.stop_tunnel()

def restart_iperf_slaves():
    for slave in slaves:
        slave.start_iperf()

def prepare_slaves():
    for slave in slaves:
        if slave.flow:
            slave.start()

def configure_nodes(hold, rts, rate):
    set_hold_nodes(hold)
    set_rts_nodes(rts)
    set_rate_nodes(rate)

def signal_slaves(test):
    for slave in slaves:
        slave.test = test
        slave.error = False
    signal.set()
    signal.clear()

def check_slave_times():
    max_diff = 1
    last = slaves[0]
    for slave in slaves:
        if slave.flow and abs(last.timestamp - slave.timestamp) > max_diff:
            return False
    return True

def check_node_paths(stats):
    for node in nodes:
        if node.endnode:
            origs = stats.nexthops(node)
            for orig in nodes:
                if orig.endnode and origs.has_key(orig.mac) and origs[orig.mac] == orig.mac:
                    return False
    return True

def wait_slaves():
    ret = True
    for slave in slaves:
        if slave.flow:
            slave.finish.wait()
            slave.finish.clear()

            if slave.error:
                ret = False
    return ret

def configure_slaves(speed, duration, interval):
    for slave in slaves:
        if slave.flow:
            slave.interval = interval
            slave.speed = speed
            slave.duration = duration

def result_slaves():
    l = []
    for slave in slaves:
        if slave.flow:
            l.append(slave.res)
    return l

def set_hold_nodes(hold=30):
    for node in nodes:
        host = "{}:{}".format(node.forward_ip, node.port)
        s = cmd.connect(host)
        cmd.write_cmd(s, cmd.hold_path, hold)

def set_rate_nodes(rate="2M", ifc="mesh0"):
    if not rate == "auto":
        rate = rate + " fixed"
    for node in nodes:
        host = "{}:{}".format(node.forward_ip, node.port)
        s = cmd.connect(host)
        cmd.exec_cmd(s, "iwconfig {} rate {}".format(ifc, rate))

def set_rts_nodes(rts=True, ifc="mesh0"):
    rts_th = "10" if rts else "off"
    for node in nodes:
        host = "{}:{}".format(node.forward_ip, node.port)
        s = cmd.connect(host)
        cmd.exec_cmd(s, "iwconfig {} rts {}".format(ifc, rts_th))

def set_coding_nodes(coding=True):
    c = "1" if coding else "0"
    for node in nodes:
        host = "{}:{}".format(node.forward_ip, node.port)
        s = cmd.connect(host)
        cmd.write_cmd(s, cmd.catw_path, c)
