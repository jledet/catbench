#!/usr/bin/env python2

import sys
import socket
import pickle
import time
import argparse

port = 8899

class Server:
    def __init__(self, args):
        self.host = args.host
        self.port = args.port

        self.listen()
        self.read_config()

        self.open_udp()
        self.step_udp()
        self.close_udp()

    def listen(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        self.conn, addr = self.sock.accept()
        print("Connection from {0}".format(addr))

    def read_config(self):
        f = self.conn.makefile('rb')
        self.config = pickle.load(f)
        f.close()
        self.conn.shutdown(socket.SHUT_RD)
        self.conn.close()
        self.sock.close()

    def open_udp(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))

    def step_udp(self):
        begin = self.config['start']
        end = self.config['end']
        step = self.config['step']

        for i in range(begin, end, -step):
            self.read_udp(i)

    def read_udp(self, i):
        count = self.config['pc']
        size = self.config['ps']
        missed = 0
        x = 0

        while x < count:
            packet = int(self.sock.recv(size))
            if packet > x:
                missed += packet - x
                x = packet + 1
            else:
                x += 1

        print("{0}: {1}/{2}".format(i, count-missed, count))

    def close_udp(self):
        self.sock.close()



class Client:
    def __init__(self, args):
        self.host = args.host
        self.port = args.port
        self.config = args.config

        self.connect()
        self.open_udp()
        self.step_udp()
        self.close_udp()

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

        print("Connected")

        f = self.sock.makefile('wb')
        pickle.dump(self.config, f, pickle.HIGHEST_PROTOCOL)
        f.close()
        self.sock.close()
        time.sleep(0.1)

    def open_udp(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def step_udp(self):
        begin = self.config['start']
        end = self.config['end']
        step = self.config['step']

        for i in range(begin, end, -step):
            self.send_udp(i)
            time.sleep(0.1)

    def send_udp(self, i):
        size = self.config['ps']
        count = self.config['pc']

        print(i)
        for x in range(count):
            packet = str(x).zfill(size)
            self.sock.sendto(packet, 0, (self.host, self.port))
            time.sleep(i/1000.0)

    def close_udp(self):
        self.sock.close()


class ParseArgs:
    def __init__(self):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('-s', dest='server', action='store_true')
        parser.add_argument('-h', dest='host', default='localhost')
        parser.add_argument('-p', dest='port', default=8899)
        parser.add_argument('-ps', dest='ps', default=1400)
        parser.add_argument('-pc', dest='pc', default=1000)
        parser.add_argument('-step', dest='step', default=1)
        parser.add_argument('-start', dest='start', default=10)
        parser.add_argument('-end', dest='end', default=0)

        args = parser.parse_args()

        self.server = args.server
        self.host = args.host
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

