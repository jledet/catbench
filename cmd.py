#!/usr/bin/env python2

import cPickle
import socket
import argparse

stats_path = '/sys/kernel/debug/batman_adv/bat0/coding_stats'
clean_path = '/sys/kernel/debug/batman_adv/bat0/coding_stats_clear'
catw_path = '/sys/devices/virtual/net/bat0/mesh/catwoman'
hold_path = '/sys/devices/virtual/net/bat0/mesh/catwoman_hold'
purge_path = '/sys/devices/virtual/net/bat0/mesh/catwoman_purge'

def send_obj(sock, obj):
    f = sock.makefile('wb')
    cPickle.dump(obj, f, cPickle.HIGHEST_PROTOCOL)
    f.close()

def recv_obj(sock):
    f = sock.makefile('rb')
    obj = cPickle.load(f)
    f.close()
    return obj

def connect(node):
    host = "10.10.0.10{}".format(node)
    port = 9988
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    return sock

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
    parser.add_argument('-h', dest='hold')
    parser.add_argument('-p', dest='purge')
    return parser.parse_args()


def parse_args(sock, args):
    if args.stats:
        return read_cmd(sock, stats_path)
    elif args.clear:
        return write_cmd(sock, clean_path)
    elif args.enable:
        return write_cmd(sock, catw_path, '1')
    elif args.disable:
        return write_cmd(sock, catw_path, '0')
    elif args.hold:
        return write_cmd(sock, hold_path, args.hold)
    elif args.purge:
        return write_cmd(sock, purge_path, args.purge)
    elif args.quit:
        return close_cmd(sock)

args = get_args()
sock = connect(args.node)
print parse_args(args)
sock.close()
