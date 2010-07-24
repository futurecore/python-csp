from csp.csp import *
import random, time

@process
def customer_child(cchildout, n):
	for i in xrange(3):
		print "Customer's "+str(n)+" child sending "+str(i)
		cchildout.write(i)
		time.sleep(random.random() * 3)
	return

@process
def customer(cparentout, cchildout, n):
	for i in xrange(5):
		#print 'customer ', n, ' sending: customer '+str(i)
		print 'Customer '+str(n)+" sending "+str(i)
		Par(customer_child(cchildout, n)).start()
		cparentout.write(i)
		time.sleep(random.random() * 5)
	return

@process
def merchant(cin):
	for i in xrange(15):
		data = cin.read()
		print 'Merchant got:', data
		time.sleep(random.random() * 5)
	return

@process
def merchantswife(cin):
	for i in xrange(15):
		data = cin.read()
		print "Merchant's wife got: ", data
		time.sleep(random.random() * 4)
	return

@process
def terminator(chan):
	time.sleep(10)
	print 'Terminator is killing channel:', chan.name
	chan.poison()
	return

doomed = Channel()
doomed_children = Channel()
Par(customer(doomed, doomed_children, 1), merchant(doomed), merchantswife(doomed_children), customer(doomed, doomed_children, 2), customer(doomed, doomed_children, 3), terminator(doomed)).start()
#send5(doomed) // (recv(doomed), send52(doomed), interrupt(doomed))
