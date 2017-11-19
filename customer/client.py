import socket
import json
import sys
import utils
import threading

node_addr = sys.argv[1]
node_port = 8001

socket_to_node = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

request = {
	'source': 'customer',
	'action': 'get_best_server'
}

socket_to_node.sendto(json.dumps(request).encode(), (node_addr, node_port))

response = json.loads(socket_to_node.recv(1024).decode())
best_server = tuple(response.get('best_server'))

print("best server to connect is {}".format(best_server))

socket_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

service = utils.CustomerService(socket_to_server, best_server)

service.start()