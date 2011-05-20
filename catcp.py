#!/usr/bin/env python

import os
import subprocess

host = "localhost"
timeout = "10"
runs = 10

for i in range(runs):
    print subprocess.check_output(["iperf", "-c", host, "-t", timeout, "-yc", "-d"])
