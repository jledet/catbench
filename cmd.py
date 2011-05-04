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

def args():
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

cmd = {
        'action': 'read',
        'path': '',
        'value': ''
        }

sock = connect(args.node)

if args.stats:
    cmd['path'] = stats_path
    send_obj(sock, cmd)
    val = recv_obj(sock)
    print(val)
elif args.clear:
    cmd['action'] = 'write'
    cmd['path'] = clean_path
    send_obj(sock, cmd)
    val = recv_obj(sock)
    print(val)
elif args.enable:
    cmd['action'] = 'write'
    cmd['path'] = catw_path
    cmd['value'] = '0'
    send_obj(sock, cmd)
    val = recv_obj(sock)
    print(val)
elif args.disable:
    cmd['action'] = 'write'
    cmd['path'] = catw_path
    cmd['value'] = '0'
    send_obj(sock, cmd)
    val = recv_obj(sock)
    print(val)
elif args.hold:
    cmd['action'] = 'write'
    cmd['path'] = hold_path
    cmd['value'] = args.hold
    send_obj(sock, cmd)
    val = recv_obj(sock)
    print(val)
elif args.purge:
    cmd['action'] = 'write'
    cmd['path'] = purge_path
    cmd['value'] = args.purge
    send_obj(sock, cmd)
    val = recv_obj(sock)
    print(val)
elif args.quit:
    cmd['action'] = 'close'
    send_obj(sock, cmd)
    val = recv_obj(sock)
    print(val)



sock.close()
