#!/usr/bin/env python2.7

import os
import sys
import subprocess
import time
import cmd

alice = "10.10.0.9"
alice_ssh = "alice"
bob = "10.10.0.8"
bob_ssh = "bob"
relay = "cwn1.personal.es.aau.dk:9988"
timeout = "10"
runs = 25

def run_test(slave, server, timeout, dual):
    exec_cmd(slave, "killall -9 -q iperf || true")
    d = ' -d' if dual else ''
    print "iperf -c{} -t{} -yc {}".format(server, timeout, d)
    return exec_cmd(slave, "iperf -c{} -t{} -yc {}".format(server, timeout, d))

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

def run_tests(server_slave, client_slave, server_node, relay, timeout, dual=True):
    set_tq(relay, False)
    set_coding(relay, True)
    start_iperf(server_slave)
    print run_test(client_slave, server_node, timeout, dual)
    sys.stdout.flush()

    set_tq(relay, True)
    set_coding(relay, True)
    start_iperf(server_slave)
    print run_test(client_slave, server_node, timeout, dual)
    sys.stdout.flush()

    set_coding(relay, False)
    start_iperf(server_slave)
    print run_test(client_slave, server_node, timeout, dual)
    sys.stdout.flush()

if __name__ == "__main__":
    dual = True
    for i in range(runs):
        control = "vegas"
        print("Congestion control: {}\n".format(control))
        sys.stdout.flush()
        set_control(alice_ssh, control)
        set_control(bob_ssh, control)
        run_tests(alice_ssh, bob_ssh, alice, relay, timeout, dual)
        run_tests(bob_ssh, alice_ssh, bob, relay, timeout, dual)

        control = "cubic"
        print("Congestion control: {}\n".format(control))
        sys.stdout.flush()
        set_control(alice_ssh, control)
        set_control(bob_ssh, control)
        run_tests(alice_ssh, bob_ssh, alice, relay, timeout, dual)
        run_tests(bob_ssh, alice_ssh, bob, relay, timeout, dual)

        control = "westwood"
        print("Congestion control: {}\n".format(control))
        sys.stdout.flush()
        set_control(alice_ssh, control)
        set_control(bob_ssh, control)
        run_tests(alice_ssh, bob_ssh, alice, relay, timeout, dual)
        run_tests(bob_ssh, alice_ssh, bob, relay, timeout, dual)

        control = "veno"
        print("Congestion control: {}\n".format(control))
        sys.stdout.flush()
        set_control(alice_ssh, control)
        set_control(bob_ssh, control)
        run_tests(alice_ssh, bob_ssh, alice, relay, timeout, dual)
        run_tests(bob_ssh, alice_ssh, bob, relay, timeout, dual)
