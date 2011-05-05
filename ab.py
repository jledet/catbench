from config import *

# Create Alice
alice = Slave("alice")
alice.set_ip("172.26.72.40")
node_alice = Node("alice node")
node_alice.set_ip("10.10.0.100")
alice.set_node(node_alice)

# Create Bob
bob = Slave("bob")
bob.set_ip("172.26.72.111")
node_bob = Node("bob node")
node_bob.set_ip("14.14.14.14")
bob.set_node(node_bob)

# Create relay node
node_relay = Node("relay")
node_relay.set_ip("14.14.14.14")

# Connect flows
alice.set_flow(bob)
bob.set_flow(alice)
