import threading, os
from GlobalObjects import executeShellCommand, FILEPATH_BASH

class BusWorker(threading.Thread): 
    '''
    Nur ein BusWorker -> alle "Bus-Jobs" sollen brav nacheinander ausgefuehrt werden, auf keinen Fall zeitgleich!
    '''    
    busJobsQueue = None
    
    def __init__(self, busJobsQueue, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name, args=args, kwargs=kwargs, verbose=verbose)
        BusWorker.busJobsQueue = busJobsQueue 
 
    def run(self):
        while True: 
            busJob = BusWorker.busJobsQueue.get()
            
            busJob.runQueueJob()
            
            BusWorker.busJobsQueue.task_done() 
 

class BusJob(object):
    
    def __init__(self):
        pass
    
    def runQueueJob(self):
        pass


class Max6956BusJob(BusJob):
    
    port = None
    mode = None
    
    def __init__(self, port=None,mode=None):
        self.port = port
        self.mode = mode
        
    def runQueueJob(self):
        if(self.port != None):
            if(self.mode != None):
                commandArgs = [os.getcwd() + FILEPATH_BASH + 'max6956_switchport.sh', self.port, self.mode]
                #print("QueueJob::Max6956BusJob::> %s" % (commandArgs))
                result = str(executeShellCommand(commandArgs))

        