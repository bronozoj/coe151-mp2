from socket import socket, AF_INET, SOCK_DGRAM
from sys import argv
from threading import Thread
from time import sleep

class sendnodes(Thread):
	def run(self):
		while(1):
			print('\nCost Table for Current Nodes')
			print('+-----------------+-------+------+')
			print('|     Address     | Port  | Cost |')
			print('+-----------------+-------+------+')
			for hana in costlist:
				print('| %-15s | %5d | %-4d |' % (hana.ip(), hana.port(), hana.cost()) )
				song = nodeinfo('%s:%d' % (hana.ip(),hana.port()), '%s:%d' % (hana.ip(),hana.port()), psinfinity)
			print('+-----------------+-------+------+')
			sleep(3);

#	def quit(self):
#		print('thread exiting')

def exitmessage(message):
	print(message)
	print('Run this script without arguments for help')
	exit()

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

	def ip(self):
		return self.destip

class nodecost:
	def __init__(self, ip, port, cost):
		if cost > psinfinity:
			cost = psinfinity
		self.travelcost = cost
		self.destip = ip
		self.destport = port

	def cost(self):
		return self.travelcost

	def cost2(self, value):
		if value > psinfinity:
			value = psinfinity
		self.travelcost = value

	def ip(self):
		return self.destip

	def port(self):
		return self.destport

interval = 10000
psinfinity = 100
port = 12345
filedir = ''
ip = ''
poisonenabled = False
costfile = 0
costlist = []
routing_table = []

buf = ''
if(len(argv) == 1):
	print('Usage functions is under construction :p')
	exit()
for hana in argv[1:]:
	if buf == '':
		if hana == '--poison':
			poisonenabled = True
		elif len(hana) > 2 and hana[:2] == '--':
			buf = hana[2:]
		else:
			exitmessage('Stray argument ' + hana)
	else:
		if buf == 'port':
			port = int(hana)
		elif buf == 'pseudo':
			psinfinity = int(hana)
		elif buf == 'period':
			interval = int(hana)
		elif buf == 'config':
			filedir = hana
		elif buf == 'ip':
			ip = hana
		else:
			exitmessage('Unknown option --' + buf)
		buf = ''


print('Current Settings...')
print('Interval: ' + str(interval/1000) + ' seconds')
print('Current Port: ' + str(port) )
print('Poisoned Reverse mode: ' + str(poisonenabled) )
print('Pseudo-infinity value: ' + str(psinfinity) )

if filedir == '':
	print('No file given.. exiting')
	exit()

try:
	costfile = open(filedir)
except IOError:
	print('File reading for cost cannot be opened.. exiting')
	print('Run this script without arguments for help')
	exit()

for buf in costfile.readlines():
	hana = buf.split(None, 3)
	if(len(hana) != 3):
		print('Cost file formatting error.. exiting')
		print('Run this script without arguments for help')
		exit()
	try:
		if ip != '' and hana[0] == '127.0.0.1':
			hana[0] = ip
		if '%s:%s' %(hana[0], hana[1]) == '%s:%s' % (ip, port):
			hana[2] = '0'
		song = nodecost(hana[0], int(hana[1]), int(hana[2]))
	except ValueError:
		print('Cost file data error.. exiting')
		exit()
	
	costlist.append(song)
		
	#print(buf)

#print('\nCost Table for Current Nodes')
#print('+-----------------+-------+------+')
#print('|     Address     | Port  | Cost |')
#print('+-----------------+-------+------+')
#for hana in costlist:
#	print('| %-15s | %5d | %-4d |' % (hana.ip(), hana.port(), hana.cost()) )
#	song = nodeinfo('%s:%d' % (hana.ip(),hana.port()), '%s:%d' % (hana.ip(),hana.port()), psinfinity)
#print('+-----------------+-------+------+')

try:
	sender = sendnodes()
	sender.daemon = True
	sender.start()

	while(1):
	
		print('dickbutt')
		for hana in costlist:
			#print('shit %s:%d vs %s:%d' % (hana.ip(), hana.port(), ip, port))
			if hana.ip() == ip and port == hana.port():
				costlist[costlist.index(hana)].cost2(hana.cost() + 1)
				print('buttdick')
		sleep(5)
except KeyboardInterrupt:
	print('nope.. exiting')


sock = socket(AF_INET, SOCK_DGRAM)

sock.close()
