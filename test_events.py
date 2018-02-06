

#!/usr/bin/python

import threading, time

# We'll have 3 events for indicating progress
oneThird = threading.Event()
twoThird = threading.Event()
done = threading.Event()

# This is a long running function that updates it's progress
def longProcess():
    for i in range(10):
        time.sleep(0.0001)
        if i > 3:
            oneThird.set()
        if i > 6:
            twoThird.set()
    done.set()

# Create a separate thread for the worker to work
threadWork = threading.Thread(target=longProcess)
threadWork.start()

# Wait for various events
oneThird.wait()
print('One third done!')

twoThird.wait()
print('Two thirds done!')

done.wait()
print('Done!')

