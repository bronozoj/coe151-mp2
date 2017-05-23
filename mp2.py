from socket import socket, AF_INET, SOCK_DGRAM
from sys import argv, stdout
from threading import Thread, Timer
from time import sleep

def sendingthread():
	tabledump()
	if active:
		global sender
		sender = Timer(interval, sendingthread)
		sender.start()

def tabledump():
	print('\nRouting Table')
	print('+-----------------------+-----------------------+------+')
	print('|      Dest Address     |   Next Hop Address    | Cost |')
	print('+-----------------------+-----------------------+------+')
	for item in routing_table:
		print('| %-21s | %-21s | %-4d |' % (item.destaddress(), item.nextaddress(), item.getCost()) )
	print('+-----------------------+-----------------------+------+')
	cost = [item for item in costlist if item.tuple() != (ip,port)]
	for item in cost:
		dataout = ''
		for entry in routing_table:
			if poisonenabled and item.tuple() == entry.nextaddress():
				dataout += ('%s %d ' % entry.desttuple() ) + ('%d\n' % psinfinity)
			else:
				dataout += ('%s %d ' % entry.desttuple() ) + ('%d\n' % entry.getCost())
		val = sock.sendto(dataout.encode(stdout.encoding), item.tuple())
		print(str(val) + ' bytes sent to ' + item.address())

def exitmessage(message):
	print(message)
	print('Run this script without arguments for help')
	exit()

class nodeinfo:
	def __init__(self, dest, nexthop, cost):
		self.travelcost = cost
		self.destip = dest[0]
		self.destport = dest[1]
		self.nextip = nexthop[0]
		self.nextport = nexthop[1]
		self.cost = min(cost, psinfinity)
	def nexthop(self):
		return self.nextip + ':' + str(self.nextport)
	def nexttuple(self):
		return (self.nextip, self.nextport)
	def desttuple(self):
		return (self.destip, self.destport)
	def destaddress(self):
		return self.destip + ':' + str(self.destport)	
	def nextaddress(self):
		return self.nextip + ':' + str(self.nextport)
	def updatehop(self, nexthop, cost):
		if self.nexthoptuple() != nexthop:
			self.nextip = nexthop[0]
			self.nextport = nexthop[1]
		self.cost = min(cost, psinfinity)
		return
	def getCost(self):
		return self.cost
	def destip(self):
		return self.destip

class nodecost:
	def __init__(self, address, cost):
		self.travelcost = min(cost, psinfinity)
		self.destip = address[0]
		self.destport = int(address[1])
	def getCost(self):
		return self.travelcost
	def ip(self):
		return self.destip
	def port(self):
		return self.destport
	def tuple(self):
		return (self.destip, self.destport)
	def address(self):
		return self.destip + ':' + str(self.destport)

def costparser(datain, selfaddress):
	listout = []
	for item in datain:
		buf = item.split(' ')
		if(len(buf) != 3):
			print('Cost formatting error.. exiting')
			exit()
		try:
			if selfaddress[0] != '127.0.0.1' and buf[0] == '127.0.0.1':
				buf[0] = ip
			if selfaddress == (buf[0],int(buf[1])):
				buf[2] = '0'
			item = nodecost((buf[0], int(buf[1])), int(buf[2]))
			listout.append(item)
		except ValueError:
			print('Cost file data error.. exiting')
			exit()
	return listout	

interval = 10
psinfinity = 100
port = 12345
filedir = ''
ip = ''
poisonenabled = False
costfile = 0
routing_table = []
verbose = False

buf = ''
if(len(argv) == 1):
	print('Usage functions is under construction :p')
	exit()
for arg in argv[1:]:
	if buf == '':
		if arg == '--poison':
			poisonenabled = True
		elif arg == '--verbose':
			verbose = True
		elif len(arg) > 2 and arg[:2] == '--':
			buf = arg[2:]
		else:
			exitmessage('Stray argument ' + arg)
	else:
		if buf == 'port':
			port = int(arg)
		elif buf == 'pseudo':
			psinfinity = int(arg)
		elif buf == 'period':
			interval = int(arg)
		elif buf == 'config':
			filedir = arg
		elif buf == 'ip':
			ip = arg
		else:
			exitmessage('Unknown option --' + buf)
		buf = ''

if ip == '':
	ip = '127.0.0.1'

print('Current Settings...')
print('Interval: ' + str(interval) + ' seconds')
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

costlist = costparser(costfile.readlines(), (ip, port))

print('\nCost Table for Current Nodes')
print('+-----------------+-------+------+')
print('|     Address     | Port  | Cost |')
print('+-----------------+-------+------+')
for neighbor in costlist:
	print('| %-15s | %5d | %-4d |' % (neighbor.ip(), neighbor.port(), neighbor.getCost()) )
	if neighbor.tuple() == (ip, port):
		entry = nodeinfo( neighbor.tuple(), neighbor.tuple(), 0)
	else:
		entry = nodeinfo( neighbor.tuple(), neighbor.tuple(), psinfinity)
	routing_table.append(entry)
print('+-----------------+-------+------+')

sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(('', port))

active = True
sender = Timer(interval, sendingthread)
sender.start()

try:

	while(1):
		payload, source = sock.recvfrom(10240)
		sourcecost = list(neighbor for neighbor in costlist if neighbor.tuple() == source)
		if len(sourcecost) != 1:
			print('Sketchy source sent data')
			continue
		sourcecost = sourcecost[0].getCost()
		sourcetable = costparser(payload.decode(stdout.encoding).rstrip().split('\n'), ('',0))
		sourceselfcost = list(item for item in sourcetable if item.tuple() == source)
		if len(sourceselfcost) != 1:
			print('Sketchy data from neighbor')
			continue
		sourceselfcost = sourceselfcost[0].getCost()
		if verbose:
			print('\nCost Table for %s:%d Nodes' % source)
			print('+-----------------+-------+------+')
			print('|     Address     | Port  | Cost |')
			print('+-----------------+-------+------+')
			for item in sourcetable:
				print('| %-15s | %5d | %-4d |' % (item.ip(), item.port(), item.getCost()) )
			print('+-----------------+-------+------+')

		for num, entry in enumerate(routing_table):
			item = list([item for item in sourcetable if item.tuple() == entry.desttuple()])
			if(len(item) != 1):
				continue
			item = item[0]
			if entry.nexttuple() == source:
				cam = nodeinfo(entry.desttuple(), source, item.getCost() + sourcecost + sourceselfcost)
				routing_table[num] = cam
			elif poisonenabled and entry.getCost() == psinfinity and entry.nexttuple() != source:
				pass
			elif entry.getCost() > (item.getCost() + sourcecost + sourceselfcost):
				cam = nodeinfo(entry.desttuple(), source, item.getCost() + sourcecost + sourceselfcost)
				routing_table[num] = cam
			sourcetable.remove(item)

		for item in sourcetable:
			entry = nodeinfo(item.tuple(), source, item.getCost() + sourcecost + sourceselfcost)
			routing_table.append(entry)

except KeyboardInterrupt:
	active = False
	sender.cancel()
	selfentry = [(number, item) for (number, item) in enumerate(routing_table) if item.desttuple() == (ip, port)]
	for number, item in selfentry:
		routing_table[number] = nodeinfo( (ip, port), (ip,port), psinfinity)
	tabledump()
	sock.close()
	print('nope.. exiting')
