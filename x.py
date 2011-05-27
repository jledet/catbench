from slave import *

# Setup relay node
relay = Node("relay")
relay.set_ip("cwn1.personal.es.aau.dk", "00:72:cf:28:19:da")

# Setup Alice
alice = Slave("alice")
alice.set_ip("172.26.72.40", "10.10.0.9")
alice.set_node_ip("10.10.0.100", "00:72:cf:28:19:1a")

# Setup Bob
bob = Slave("bob")
bob.set_ip("172.26.72.104", "10.10.0.8")
bob.set_node_ip("10.10.0.102", "00:72:cf:28:19:16")

# Setup Charlie
charlie = Slave("charlie")
charlie.set_ip("172.26.72.111", "10.10.0.10")
#charlie.set_node_ip("10.10.0.104", "00:72:cf:28:1c:0a")
charlie.set_node_ip("10.10.0.106", "00:72:cf:28:19:a4")

# Setup Dave
dave = Slave("dave")
dave.set_ip("172.26.72.41", "10.10.0.7")
dave.set_node_ip("10.10.0.105", "00:72:cf:28:19:88")

# Connect flows
alice.set_flow(dave)
bob.set_flow(charlie)
charlie.set_flow(bob)
dave.set_flow(alice)

# Setup route checks
alice.add_route(bob.node, relay)
alice.add_route(dave.node, relay)
bob.add_route(alice.node, relay)
bob.add_route(charlie.node, relay)
charlie.add_route(bob.node, relay)
charlie.add_route(dave.node, relay)
dave.add_route(alice.node, relay)
dave.add_route(charlie.node, relay)
