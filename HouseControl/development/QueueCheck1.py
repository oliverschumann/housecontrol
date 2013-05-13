'''
Created on 19.01.2013

@author: admin
'''
import threading, Queue
import random
from time import sleep

class BusWorker(threading.Thread): 
    Ergebnis = {} 
    ErgebnisLock = threading.Lock() 
 
    busJobsQueue = None
    
    def __init__(self, busJobsQueue, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name, args=args, kwargs=kwargs, verbose=verbose)
        BusWorker.busJobsQueue = busJobsQueue 
 
    def run(self):
        while True: 
            busJob = BusWorker.busJobsQueue.get() 
            busJob.run()
            BusWorker.busJobsQueue.task_done() 
 
 
class BusJob(object):
    sleepTime = 0
    
    def __init__(self, sleepTime=5):
        self.sleepTime = sleepTime
    
    def run(self):
        print("---------------------") 
        print ("SleepTime: %s" % (self.sleepTime))
        sleep(self.sleepTime)
        print("---------------------") 

         

         
if __name__ == '__main__':

    busJobsQueue = Queue.Queue()
    
    for a in range(5):
        time = random.randint(0, 2)
        print("time: %s" % (time))
        busJobsQueue.put(BusJob(time))
    
    print("Jobs generated")
    
    busWorkerThread = BusWorker(busJobsQueue) 
    busWorkerThread.setDaemon(True)        
    busWorkerThread.start() 
     
    while True: 
        eingabe = raw_input("> ") 
        if eingabe == "ende": 
            break 
     
     
        else: 
            time = random.randint(0, 2)
            print("time: %s" % (time))
            busJobsQueue.put(BusJob(time))
            
        
    busJobsQueue.join()
