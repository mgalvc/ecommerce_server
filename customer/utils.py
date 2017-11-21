class CustomerService(object):
	
	def __init__(self, socket, best_server):
		self.socket = socket
		self.best_server = best_server

	def start(self):
		self.socket.connect(self.best_server)

	def send_message(self, message):
		self.socket.send(message)

		return self.socket.recv(1024)