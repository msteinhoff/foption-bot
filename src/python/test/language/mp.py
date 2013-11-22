# -*- coding: UTF-8 -*-
"""
$Id$

$URL$

Copyright (c) 2010 foption

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

@since Jan 9, 2011
@author Mario Steinhoff
"""

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
    