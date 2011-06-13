from slave import *

# Create Alice
alice = Slave("alice")
alice.set_ip("172.26.72.40", "10.10.0.9")
#alice.set_ip("172.26.72.111", "10.10.0.10")
#alice.set_node_ip("10.10.0.100", "00:72:cf:28:19:1a")
alice.set_node_ip("10.10.0.106", "00:72:cf:28:19:a4")
#alice.rate_ratio = 0.5

# Create Bob
bob = Slave("bob")
bob.set_ip("172.26.72.104", "10.10.0.8")
#bob.set_node_ip("10.10.0.102", "00:72:cf:28:19:16")
bob.set_node_ip("10.10.0.109", "06:72:cf:28:19:d6")

# Create relay node
node_relay = Node("relay")
#node_relay.set_ip("cwn1.personal.es.aau.dk", "00:72:cf:28:19:da")
#node_relay.set_ip("cwn4.personal.es.aau.dk", "00:72:cf:28:1c:0a")
node_relay.set_ip("cwn7.personal.es.aau.dk", "00:72:cf:28:19:7a")

# Connect flows
alice.set_flow(bob)
bob.set_flow(alice)

# Setup route checks
#alice.add_route(bob.node, node_relay)
#bob.add_route(alice.node, node_relay)
