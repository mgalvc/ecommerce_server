from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import sys
import threading
import json

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

				print(itens)

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


reactor.listenMulticast(10000, MulticastingServer(), listenMultiple=True)
reactor.run()