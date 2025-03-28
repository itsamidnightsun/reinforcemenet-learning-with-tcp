import socket
import subprocess
import time
import traceback

oneFlow = []

portNum = 5566
srcPort = 44409

xx = False

while True:
	try:
		client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client.connect(('10.0.0.2', 123))


		time.sleep(4)

		if client.connect:

			print ("Connected!")

			result = subprocess.run(['ss', '-i'], stdout=subprocess.PIPE)
			result = result.stdout
			result = result.splitlines()

			if result is not None:

				for i in result:

					i = i.decode("utf-8")

					if xx == True and str(portNum) not in i and ("rto" in i or "cubic" in i or "retrans" in i or "cwnd" in i or "rtt" in i or "bytes" in i):
						oneFlow.append(i)
					elif str(portNum) in i and "tcp" in i and str(srcPort) in i:
						if "CLOSE-WAIT" not in i and "1      0 " not in i and "0      0 " not in i and "0      1 " not in i and "1      1 " and "2      0 " not in i and "0      2 " not in i and "2      2 " not in i and "2      1 " not in i and "1      2 " not in i:
							xx = True
							oneFlow.append(i)
					elif "tcp" in i and str(portNum) not in i and xx == True:
						xx = False
						break
				print(oneFlow)

				oneFlow = ''.join(oneFlow)
				client.send(oneFlow.encode('ascii'))
				xx = False
				result = ""
				oneFlow = []
				time.sleep(5)
	except Exception as e:
		time.sleep(4)
		print(traceback.format_exc())
