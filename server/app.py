from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import sys
import threading
import json
import socketserver


my_address = sys.argv[1]
my_port = 8000

stock_details = {}
stock_total = {}

class MulticastingServer(DatagramProtocol):

	def startProtocol(self):
		self.transport.setTTL(1)
		self.transport.joinGroup('225.0.0.250')

	def datagramReceived(self, datagram, address):

		response = json.loads(datagram.decode())

		if response.get('source') == 'warehouse':
			if response.get('action') == 'new_entry':
				itens = response.get('payload').get('itens')
				location = response.get('payload').get('location')

				for item in itens:
					if item in stock_details:
						if location in stock_details[item]:
							stock_details[item][location]['quantity'] += itens[item]['quantity']
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

				print(stock_details)
				print(stock_total)

				self.transport.write('ok'.encode(), address)


class TCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer): pass

class TCPHandler(socketserver.BaseRequestHandler):

	def handle(self):
		print("{} connected".format(self.client_address[0]))

		while True:
			request = json.loads(self.request.recv(1024).decode())
			
			response = {
				'source': 'server',
				'payload': stock_total
			}

			self.request.send(json.dumps(response).encode())

tcp_server = TCPServer((my_address, my_port), TCPHandler)
tcp_thread = threading.Thread(target=tcp_server.serve_forever)
tcp_thread.daemon = True
tcp_thread.start()

reactor.listenMulticast(10000, MulticastingServer(), listenMultiple=True)
reactor.run()