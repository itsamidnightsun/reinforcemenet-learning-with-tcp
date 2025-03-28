import time

from subprocess import Popen, PIPE

def serverStart():
	p = Popen(['iperf3', '-c', '10.0.0.3', '-p', '9000','-P','3','-t','86389'], stdout=PIPE, stderr=PIPE)
	x = time.time() + 86490

	while time.time() < x:
		nextline = p.stdout.readline()
		nextline = nextline.decode('utf-8')

		if nextline == '': 
			break

		print(nextline)

	stdout, stderr = p.communicate()

while True:
	serverStart()
