from slave import *

# Create Alice
alice = Slave("alice")
alice.set_ip("172.26.72.40", "10.10.0.9")
alice.set_node_ip("10.10.0.106", "06:72:cf:28:19:a4")

# Create Bob
bob = Slave("bob")
bob.set_ip("172.26.72.104", "10.10.0.8")
bob.set_node_ip("10.10.0.109", "06:72:cf:28:19:d6")

# Create relays
n7 = Node("n7")
n8 = Node("n8")
n7.set_ip("cwn7.personal.es.aau.dk", "06:72:cf:28:19:7a")
n8.set_ip("cwn8.personal.es.aau.dk", "06:72:cf:28:19:5a")

# Setup flows
alice.set_flow(bob)
bob.set_flow(alice)
