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
        self.rate_ratio = 1

        slaves.append(self)

        self.stopped = False
        self.error = False
        self.timestamp = None
        self.finish = threading.Event()
        self.delay_finish = threading.Event()
        self.daemon = True

    def set_ip(self, ip, bat_ip):
        self.ip = ip
        self.bat_ip = bat_ip

    def set_node_ip(self, ip, mac):
        self.node.set_ip(ip, mac)
        self.node.set_local()

    def set_flow(self, flow):
        self.flow = flow

    def add_route(self, orig, nexthop):
        self.node.add_route(orig, nexthop)

    def run_command(self, command):
        return subprocess.check_output(["ssh", "-o", "PasswordAuthentication=no", "catwoman@{}".format(self.ip), command], stderr=subprocess.STDOUT)

    def stop_iperf(self):
        self.run_command("killall -9 iperf || true")

    def start_iperf(self):
        self.stop_iperf()
        self.run_command("iperf -s -u -B{} &> /dev/null &".format(self.bat_ip))

    def stop_tunnel(self):
        os.system("ps aux | grep ssh | grep catwoman@{} | grep {} | awk '{{print $2}}' | xargs kill".format(self.ip, self.node.port))

    def start_tunnel(self):
        self.stop_tunnel()
        os.system("ssh -o PasswordAuthentication=no -fNL {}:{}:9988 catwoman@{}".format(self.node.port, self.node.ip, self.ip))

    def stop(self):
        self.stopped = True

    def delay_run(self):
        while not self.stopped:
            signal.wait()
            try:
                command = "ping -q {} -w {} || true".format(self.flow.bat_ip, self.duration)
                output  = self.run_command(command)

                min,avg,max,mdev = re.findall("(\d+\.?\d*)/(\d+\.?\d*)/(\d+\.?\d*)/(\d+\.?\d*)", output)[0]
                self.delay_res = {
                        'delay_min': float(min),
                        'delay_avg': float(avg),
                        'delay_max': float(max),
                        'delay_mdev': float(mdev)
                        }
                self.delay_finish.set()
            except KeyboardInterrupt:
                return 
            except Exception as e:
                if not self.stopped:
                    print("Delay failed for {}! ({})".format(self.name, e))
                    print(output)
                self.error = True
                self.delay_finish.set()

    def run(self):
        #self.delay_thread = threading.Thread(None, self.delay_run)
        #self.delay_thread.start()
        while not self.stopped:
            # Wait for start signal
            signal.wait()

            try:
                speed = self.speed*self.rate_ratio
                command = "iperf -c {} -u -fk -b{}k -t{} -i{}".format(self.flow.bat_ip, speed, self.duration, self.interval)
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
                self.timestamp = time.time()
                self.finish.set()
            except KeyboardInterrupt:
                return 
            except Exception as e:
                if not self.stopped:
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
        self.endnode = False
        self.routes = []
        nodes.append(self)

    def add_route(self, orig, nexthop):
        self.routes.append((orig.mac, nexthop.mac))

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
        slave.stop()
        slave.stop_iperf()
        slave.stop_tunnel()

def restart_iperf_slaves():
    for slave in slaves:
        slave.start_iperf()

def prepare_slaves():
    for slave in slaves:
        if slave.flow:
            slave.start()

def configure_nodes(hold=None, disable_rts=None, rate=None, hop=None, tx=None):
    if hold:
        set_hold_nodes(hold)
    if disable_rts != None:
        set_rts_nodes(disable_rts)
    if rate:
        set_rate_nodes(rate)
    if hop:
        set_hop_penalty(hop)
    if tx:
        set_tx_nodes(tx)

def signal_slaves(test):
    for slave in slaves:
        slave.test = test
        slave.error = False
    signal.set()
    signal.clear()

def check_slave_times():
    max_diff = 1
    last = None
    for slave in slaves:
        if slave.flow and not last:
            last = slave
        if slave.flow and abs(last.timestamp - slave.timestamp) > max_diff:
            print(slave.name)
            return False
    return True

def wait_slaves():
    ret = True
    for slave in slaves:
        if slave.flow:
            slave.finish.wait()
            #slave.delay_finish.wait()
            slave.finish.clear()
            #slave.delay_finish.clear()

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
            #slave.res.update(slave.delay_res)
            l.append(slave.res)
    return l

def set_hold_nodes(hold="30"):
    for node in nodes:
        host = "{}:{}".format(node.forward_ip, node.port)
        s = cmd.connect(host)
        cmd.write_cmd(s, cmd.hold_path, int(hold))

def set_rate_nodes(rate="2", ifc="mesh0"):
    if not rate == "auto":
        rate = rate + "M fixed"

    command = "iwconfig {} rate {}".format(ifc, rate)
    for node in nodes:
        host = "{}:{}".format(node.forward_ip, node.port)
        s = cmd.connect(host)
        cmd.exec_cmd(s, command)

def set_rts_nodes(disable_rts=False, ifc="mesh0"):
    rts_th = "10" if not disable_rts else "off"
    command = "iwconfig {} rts {}".format(ifc, rts_th)
    for node in nodes:
        host = "{}:{}".format(node.forward_ip, node.port)
        s = cmd.connect(host)
        cmd.exec_cmd(s, command)

def set_coding_nodes(coding=True, toggle_tq=False):
    c = "1" if coding else "0"
    try:
        for node in nodes:
            host = "{}:{}".format(node.forward_ip, node.port)
            if toggle_tq:
                s = cmd.connect(host)
                cmd.write_cmd(s, cmd.tq_path, c)
                s = cmd.connect(host)
                cmd.write_cmd(s, cmd.catw_path, "1")
            else:
                s = cmd.connect(host)
                cmd.write_cmd(s, cmd.catw_path, c)
    except Exception:
        return False
    else:
        return True

def set_hop_penalty(penalty="10"):
    for node in nodes:
        host = "{}:{}".format(node.forward_ip, node.port)
        s = cmd.connect(host)
        if node.endnode:
            cmd.write_cmd(s, cmd.hop_path, penalty)
        else:
            cmd.write_cmd(s, cmd.hop_path, "0")

def set_tx_nodes(tx):
    for node in nodes:
        host = "{}:{}".format(node.forward_ip, node.port)
        s = cmd.connect(host)
        cmd.exec_cmd(s, "iwconfig mesh0 txpower {}".format(tx))
