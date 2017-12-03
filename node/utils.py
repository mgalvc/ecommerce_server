import json, socketserver

servers = [
	('192.168.15.9', 8000), 
	('192.168.15.13', 8000), 
]

def get_server_round_robin():
	best = servers.pop(0)
	servers.append(best)
	return best

class ConnectionHandler(socketserver.BaseRequestHandler):

	def handle(self):
		data = json.loads(self.request[0].decode())
		socket = self.request[1]

		if data.get('source') == 'customer':
			print('someone connected')
			if data.get('action') == 'get_best_server':
				response = {
					'best_server': get_server_round_robin()
				}

				socket.sendto(json.dumps(response).encode(), self.client_address)



