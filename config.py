import subprocess
import os
import threading
import time
import sys
import re
import cmd

slaves = []
nodes = []

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
        os.system("ps aux | grep ssh | grep {} | awk '{{print $2}}' | xargs kill".format(self.ip))

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
            self.signal.wait()

            try:
                cmd = "iperf -c {} -u -fk -b{}k -t{}".format(self.flow.bat_ip, self.speed, self.duration)
                output = self.run_command(cmd)
            except Exception as e:
                print("Test failed for {}! ({})".format(self.name, e))
                sys.exit(-1)
            else:
                if "WARNING" in output:
                    print(output)
                    self.error = True
                    self.finish.set()
                    break

                lines = filter(lambda x: re.search("\(.+%\)$", x), output.split("\n"))
                if not len(lines) == 1:
                    print("Incorrect output format")
                    sys.exit(-1)
                else:
                    tx = lines[0].split()
                    speed = tx[6]
                    delay = tx[8]
                    lost  = tx[10].replace("/", "")
                    total = tx[11]
                    pl    = tx[12].replace("%", "").replace("(", "").replace(")", "")

                    self.res = {"slave": self.name, "speed": speed, "delay": delay, "lost": lost, "total": total, "pl": pl}
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

def prepare_slaves(signal):
    for slave in slaves:
        if slave.flow:
            slave.signal = signal
            slave.start()

def wait_slaves():
    ret = True
    for slave in slaves:
        if slave.flow:
            slave.finish.wait()
            slave.finish.clear()

            if slave.error:
                ret = False
    return ret

def configure_slaves(speed, duration):
    for slave in slaves:
        if slave.flow:
            slave.speed = speed
            slave.duration = duration

def result_slaves():
    l = []
    for slave in slaves:
        if slave.flow:
            l.append(slave.res)
    return l

def start_nodes(coding):
    c = "1" if coding == "enabled" else "0"
    for node in nodes:
            host = "{}:{}".format(node.forward_ip, node.port)
            s = cmd.connect(host)
            cmd.write_cmd(s, cmd.catw_path, c)

