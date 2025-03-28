import sys
import threading
from subprocess import Popen, PIPE
import os
import iperf3
import time

def sendTraffic():

	for i in range(1,100):
		print("Start")

	p = Popen(['iperf3', '-c', '10.0.0.2', '-n', '100M', '-p', '5566', '-B', '10.0.0.1', '--cport', '44409'], stdout=PIPE, stderr=PIPE)

	while True:
		nextline = p.stdout.readline()
		nextline = nextline.decode('utf-8')
		if nextline == '':
			break
		print(nextline)

while True:
	sendTraffic()
	time.sleep(37)
