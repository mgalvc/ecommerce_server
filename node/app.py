import socketserver, atexit, sys, socket
from utils import ConnectionHandler
import netifaces as ni

class UDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer): pass

udpserver = UDPServer((sys.argv[1], int(sys.argv[2])), ConnectionHandler)
print('starting server on {}...'.format(udpserver.server_address))

udpserver.serve_forever()