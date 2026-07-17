import sys
import threading

import masarclient.masarClient as masarClient

def getsnapshot(counts, eid):
    for i in range(counts):
        mc.retrieveSnapshot({'eventid': eid})

def usingthread():
    thread_list = []

    for i in range(1,10):
        # Instatiates the thread
        t = threading.Thread(target=getsnapshot, args=(10,'1005'))
        # Sticks the thread in a list so that it remains accessible 
        thread_list.append(t)

    # Starts threads
    for thread in thread_list:
        thread.start()

    # This blocks the calling thread until the thread whose join() method is called is terminated.
    # From http://docs.python.org/2/library/threading.html#thread-objects
    for thread in thread_list:
        thread.join()

    print "Done with threads"

def usingsinglethread():
    getsnapshot(10,'1005')

    print "Done w/o thread"

if __name__ == "__main__":
    channel = "masarService4Test"
    mc =  masarClient.client(channel)
    if len(sys.argv) >1 and sys.argv[1] == "thread":
        usingthread()
    else:
        usingsinglethread()


