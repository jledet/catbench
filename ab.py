from config import *

# Create Alice
alice = Slave("alice")
alice.set_ip("172.26.72.40", "10.10.0.9")
node_alice = Node("alice node")
node_alice.set_ip("10.10.0.100")
alice.set_node(node_alice)

# Create Bob
bob = Slave("bob")
bob.set_ip("172.26.72.111", "10.10.0.8")
node_bob = Node("bob node")
node_bob.set_ip("10.10.0.102")
bob.set_node(node_bob)

# Create relay node
node_relay = Node("relay")
node_relay.set_ip("10.10.0.101")

# Connect flows
alice.set_flow(bob)
bob.set_flow(alice)
