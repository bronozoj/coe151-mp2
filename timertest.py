from threading import Timer, Thread
from time import sleep

def sendnodes():
	print('send nodes')
	if dont:
		global sender
		sender = Timer(1,sendnodes)
		sender.start()

dont = True
sender = Timer(1,sendnodes)
sender.start()

try:
	while 1:
		pass

except KeyboardInterrupt:	
	sender.cancel()
	dont=False
	sleep(5)
