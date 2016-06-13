import argparse
import socket
from time import sleep, time, clock
from threading import Thread

knownClient = None
target = None
lastComm = None


def handlePacket(data, addr, delay):
		global knownClient
		global target

		if delay is not None:
			sleep(delay)

		if knownClient == None:
			knownClient = addr
			postMsg('knownClient={}'.format(addr))

		if addr == knownClient:
			sock.sendto(data, target)
		elif addr == target:
			sock.sendto(data, knownClient)
		else:
			postMsg('packet came from unknown source... dropping')

def watchdog():
	global lastComm
	global knownClient
	while True:
		sleep(.250)
		if lastComm is not None:
			v = time() - lastComm
			if v > 5 and knownClient is not None:
				knownClient = None
				postMsg('client reset')

def postMsg(msg):
	print('[ {} ] {}'.format(clock(), msg))

def gatherArgs():
		parser = argparse.ArgumentParser(prog='pydur', description='delayed udp relay')
		parser.add_argument('localport', help='local port to bind to', type=int)
		parser.add_argument('remotehost', help='remote host to relay packets to')
		parser.add_argument('remoteport', help='remote port to relay packets to', type=int)
		parser.add_argument('-d', '--delay', help='delay to induce', type=float, default=0)
		parser.add_argument('-m', '--maxsize', help='max udp packet size', type=int, default=1024)
		args = vars(parser.parse_args())
		postMsg('starting with: {}'.format(args))
		return args


class udpRelay:

	def __init__(self):
		self.args = gatherArgs()
		self.knownClient = None
		self.target = ( self.args['remotehost'], self.args['remoteport'] )
		self.lastComm = None

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind(('0', self.args['localport']))

		Thread(target=self.watchdog, args=()).start()

		self.listenLoop()

	def handlePacket(self, data, addr, delay):
		if delay is not None:
			sleep(delay)

		if self.knownClient == None:
			self.knownClient = addr
			postMsg('knownClient={}'.format(addr))

		if addr == self.knownClient:
			self.sock.sendto(data, self.target)
		elif addr == self.target:
			self.sock.sendto(data, self.knownClient)
		else:
			postMsg('packet came from unknown source... dropping')

	def watchdog(self):
		while True:
			sleep(.250)
			if self.lastComm is not None:
				v = time() - self.lastComm
				if v > 5 and self.knownClient is not None:
					self.knownClient = None
					postMsg('client reset')

	def listenLoop(self):
		while True:
			data, addr = self.sock.recvfrom(self.args['maxsize'])
			self.lastComm = time()
			Thread(target=self.handlePacket, args=(data, addr, self.args['delay'])).start()



if __name__ == '__main__':
	relay = udpRelay()

#		args = gatherArgs()
#
#		target = ( args['remotehost'], args['remoteport'] )
#		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#		sock.bind(('0', args['localport']))
#
#		Thread(target=watchdog, args=()).start()
#
#		while True:
#			data, addr = sock.recvfrom(args['maxsize'])
#			lastComm = time()
#			Thread(target=handlePacket, args=(data, addr, args['delay'])).start()
