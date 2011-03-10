'''
Created on Jan 9, 2011

@author: msteinhoff
'''

from multiprocessing import Process, Pipe
from random import seed, choice
from time import sleep

class Thread(object):
    
    def __init__(self, name, pipe):
        self.name = name
        self._pipe = pipe
        
    def sendMessage(self, target, data):
        message = {}
        message['source'] = self.name
        message['target'] = target
        message['data'] = data
        
        self._pipe.send(message)
        
    def recvMessage(self):
        msg = self._pipe.recv()
        
        if len(msg) > 0:
            return msg
        

class ProcessOne(Thread):
    def __init__(self, pipe):
        Thread.__init__(self, 'one', pipe)
    
        while True:
            msg = self.recvMessage()
            
            print "From %s to %s: %s" % (msg['source'], msg['target'], msg['data']) 
            
            if msg['source'] == "two" and msg['data'] == "foo":
                self.sendMessage(msg['source'], 'bar')

class ProcessTwo(Thread):
    def __init__(self, pipe):
        Thread.__init__(self, 'two', pipe)
    
        while True:
            msg = self.recvMessage()
            
            print "Two: %s" % msg['data']
            
            self.sendMessage('one', 'foo') 
            
            if msg['source'] == "one" and msg['data'] == "bar":
                self.sendMessage(msg['source'], 'ok')

def startProcess(f):
    dispatcher_pipe, process_pipe = Pipe()
    
    process = Process(target=f, args=(process_pipe, ))
    process.start()
    
    return {'process': process, 'pipe': dispatcher_pipe}



if __name__ == '__main__':
    print "main start"

    pr = {}
    pr['a'] = startProcess(ProcessOne)
    pr['b'] = startProcess(ProcessTwo)

    while True:
        print "loop"
        # retrieve from all processes
        msgs = [pr[p]['pipe'].recv() for p in pr]
        print msgs
        
        [pr[msg['target']]['pipe'].send(msg['data']) for msg in msgs if len(msgs['data']) > 0 and msg['target'] in pr]

    print "main stop"
    