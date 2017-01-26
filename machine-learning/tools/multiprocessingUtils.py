#!/usr/bin/python

import multiprocessing, Queue

class NotYetImplementedException(Exception):
    """
        Exception to contorl flow in Task object
    """

class worker(multiprocessing.Process):
    """
        Define a worker that accesses a queue for the next task
        for multiprocessing.  The approcah i am using here is 
        that of the 2nd example in:
        http://broadcast.oreilly.com/2009/04/pymotw-multiprocessing-part-2.html
        
        Here I am deriving a custom subclass of Process.
    """
    def __init__(self, taskQueue, resultQueue):
        """
            Initialse the custom subclass
            """
        multiprocessing.Process.__init__(self)
        self.taskQueue = taskQueue
        self.resultQueue = resultQueue
    
    def run(self):
        """
            I'm deriving a custom subclass of Process so 
            should override the Process.run() method to do
            its work.
            """
        processName = self.name
        while True:
            nextTask = self.taskQueue.get()
            if nextTask == None:
                print "%s: Exiting" % processName
                break
            print "%s: %s" % (processName, nextTask)
            answer = nextTask()
            self.resultQueue.put(answer)
        return

class Task(object):
    """
        Task that is added to the queue and
        performed by the workers.
    """
    def __init__(self):
        """
            This is a dummy __init__ which must be overridden by
            subclasses.
        """
    def __call__(self):
        """
            This must be overridden with the desired task to be performed.
        """
        try:
            raise NotYetImplementedException
        except:
            print "Task objects __call__ method must be overridden."
    
    def __str__(self):
        
        """
            Dummy method again
        """

def multiprocessTaskList(taskList, cpuCount):

    tasks = multiprocessing.Queue()
    results = multiprocessing.Queue()
    nworkers = min([len(taskList), cpuCount])
    print "Creating %d workers ..." % (nworkers),
    workers = [worker(tasks, results) for i in range(nworkers)]
    print "[Done]"

    for i in range(nworkers):
        workers[i].start()

    # workers are now wating for tasks to be added to the queue
    #print "Creating %d data \'chunks\' for processing and adding to queue ..." % cpuCount,
    #tasksPerChunk = int(len(taskList) / (cpuCount))
    #print "%d tasks per chunk ..." % tasksPerChunk,

    for i in range(len(taskList)):
        #start = int(i*tasksPerChunk)
        #stop = int((i+1)*tasksPerChunk)
        tasks.put(taskList[i])
    print "[Done]"

    # Add stop value to queues, one for each process spawned
    print "Adding %d stop values to queue ..." % (nworkers),
    for i in range(nworkers):
        tasks.put(None)
    print "[Done]"

    resultsList = []

    sentinel = len(taskList)
    while sentinel:
        # get_nowait pools the queue immediately and raises Queue.Empty exception if nothing found
        try:
            resultsList.append(results.get())
            sentinel -= 1
        except Queue.Empty:
            print "Queue is empty."

    result = []

    #for i in range(resultsList):
    #    result += resultsList[i]
    print "Multiprocessing complete."
    return resultsList
