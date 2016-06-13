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

if __name__ == '__main__':
		args = gatherArgs()

		target = ( args['remotehost'], args['remoteport'] )
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind(('0', args['localport']))

		Thread(target=watchdog, args=()).start()

		while True:
			data, addr = sock.recvfrom(args['maxsize'])
			lastComm = time()
			Thread(target=handlePacket, args=(data, addr, args['delay'])).start()
