#!/usr/bin/env python2

import sys
import serial
import threading
import time

powers = []
signal = threading.Event()

class Power(threading.Thread):
    def __init__(self, node, interval, gun=None):
        # Check if this node has a serial connected
        if not path:
            return

        super(Power, self).__init__(None)
        self.node = node
        self.interval = interval
        self.gun = gun
        self.stop = False
        self.serial = serial.Serial(node.path, node.bitrate, timeout=1)
        self.meas = []
        self.speed = "0"
        self.test = "0"

        self.daemon = True
        self.start()

    def run(self):
        while(True):
            if self.gun:
                self.gun.wait()
            if self.stop:
                break

            try:
                self.read_meas()
                time.sleep(self.interval)
            except Exception:
                print("Power error")
                self.error = True

    def read_meas(self):
        line = self.serial.readline().strip()
        (timestamp, pwr) = line.split()
        self.meas.append(pwr)

    def clear_meas(self):
        self.meas = []

    def quit(self):
        self.stop = True
        if not self.gun.is_set():
            self.gun.set()


def create(nodes, interval):
    for node in nodes:
        pwr = Power(node, interval)
        powers.append(pwr)

def results():
    res = []
    for pwr in powers:
        res.append([pwr, pwr.meas])
    return res

def start(test):
    for pwr in powers:
        pwr.clear_meas()
        pwr.test = test
    signal.set()

def stop():
    signal.clear()
    for pwr in powers:
        if pwr.error:
            return False

    return True

def shutdown():
    for pwr in powers:
        pwr.quit()

if __name__ == "__main__":
    print "Power Meas"
    try:
        pwr = Power("test", "/dev/ttyUSB0", 115200)
        time.sleep(10)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print e

    print pwr.meas
