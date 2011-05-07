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
        self.ip = None
        self.node = None
        self.flow = None
        slaves.append(self)
        self.stopped = False
        self.error = False
        self.finish = threading.Event()
        self.daemon = True
    
    def set_ip(self, ip, bat_ip):
        self.ip = ip
        self.bat_ip = bat_ip

    def set_node(self, node):
        self.node = node
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
                cmd = "iperf -c {} -u -fk -b{}k -t{} -i{}".format(self.flow.bat_ip, self.speed, self.duration, self.interval)
                output = self.run_command(cmd)

                r       = re.findall("(\d*\.?\d*) *Kbits/sec *(\d+\.\d+)+ ms *(\d+)/ *(\d+) *\((\d*\.?\d+)\%\)", output)[0]
                speeds  = re.findall("([0-9]+) Kbits/sec\n", output)[0]

                self.res = {
                        "slave": self.name,
                        "throughput": float(r[0]),
                        "jitter": float(r[1]),
                        "lost": int(r[2]),
                        "total": int(r[3]),
                        "pl": float(r[4])
                        }
                print("{slave:10s}: {throughput: 4.1f} kb/s | {jitter: 2.1f} ms | {lost: 4d}/{total: 4d} ({pl: 3.1f}%)".format(**self.res))
                self.finish.set()
            except Exception as e:
                print(output)
                print("Test failed for {}! ({})".format(self.name, e))
                self.error = True
                self.finish.set()

class Node():
    def __init__(self, name):
        self.name = name
        self.ip = None
        self.forward_ip = None
        self.port = 9988
        nodes.append(self)

    def set_ip(self, ip):
        self.ip = ip
        self.forward_ip = ip

    def set_local(self):
        self.forward_ip = "localhost"
        self.port = get_port()

def start_slaves():
    for slave in slaves:
        slave.start_iperf()
        slave.start_tunnel()

def stop_slaves():
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

def signal_slaves():
    for slave in slaves:
        slave.error = False
    signal.set()
    signal.clear()

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

def set_coding_nodes(coding=True):
    c = "1" if coding else "0"
    for node in nodes:
        host = "{}:{}".format(node.forward_ip, node.port)
        s = cmd.connect(host)
        cmd.write_cmd(s, cmd.catw_path, c)
