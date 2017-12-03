from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import sys
import threading
import json
import socketserver
import os
import socket
import struct
import time
from geopy.geocoders import Nominatim
from geopy.distance import vincenty


my_address = sys.argv[1]
my_port = int(sys.argv[2])

updated = False

socket_to_multicast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ttl_bin = struct.pack('@i', 3)
socket_to_multicast.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)

stock_details = {}
stock_total = {}

path = os.path.dirname(os.path.abspath(__file__))

if os.path.exists(path + '/stock_details.txt'):
	stock_details_file = open(path + '/stock_details.txt', 'r')
	stock_total_file = open(path + '/stock_total.txt', 'r')

	stock_details = json.loads(stock_details_file.read())
	stock_total = json.loads(stock_total_file.read())

	stock_details_file.close()
	stock_total_file.close()

	print(stock_details)
	print(stock_total)

def flush_stock():
	stock_details_file = open(path + '/stock_details.txt', 'w')
	stock_total_file = open(path + '/stock_total.txt', 'w')

	stock_details_file.write(json.dumps(stock_details))
	stock_total_file.write(json.dumps(stock_total))

	stock_details_file.close()
	stock_total_file.close()

def get_closest(location, warehouses):
	closest = None
	geolocator = Nominatim()

	for warehouse in warehouses:
		origin_geocode = geolocator.geocode(location)
		origin = (origin_geocode.latitude, origin_geocode.longitude)
		destination_geocode = geolocator.geocode(warehouse)
		destination = (destination_geocode.latitude, destination_geocode.longitude)

		distance = vincenty(origin, destination).miles

		if closest == None or closest[1] > distance:
			closest = [warehouse, distance]

	closest[1] = closest[1] * 1.609344

	return closest

def update_others(message):
	request = {
		'source': my_address,
		'action': 'update',
		'payload': message
	}
	socket_to_multicast.sendto(json.dumps(request).encode(), ('225.0.0.250', 10000))


class MulticastingServer(DatagramProtocol):

	def startProtocol(self):
		self.transport.setTTL(1)
		self.transport.joinGroup('225.0.0.250')

		first_request = {
			'source': my_address,
			'action': 'new_server'
		}

		socket_to_multicast.sendto(json.dumps(first_request).encode(), ('225.0.0.250', 10000))

	def datagramReceived(self, datagram, address):

		response = json.loads(datagram.decode())
		print("got {} from {}".format(response, address))

		if response.get('source') == 'warehouse':
			if response.get('action') == 'new_entry':
				itens = response.get('payload').get('itens')
				location = response.get('payload').get('location')

				for item in itens:
					if item in stock_details:
						if location in stock_details[item]:
							stock_details[item][location]['price'] = itens[item]['price']
							stock_details[item][location]['tax'] = itens[item]['tax']
						else:
							to_update = {
								location: itens[item]
							}
							stock_details[item].update(to_update)
					else:						
						to_update = {
							item: {
								location: itens[item]
							}
						}
						stock_details.update(to_update)

					if item in stock_total:
						stock_total[item]['quantity'] += itens[item]['quantity']
						stock_total[item]['price'] = itens[item]['price']
					else: 
						stock_total.update({ item: {
								'quantity': itens[item]['quantity'],
								'price': itens[item]['price']
							}
						})

				flush_stock()

				print(stock_details)
				print(stock_total)

				self.transport.write('ok'.encode(), address)
		elif not response.get('source') == my_address:
			print('got a multicast message from other server')
			if response.get('action') == 'update':
				itens = response.get('payload').get('itens')
				warehouse_location = response.get('payload').get('warehouse_location')
				
				for item in itens:
					stock_total[item]['quantity'] -= itens[item]
				
				flush_stock()
			if response.get('action') == 'new_server':
				print('{} came to network'.format(address))

				message = {
					'source': my_address,
					'to': address[0],
					'action': 'new_server_response',
					'stock_details': stock_details,
					'stock_total': stock_total
				}

				socket_to_multicast.sendto(json.dumps(message).encode(), ('225.0.0.250', 10000))
			if response.get('action') == 'new_server_response' and response.get('to') == my_address and not updated:
				updated = True
				print("{} answered me".format(address))
				stock_total.update(response.get('stock_total'))
				stock_details.update(response.get('stock_details'))


class TCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer): pass

class TCPHandler(socketserver.BaseRequestHandler):

	def handle(self):
		print("{} connected".format(self.client_address[0]))

		while True:
			request = json.loads(self.request.recv(1024).decode())

			if request.get('source') == 'customer':
				if request.get('action') == 'get_products':
					response = {
						'source': 'server',
						'payload': stock_total
					}
					
					self.request.send(json.dumps(response).encode())
				if request.get('action') == 'get_shipping_tax':
					itens = request.get('payload').get('itens')
					location = request.get('payload').get('location')

					tax = 0

					for item in itens:
						warehouses = list(stock_details[item])
						closest_warehouse = get_closest(location, warehouses)
						tax += stock_details[item][closest_warehouse[0]]['tax'] * 2.5 * itens[item]

					tax = round(tax, 2)

					response = {
						'source': 'server',
						'payload': {
							'tax': tax,
							'warehouse_location': closest_warehouse[0]
						}
					}

					self.request.send(json.dumps(response).encode())
				if request.get('action') == 'checkout':
					itens = request.get('payload').get('itens')
					warehouse_location = request.get('payload').get('warehouse_location')

					print("get {} from {}".format(itens, warehouse_location))

					payload_message = None
					status_ok = True

					for item in itens:
						if itens[item] > stock_total[item]['quantity']:
							payload_message = "not enough {} in stock".format(item)
							status_ok = False
							break

					if status_ok:
						for item in itens:
							stock_total[item]['quantity'] -= itens[item]
						payload_message = "itens are reserved"
						flush_stock()
						update_others(request.get('payload'))

					response = {
						'source': 'server',
						'payload': {
							'message': payload_message
						}
					}

					self.request.send(json.dumps(response).encode())

tcp_server = TCPServer((my_address, my_port), TCPHandler)
tcp_thread = threading.Thread(target=tcp_server.serve_forever)
tcp_thread.daemon = True
tcp_thread.start()

reactor.listenMulticast(10000, MulticastingServer(), listenMultiple=True)
reactor.run()