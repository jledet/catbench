from slave import *

# Create Alice
alice = Slave("alice")
alice.set_ip("172.26.72.104", "10.10.0.8")
alice.set_node_ip("10.10.0.102", "00:72:cf:28:19:16")

# Create Bob
bob = Slave("bob")
bob.set_ip("172.26.72.40", "10.10.0.9")
bob.set_node_ip("10.10.0.106", "00:72:cf:28:19:a4")

# Create relays
n4 = Node("n4")
n5 = Node("n5")
n4.set_ip("cwn4.personal.es.aau.dk", "00:72:cf:28:1c:0a")
n5.set_ip("cwn5.personal.es.aau.dk", "00:72:cf:28:19:88")

# Setup flows
alice.set_flow(bob)
bob.set_flow(alice)
