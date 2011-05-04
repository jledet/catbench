#!/usr/bin/env python2

import sys
import socket
import pickle
import time
import argparse
import threading

port = 8899

class Server(threading.Thread):
    def __init__(self, args, server=True):
        super(Server, self).__init__(None)

        self.args = args
        self.bind = args.bind
        self.port = args.port
        self.is_server = server

        self.start()

    def run(self):
        try:
            self.listen()

            if self.is_server:
                self.client = Client(self.args, False)

            self.open_udp()
            self.step_udp()
            self.close()
        except KeyboardInterrupt:
            return

    def listen(self):
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp.bind((self.bind, self.port))
        self.tcp.listen(1)
        self.conn, addr = self.tcp.accept()
        self.config = self.recv_object()

        self.args.host = addr[0]
        print("Connection from {0}".format(addr))

    def recv_object(self):
        f = self.conn.makefile('rb')
        ret = pickle.load(f)
        f.close()
        return ret

    def open_udp(self):
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp.bind((self.bind, self.port))

    def step_udp(self):
        begin = self.config['start']
        end = self.config['end']
        step = self.config['step']

        while True:
            i = self.recv_object()
            if not i:
                break

            self.read_udp(i)

    def read_udp(self, i):
        count = self.config['pc']
        size = self.config['ps']
        missed = 0
        x = 0

        while x < count:
            packet = int(self.udp.recv(size))
            if packet > x:
                missed += packet - x
                x = packet + 1
            else:
                x += 1

        print("{0}: {1}/{2}".format(i, count-missed, count))

    def close(self):
        self.udp.close()
        self.tcp.close()



class Client(threading.Thread):
    def __init__(self, args, client=True):
        super(Client, self).__init__(None)

        self.host = args.host
        self.port = args.port
        self.config = args.config
        self.is_client = client

        self.start()

    def run(self):
        try:
            if self.is_client:
                self.server = Server(args, False)

            self.connect()

            self.open_udp()
            self.step_udp()
            self.close()
        except KeyboardInterrupt:
            return

    def connect(self):
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp.connect((self.host, self.port))
        self.send_object(self.config)

        print("Connected")

    def send_object(self, obj):
        f = self.tcp.makefile('wb')
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
        f.close()

    def open_udp(self):
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def step_udp(self):
        begin = self.config['start']
        end = self.config['end']
        step = self.config['step']

        for i in range(begin, end, -step):
            self.send_object(i)
            self.send_udp(i)
            time.sleep(1)

        self.send_object(0)

    def send_udp(self, i):
        size = self.config['ps']
        count = self.config['pc']

        for x in range(count):
            packet = str(x).zfill(size)
            self.udp.sendto(packet, 0, (self.host, self.port))
            time.sleep(i/1000.0)

    def close(self):
        self.udp.close()
        self.tcp.close()


class ParseArgs:
    def __init__(self):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('-s', dest='server', action='store_true')
        parser.add_argument('-h', dest='host', default='localhost')
        parser.add_argument('-b', dest='bind', default='')
        parser.add_argument('-p', dest='port', default=8899)
        parser.add_argument('-ps', dest='ps', default=1400)
        parser.add_argument('-pc', dest='pc', default=100)
        parser.add_argument('-step', dest='step', default=1)
        parser.add_argument('-start', dest='start', default=10)
        parser.add_argument('-end', dest='end', default=0)

        args = parser.parse_args()

        self.server = args.server
        self.host = args.host
        self.bind = args.bind
        self.port = args.port

        self.config = {
            'ps': args.ps,
            'pc': args.pc,
            'step': args.step,
            'start': args.start,
            'end': args.end
            }

if __name__ == "__main__":
    args = ParseArgs()
    try:
        if args.server:
            s = Server(args)
        else:
            c = Client(args)

    except KeyboardInterrupt:
        print("Quiting")

