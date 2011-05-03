#!/usr/bin/env python2

import sys
import socket
import pickle
import time

port = 8899

config = {
        'packet_size': 1400,
        'packet_count': 1000,

        # milliseconds
        'step_size': -1,
        'step_begin': 10,
        'step_end': 0
        }


class Server:
    def __init__(self, host='', port=port):
        self.host = host
        self.port = port

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
        begin = self.config['step_begin']
        end = self.config['step_end']
        step = self.config['step_size']

        for i in range(begin, end, step):
            self.read_udp(i)

    def read_udp(self, i):
        count = self.config['packet_count']
        size = self.config['packet_size']
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
    def __init__(self, config, host='localhost', port=port):
        self.host = host
        self.port = port
        self.config = config

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
        begin = self.config['step_begin']
        end = self.config['step_end']
        step = self.config['step_size']

        for i in range(begin, end, step):
            self.send_udp(i)
            time.sleep(0.1)

    def send_udp(self, i):
        size = self.config['packet_size']
        count = self.config['packet_count']

        print(i)
        for x in range(count):
            packet = str(x).zfill(size)
            self.sock.sendto(packet, 0, (self.host, self.port))
            time.sleep(i/1000.0)

    def close_udp(self):
        self.sock.close()


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            s = Server()
        else:
            c = Client(config)

    except KeyboardInterrupt:
        print("Quiting")

