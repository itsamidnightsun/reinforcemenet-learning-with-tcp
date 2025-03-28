from mininet.net import Mininet

from background_files.network import spineAndLeaf
from background_files.network import startNetwork

congested_flows = 1
spine_and_leaf = 4

topo = spineAndLeaf(spine_and_leaf)
net = Mininet(topo=topo)
startNetwork(net, congested_flows, spine_and_leaf, reinforcement_learning=True)

