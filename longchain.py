from slave import *

# Create Alice
alice = Slave("alice")
alice.set_ip("172.26.72.40", "10.10.0.9")
alice.set_node_ip("10.10.0.100", "00:72:cf:28:19:1a")

# Create Bob
bob = Slave("bob")
bob.set_ip("172.26.72.104", "10.10.0.8")
bob.set_node_ip("10.10.0.109", "00:72:cf:28:19:d6")

# Create relays
n1 = Node("n1")
n2 = Node("n2")
n4 = Node("n4")
n5 = Node("n5")
n6 = Node("n6")
n7 = Node("n7")
n8 = Node("n8")
n1.set_ip("cwn1.personal.es.aau.dk", "00:72:cf:28:19:1a")
n2.set_ip("cwn2.personal.es.aau.dk", "00:72:cf:28:19:da")
n4.set_ip("cwn4.personal.es.aau.dk", "00:72:cf:28:19:0a")
n5.set_ip("cwn5.personal.es.aau.dk", "00:72:cf:28:19:88")
n6.set_ip("cwn6.personal.es.aau.dk", "00:72:cf:28:19:a4")
n7.set_ip("cwn7.personal.es.aau.dk", "00:72:cf:28:19:7a")
n8.set_ip("cwn8.personal.es.aau.dk", "00:72:cf:28:19:5a")

# Setup flows
alice.set_flow(bob)
bob.set_flow(alice)

