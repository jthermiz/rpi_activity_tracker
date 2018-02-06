import threading
import numpy
import time

def send_alert():	
	if send_ready.is_set():
		print('sent alert')
		send_ready.clear()
	
send_ready = threading.Event
sendthread = threading.Thread(target = send_alert)
sendthread.start()

for i in range(50):
	if numpy.random.rand() > 0.5:
		send_ready.set()	

time.sleep(1)

