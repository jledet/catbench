from slave import *

# Create Alice
alice = Slave("alice")
alice.set_ip("172.26.72.40", "10.10.0.9")
alice.set_node_ip("10.10.0.100", "00:72:cf:28:19:1a")

# Create Bob
bob = Slave("bob")
bob.set_ip("172.26.72.111", "10.10.0.8")
bob.set_node_ip("10.10.0.102", "00:72:cf:28:19:16")

# Create relay node
node_relay = Node("relay")
node_relay.set_ip("cwn1.personal.es.aau.dk", "00:72:cf:28:19:da")

# Connect flows
alice.set_flow(bob)
bob.set_flow(alice)
