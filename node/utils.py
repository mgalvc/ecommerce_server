import json, socketserver


class ConnectionHandler(socketserver.BaseRequestHandler):

	def handle(self):
		data = json.loads(self.request[0].decode())
		socket = self.request[1]

		if data.get('source') == 'warehouse':
			if data.get('action') == 'get_server':
				response = {
					'source': 'node',
					'payload': {
						'best_server': ('addr', 'port')
					}
				}

				socket.sendto(json.dumps(response).encode(), self.client_address)


