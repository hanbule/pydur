import argparse
import socket
from time import sleep, clock
from threading import Thread

knownClient = None
target = None

def handlePacket(data, addr, delay):
		global knownClient
		global target
		if delay is not None:
			sleep(delay)
		if knownClient == None:
			knownClient = addr
		if addr == knownClient:
			sock.sendto(data, target)
		elif addr == target:
			sock.sendto(data, knownClient)

def gatherArgs():
		parser = argparse.ArgumentParser(prog='pydur', description='delayed udp relay')
		parser.add_argument('localport', help='local port to bind to', type=int)
		parser.add_argument('remotehost', help='remote host to relay packets to')
		parser.add_argument('remoteport', help='remote port to relay packets to', type=int)
		parser.add_argument('-d', '--delay', help='delay to induce', type=float, default=0)
		parser.add_argument('-m', '--maxsize', help='max udp packet size', type=int, default=1024)
		args = vars(parser.parse_args())
		print(args)
		return args

if __name__ == '__main__':
		args = gatherArgs()

		target = ( args['remotehost'], args['remoteport'] )
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind(('0', args['localport']))

		while True:
			data, addr = sock.recvfrom(args['maxsize'])
			Thread(target=handlePacket, args=(data, addr, args['delay'])).start()
