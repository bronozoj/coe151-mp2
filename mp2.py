from socket import socket, AF_INET, SOCK_DGRAM
from sys import argv

class nodeinfo:
	def __init__(self, ip, nexthop, cost):
		self.travelcost = cost
		self.destip = ip
		self.nexthopip = nexthop

	def nexthop(self):
		return self.nexthopip

	def nexthop(self, nexthop):
		self.nexthopip = nexthop
		return nexthop

	def cost(self):
		return self.cost

	def cost(self, cost):
		self.travelcost = cost
		return cost

interval = 10000
psinfinity = 100
port = 12345
filedir = ''
poisonenabled = False

buf = ''
for hana in argv:
	if buf == '':
		if hana == '-poison':
			poisonenabled = True
		elif hana[:1] == '-':
			buf = hana[1:]
	else:
		if buf == 'port':
			port = int(hana)
		elif buf == 'psinf':
			psinfinity = int(hana)
		elif buf == 'interval':
			interval = int(hana)
		elif buf == 'config':
			filedir = hana
		buf = ''

if filedir == '':
	print('Current Settings...')
	print('Interval: ' + str(interval) )
	print('Current Port: ' + str(port) )
	print('Poisoned Reverse mode: ' + str(poisonenabled) )
	print('Pseudo-infinity value: ' + str(psinfinity) )
	print('No file given.. exiting')
	exit()

sock = socket(AF_INET, SOCK_DGRAM)

sock.close()
