import socket
import json
import sys
import utils
import threading


class Client(object):

	def __init__(self):
		self.socket_to_node = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.node_addr = ('', 8001)

	def connect_to_best_server(self):
		request = {
			'source': 'customer',
			'action': 'get_best_server'
		}		

		self.socket_to_node.sendto(json.dumps(request).encode(), self.node_addr)

		response = json.loads(self.socket_to_node.recv(1024).decode())
		self.best_server = tuple(response.get('best_server'))

		print("best server to connect is {}".format(self.best_server))

		self.service = utils.CustomerService(self.socket_to_server, self.best_server)

		self.service.start()

	def get_products(self):
		request = {
			'source': 'customer',
			'action': 'get_products'
		}

		response = self.service.send_message(json.dumps(request).encode())

		products = json.loads(response.decode()).get('payload')

		return products

	def send_message(self, message):
		self.service.send_message(json.dumps(message).encode())
