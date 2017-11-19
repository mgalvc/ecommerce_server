from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import sys
import threading
import json
import socketserver


my_address = sys.argv[1]
my_port = 8000

stock = {}

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
					if item in stock:
						if location in stock[item]:
							stock[item][location] += itens[item]
						else:
							to_update = {
								location: itens[item]
							}
							stock[item].update(to_update)
					else:						
						to_update = {
							item: {
								location: itens[item]
							}
						}
						stock.update(to_update)

				print(stock)

				self.transport.write('ok'.encode(), address)


class TCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer): pass

class TCPHandler(socketserver.BaseRequestHandler):

	def handle(self):
		print("{} connected".format(self.client_address[0]))

tcp_server = TCPServer((my_address, my_port), TCPHandler)
tcp_thread = threading.Thread(target=tcp_server.serve_forever)
tcp_thread.daemon = True
tcp_thread.start()

reactor.listenMulticast(10000, MulticastingServer(), listenMultiple=True)
reactor.run()