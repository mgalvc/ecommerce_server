import socketserver, atexit, sys, socket
from utils import ConnectionHandler
import netifaces as ni

my_address = 'localhost'
my_port = 8001

class UDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer): pass

udpserver = UDPServer((my_address, my_port), ConnectionHandler)
print('starting server on {}...'.format(udpserver.server_address))

udpserver.serve_forever()