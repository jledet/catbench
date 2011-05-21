#!/usr/bin/env python2

import cPickle
import socket
import argparse

stats_path = '/sys/kernel/debug/batman_adv/bat0/coding_stats'
clear_path = '/sys/kernel/debug/batman_adv/bat0/coding_stats_clear'
catw_path = '/sys/devices/virtual/net/bat0/mesh/catwoman'
hold_path = '/sys/devices/virtual/net/bat0/mesh/catwoman_hold'
purge_path = '/sys/devices/virtual/net/bat0/mesh/catwoman_purge'
hop_path = '/sys/devices/virtual/net/bat0/mesh/hop_penalty'
tq_path = '/sys/devices/virtual/net/bat0/mesh/catwoman_random_tq'
orig_path = '/sys/kernel/debug/batman_adv/bat0/originators'
cpu_path = '/proc/stat'
test_path = '/tmp/cmd_test'
ath_cmd = 'athstats'

def connect(host):
    port = "9988"
    if ':' in host:
        (host, port) = host.split(':')

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, int(port)))
    return sock

def send_obj(sock, obj):
    f = sock.makefile('wb')
    cPickle.dump(obj, f, cPickle.HIGHEST_PROTOCOL)
    f.close()

def recv_obj(sock):
    f = sock.makefile('rb')
    obj = cPickle.load(f)
    f.close()
    return obj

def exec_cmd(sock, command):
    cmd = {}
    cmd['action'] = 'exec'
    cmd['cmd'] = command
    send_obj(sock, cmd)
    return recv_obj(sock)

def write_cmd(sock, path, val=''):
    cmd = {}
    cmd['action'] = 'write'
    cmd['path'] = path
    cmd['value'] = val
    send_obj(sock, cmd)
    return recv_obj(sock)

def read_cmd(sock, path):
    cmd = {}
    cmd['action'] = 'read'
    cmd['path'] = path
    send_obj(sock, cmd)
    return recv_obj(sock)

def close_cmd(sock):
    cmd = {}
    cmd['action'] = 'close'
    send_obj(sock, cmd)
    return recv_obj(sock)

def get_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-n', dest='node', required=True)
    parser.add_argument('-s', dest='stats', action='store_true')
    parser.add_argument('-c', dest='clear', action='store_true')
    parser.add_argument('-e', dest='enable', action='store_true')
    parser.add_argument('-d', dest='disable', action='store_true')
    parser.add_argument('-q', dest='quit', action='store_true')
    parser.add_argument('-u', dest='cpu', action='store_true')
    parser.add_argument('-o', dest='orig', action='store_true')
    parser.add_argument('-a', dest='ath', action='store_true')
    parser.add_argument('-t', dest='test', action='store_true')
    parser.add_argument('--hop-penalty', dest='hop')
    parser.add_argument('-h', dest='hold')
    parser.add_argument('-p', dest='purge')
    return parser.parse_args()

def parse_args(sock, args):
    if args.stats:
        return read_cmd(sock, stats_path)
    elif args.clear:
        return read_cmd(sock, clear_path)
    elif args.enable:
        return write_cmd(sock, catw_path, '1')
    elif args.disable:
        return write_cmd(sock, catw_path, '0')
    elif args.hold:
        return write_cmd(sock, hold_path, args.hold)
    elif args.purge:
        return write_cmd(sock, purge_path, args.purge)
    elif args.hop:
        return write_cmd(sock, hop_path, args.hop)
    elif args.orig:
        return read_cmd(sock, orig_path)
    elif args.cpu:
        return read_cmd(sock, cpu_path)
    elif args.ath:
        return exec_cmd(sock, ath_cmd)
    elif args.quit:
        return close_cmd(sock)

def test_cmd():
    sock = connect(args.node)
    print(write_cmd(sock, test_path, 'test'))
    sock.close()

    sock = connect(args.node)
    print(read_cmd(sock, test_path))
    sock.close()

    sock = connect(args.node)
    print(write_cmd(sock, test_path, 0))
    sock.close()

    sock = connect(args.node)
    print(write_cmd(sock, test_path+'/', 0))
    sock.close()

    sock = connect(args.node)
    sock.close()

if __name__ == "__main__":
    args = get_args()
    if args.test:
        test_cmd()
    else:
        sock = connect(args.node)
        print parse_args(sock, args)
        sock.close()
