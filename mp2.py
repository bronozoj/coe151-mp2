from socket import socket, AF_INET, SOCK_DGRAM
from sys import argv, stdout
from threading import Thread
from time import sleep

class sendnodes(Thread):
	toexit = False
	def run(self):
		while(1):
			if sender.toexit:
				print('byeee')
				exit()
			print('\nRouting Table')
			print('+-----------------------+-----------------------+------+')
			print('|      Dest Address     |   Next Hop Address    | Cost |')
			print('+-----------------------+-----------------------+------+')
			for hana in routing_table:
				print('| %-21s | %-21s | %-4d |' % (hana.destaddress(), hana.nextaddress(), hana.getCost()) )
			print('+-----------------------+-----------------------+------+')
			dva = [hana for hana in costlist if hana.tuple() != (ip,port)]
			for hana in dva:
				dataout = ''
				for song in routing_table:
					if poisonenabled and hana.tuple() == song.nextaddress():
						dataout += ('%s %d ' % song.desttuple() ) + ('%d\n' % psinfinity)
					else:
						dataout += ('%s %d ' % song.desttuple() ) + ('%d\n' % song.getCost())
				val = sock.sendto(dataout.encode(stdout.encoding), hana.tuple())
				print(str(val) + ' bytes sent to ' + hana.address())
			sleep(3);

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
		hana = item.split(' ')
		if(len(hana) != 3):
			print('Cost formatting error.. exiting')
			exit()
		try:
			if selfaddress[0] != '127.0.0.1' and hana[0] == '127.0.0.1':
				hana[0] = ip
			if selfaddress == (hana[0],int(hana[1])):
				hana[2] = '0'
			song = nodecost((hana[0], int(hana[1])), int(hana[2]))
			listout.append(song)
		except ValueError:
			print('Cost file data error.. exiting')
			exit()
	return listout	

interval = 10000
psinfinity = 100
port = 12345
filedir = ''
ip = ''
poisonenabled = False
costfile = 0
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

if ip == '':
	ip = '127.0.0.1'

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

costlist = costparser(costfile.readlines(), (ip, port))

print('\nCost Table for Current Nodes')
print('+-----------------+-------+------+')
print('|     Address     | Port  | Cost |')
print('+-----------------+-------+------+')
for hana in costlist:
	print('| %-15s | %5d | %-4d |' % (hana.ip(), hana.port(), hana.getCost()) )
	if hana.tuple() == (ip, port):
		song = nodeinfo( hana.tuple(), hana.tuple(), 0)
	else:
		song = nodeinfo( hana.tuple(), hana.tuple(), psinfinity)
	routing_table.append(song)
print('+-----------------+-------+------+')

sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(('', port))

sender = sendnodes()
sender.daemon = True
sender.start()
sender.toexit = False

try:

	while(1):
		payload, source = sock.recvfrom(10240)
		sourcecost = list(hana for hana in costlist if hana.tuple() == source)
		if len(sourcecost) != 1:
			print('Sketchy source sent data')
			continue
		sourcecost = sourcecost[0].getCost()
		sourcetable = costparser(payload.decode(stdout.encoding).rstrip().split('\n'), ('',0))
		sourceselfcost = list(hana for hana in sourcetable if hana.tuple() == source)
		if len(sourceselfcost) != 1:
			print('Sketchy data from neighbor')
			continue
		sourceselfcost = sourceselfcost[0].getCost()
		'''
		print('\nCost Table for %s:%d Nodes' % source)
		print('+-----------------+-------+------+')
		print('|     Address     | Port  | Cost |')
		print('+-----------------+-------+------+')
		#sourcetable.remove(sourceselfcost)
		for hana in sourcetable:
			print('| %-15s | %5d | %-4d |' % (hana.ip(), hana.port(), hana.getCost()) )
			#song = nodeinfo( hana.tuple(), hana.tuple(), psinfinity)
			#routing_table.append(song)
		print('+-----------------+-------+------+')
		'''

		for num, hana in enumerate(routing_table):
			dva = list([song for song in sourcetable if song.tuple() == hana.desttuple()])
			if(len(dva) != 1):
				continue
			song = dva[0]
			if hana.desttuple() == (ip, port):
				print('its me')
				pass
			elif hana.nexttuple() == source:
				print(('update %s:%d with ' % hana.desttuple()) + str(song.getCost()))
				cam = nodeinfo(hana.desttuple(), source, song.getCost() + sourcecost + sourceselfcost)
				routing_table[num] = cam
			elif hana.getCost() > (song.getCost() + sourcecost + sourceselfcost):
				cam = nodeinfo(hana.desttuple(), source, song.getCost() + sourcecost + sourceselfcost)
				routing_table[num] = cam
			sourcetable.remove(song)

		for hana in sourcetable:
			print('wat')
			song = nodeinfo(hana.tuple(), source, hana.getCost() + sourcecost + sourceselfcost)
			routing_table.append(song)
		'''
		for hana in costlist:
			#print('shit %s:%d vs %s:%d' % (hana.ip(), hana.port(), ip, port))
			if hana.ip() == ip and port == hana.port():
				
				print('buttdick')
		'''
		#sleep(5)
except KeyboardInterrupt:
	sender.toexit = True
	print('\nRouting Table')
	print('+-----------------------+-----------------------+------+')
	print('|      Dest Address     |   Next Hop Address    | Cost |')
	print('+-----------------------+-----------------------+------+')
	for hana in routing_table:
		print('| %-21s | %-21s | %-4d |' % (hana.destaddress(), hana.nextaddress(), hana.getCost()) )
	print('+-----------------------+-----------------------+------+')
	dva = [hana for hana in costlist if hana.tuple() != (ip,port)]
	for hana in dva:
		dataout = ''
		for song in routing_table:
			if song.desttuple() == (ip,port):
				dataout += ('%s %d ' % song.desttuple() ) + ('%d\n' % psinfinity)
			elif poisonenabled and hana.tuple() == song.nextaddress():
				dataout += ('%s %d ' % song.desttuple() ) + ('%d\n' % psinfinity)
			else:
				dataout += ('%s %d ' % song.desttuple() ) + ('%d\n' % song.getCost())
		print(dataout)
		val = sock.sendto(dataout.encode(stdout.encoding), hana.tuple())
		print(str(val) + ' bytes sent to ' + hana.address())
	sock.close()
	print('nope.. exiting')


sock = socket(AF_INET, SOCK_DGRAM)

sock.close()
