#!/usr/bin/env python2.7

import os
import subprocess
import time
import cmd

alice = "10.10.0.10"
alice_ssh = "172.26.72.111"
bob = "10.10.0.7"
bob_ssh = "172.26.72.41"
relay = "cwn1.personal.es.aau.dk:9988"
timeout = "10"
runs = 1

def run_test(slave, server, timeout):
    exec_cmd(slave, "killall -9 -q iperf || true")
    return exec_cmd(slave, "iperf -c{} -t{} -yc -d".format(server, timeout))

def start_iperf(slave):
    exec_cmd(slave, "killall -9 -q iperf || true")
    exec_cmd(slave, "iperf -s &> /dev/null &")

def exec_cmd(host, cmd):
    return subprocess.check_output(["ssh", "-o", "PasswordAuthentication=no", "catwoman@{}".format(host), cmd], stderr=subprocess.STDOUT)

def set_coding(node, coding=True):
    print("Network Coding: {}".format(coding))
    c = "1" if coding else "0"
    s = cmd.connect(node)
    cmd.write_cmd(s, cmd.catw_path, c)

def set_tq(node, tq=True):
    print("Random tq: {}".format(tq))
    t = "1" if tq else "0"
    s = cmd.connect(node)
    cmd.write_cmd(s, cmd.tq_path, t)

def set_control(slave, control="cubic"):
    exec_cmd(slave, "sudo sysctl net.ipv4.tcp_congestion_control={}".format(control))

def run_tests(server_slave, client_slave, server_node, relay, runs, timeout):
    for i in range(runs):
        set_tq(relay, False)
        set_coding(relay, True)
        start_iperf(alice_ssh)
        print run_test(bob_ssh, alice, timeout)

        set_tq(relay, True)
        set_coding(relay, True)
        start_iperf(alice_ssh)
        print run_test(bob_ssh, alice, timeout)

        set_coding(relay, False)
        start_iperf(alice_ssh)
        print run_test(bob_ssh, alice, timeout)

if __name__ == "__main__":
    control = "vegas"
    print("Congestion control: {}\n".format(control))
    set_control(alice_ssh, control)
    set_control(bob_ssh, control)
    run_tests(alice_ssh, bob_ssh, alice, relay, runs, timeout)

    control = "cubic"
    print("Congestion control: {}\n".format(control))
    set_control(alice_ssh, control)
    set_control(bob_ssh, control)
    run_tests(alice_ssh, bob_ssh, alice, relay, runs, timeout)
