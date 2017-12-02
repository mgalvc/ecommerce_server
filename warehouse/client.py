import socket, json, random, time, sys, threading, random, datetime, atexit, struct
import netifaces as ni


class Client(object):

	def __init__(self):
		self.socket_to_multicast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		ttl_bin = struct.pack('@i', 1)
		self.socket_to_multicast.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)
		
		self.node_address = None
		self.node_port = None

	def config(self, node_address, node_port):
		self.node_address = node_address
		self.node_port = node_port

	def update_servers(self, itens, location):
		message = {
			'source': 'warehouse',
			'action': 'new_entry',
			'payload': {
				'itens': itens,
				'location': location
			}
		}

		self.socket_to_multicast.sendto(json.dumps(message).encode(), ('225.0.0.250', 10000))

		return 'sent {} to servers through multicast'.format(message.get('payload'))


