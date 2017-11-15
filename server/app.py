from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

class MulticastingServer(DatagramProtocol):

	def startProtocol(self):
		self.transport.setTTL(1)
		self.transport.joinGroup('225.0.0.250')

	def datagramReceived(self, datagram, address):
		print('received {} from {}'.format(datagram, address))
		self.transport.write('ok'.encode(), address)

reactor.listenMulticast(10000, MulticastingServer(), listenMultiple=True)
reactor.run()