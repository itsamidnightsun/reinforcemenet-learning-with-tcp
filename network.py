#!/usr/bin/python

import os
import subprocess
import time
import threading
import numpy as np
import random

from subprocess import Popen, PIPE
from mininet.clean import sh
from subprocess import Popen
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from mininet.node import IVSSwitch
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.net import Mininet
from mininet.util import pmonitor

from subprocess import call

#Kills Controller (if any) in the background
process = Popen(['sudo', 'fuser', '-k', '6653/tcp'], stdout=PIPE, stderr=PIPE)

#Kills any instance of Mininet if active, commented lines can be used for troubleshooting
p = Popen(['sudo', 'mn', '-c'], stdout=PIPE, stderr=PIPE)
stdout, stderr = p.communicate()
#print(stderr)
#print(stdout)
p_status = p.wait()

def startNetwork(net, congested_flows, spine_and_leaf):

	info( '*** Starting switches\n')
	
	net.start()
	net.staticArp()

	# stop any controllers to prevent undesirable behavior
	for controller in net.controllers:
        	controller.stop()

	print("\nTurning off IPv6!\n")
	for h in net.hosts:
		h.cmd("sysctl net.ipv6.conf.all.disable_ipv6=1")
		h.cmd("sysctl net.ipv6.conf.default.disable_ipv6=1")
		h.cmd("sysctl net.ipv6.conf.lo.disable_ipv6=1")

	for sw in net.switches:
		sw.cmd("sysctl net.ipv6.conf.all.disable_ipv6=1")
		sw.cmd("sysctl net.ipv6.conf.default.disable_ipv6=1")
		sw.cmd("sysctl net.ipv6.conf.lo.disable_ipv6=1")

	congested_ports = ['9000']
	inital_congested_port = 9000
	last_port_for_host_flows = spine_and_leaf + 1
	congested_flows -= 1 # as the for loop range starts at 0, there's always one more flow than needed

	#print("Port that should be connecting to host devices on all switches is: %d" % int(last_port_for_host_flows))
	
	# make a list of all spine switches in the network
	spines = []
	i = 0

	for x in range(spine_and_leaf):
		i += 1

		if i < 10:
			spine_num = 'sp0%d' % i
			
		elif i >= 10:
			spine_num = 'sp%d' % i
		spines.append(spine_num)
			
	for i in range(congested_flows):
		inital_congested_port += 10
		congested_ports.append(inital_congested_port)

	print("Installing flows.. This may take several minutes!\n")

	for port in congested_ports:
		random_spine = random.randint(1,spine_and_leaf)
		print("Installing flows for flow: %d on randomly selected path %d" % (int(port), int(random_spine)))
		for spine in spines:	
		
			#### FLOWS ON SPINES FOR SENDING RECEIVING CONGESTION FLOWS
			os.system("sudo ovs-ofctl add-flow " + spine + " priority=5,dl_type=0x800,nw_proto=6,tp_dst=" + str(port) + ",actions=output:3")
			os.system("sudo ovs-ofctl add-flow " + spine + " priority=5,dl_type=0x800,nw_proto=6,tp_src=" + str(port) + ",actions=output:1")
			os.system("sudo ovs-ofctl add-flow " + spine + " priority=5,dl_type=0x800,nw_proto=6,tp_dst=5566,actions=output:2")
			os.system("sudo ovs-ofctl add-flow " + spine + " priority=5,dl_type=0x800,nw_proto=6,tp_src=5566,actions=output:1")
			
		#### FLOWS FOR LEAF SWITCHES, SENDING RECEIVING CONGESTION FLOWS
		os.system("sudo ovs-ofctl add-flow lf03 priority=5,dl_type=0x800,nw_proto=6,tp_dst=%d,actions=output:%d" % (int(port), int(last_port_for_host_flows)))
		os.system("sudo ovs-ofctl add-flow lf03 priority=5,dl_type=0x800,nw_proto=6,tp_src=%d,actions=output:%d" % (int(port), int(random_spine))) ##choose random port

		os.system("sudo ovs-ofctl add-flow lf01 priority=5,dl_type=0x800,nw_proto=6,tp_dst=%d,actions=output:%d" % (int(port), int(random_spine))) ##choose same random port
		os.system("sudo ovs-ofctl add-flow lf01 priority=5,dl_type=0x800,nw_proto=6,tp_src=%d,actions=output:%d" % (int(port), int(last_port_for_host_flows)))


	#### FLOWS FOR LEAF SWITCHES, SENDING RECEIVING PRIORITY FLOWS
	os.system("sudo ovs-ofctl add-flow lf02 priority=5,dl_type=0x800,nw_proto=6,tp_dst=5566,actions=output:%d" % int(last_port_for_host_flows))
	os.system("sudo ovs-ofctl add-flow lf02 priority=5,dl_type=0x800,nw_proto=6,tp_src=5566,actions=output:1")

	os.system("sudo ovs-ofctl add-flow lf01 priority=5,dl_type=0x800,nw_proto=6,tp_dst=5566,actions=output:1")
	os.system("sudo ovs-ofctl add-flow lf01 priority=5,dl_type=0x800,nw_proto=6,tp_src=5566,actions=output:%d" % int(last_port_for_host_flows))

	##### FLOWS FOR RL TCP DATA
	os.system("sudo ovs-ofctl add-flow lf01 priority=5,dl_type=0x800,nw_proto=6,tp_dst=123,actions=output:1")
	os.system("sudo ovs-ofctl add-flow sp01 priority=5,dl_type=0x800,nw_proto=6,tp_dst=123,actions=output:2")
	os.system("sudo ovs-ofctl add-flow lf02 priority=5,dl_type=0x800,nw_proto=6,tp_dst=123,actions=output:%d" % int(last_port_for_host_flows))

	os.system("sudo ovs-ofctl add-flow lf02 priority=5,dl_type=0x800,nw_proto=6,tp_src=123,actions=output:1")
	os.system("sudo ovs-ofctl add-flow sp01 priority=5,dl_type=0x800,nw_proto=6,tp_src=123,actions=output:1")
	os.system("sudo ovs-ofctl add-flow lf01 priority=5,dl_type=0x800,nw_proto=6,tp_src=123,actions=output:%d" % int(last_port_for_host_flows))

	CLI( net )
	net.stop()

class spineAndLeaf( Topo ):

	def build(self, spine_and_leaf):

		mac = '000000000001'
		leafs = []


		# adds all spine, leaf, and host devices looping the specified number of times sent by the user 
		for i in range(spine_and_leaf):

			i += 1

			if i < 10:

				spine_num = 'sp0%d' % i
				leaf_num = 'lf0%d' % i

			elif i >= 10:

				spine_num = 'sp%d' % i
				leaf_num = 'lf%d' % i

			host_num = 'h%d' % i
			leafs.append(leaf_num)

			sp0x = self.addSwitch(spine_num, cls=OVSKernelSwitch)
			lf0x = self.addSwitch(leaf_num, cls=OVSKernelSwitch)
			hx = self.addHost(host_num, mac=mac)

			mac = "{:012X}".format(int(mac, 16)+1) #increments mac address by one (specified in base 16)

		outer_count = 1

		# connects all links in the Mininet topology folllowing a strict rule that lf01 will connect to sp01 on eth1
		# and lf02 will connect to sp02 on eth2 and so on. The host will be connected at the very end... E.g.
		# if the Spine and Leaf fabric conist of ten devices, the hosts will all connect on eth11 on the leaf switches 
		# for consistency 
		for leaf in leafs:

			inner_count = 1			
			connect_to_leaf = "sp0%d" % inner_count
			
			if outer_count < 10:
				connect_to_host = "lf0%d" % outer_count
			elif outer_count >= 10:
				connect_to_host = 'lf%d' % outer_count

			for spine_inner in range(spine_and_leaf):

				print("Connecting link: " + str(leaf) + " " + str(connect_to_leaf))
				time.sleep(0.1)

				self.addLink(leaf, connect_to_leaf, cls=TCLink, max_queue_size=10, use_tbf=True, bw = 1) 

				inner_count += 1

				if inner_count < 10:
					connect_to_leaf = "sp0%d" % inner_count

				elif inner_count >= 10:
					connect_to_leaf = 'sp%d' % inner_count

			self.addLink("h%d" % outer_count, connect_to_host, cls=TCLink, max_queue_size=10000000000, use_tbf=True)

			outer_count += 1 
