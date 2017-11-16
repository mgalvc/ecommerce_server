import socket
import json
import sys

node_addr = sys.argv[1]
node_port = 8001

socket_to_node = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

request = {
	'source': 'customer',
	'action': 'get_best_server'
}

socket_to_node.sendto(json.dumps(request).encode(), (node_addr, node_port))

response = json.loads(socket_to_node.recv(1024).decode())

print(response)