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

@since Jan 14, 2011
@author Mario Steinhoff
"""

__version__ = "$Rev$"

class Command(object):
    """
    A IRC client command.
    """
    
    def __init__(self, client):
        self._client = client
        
        self._receive_listener = []
    
    @staticmethod
    def token(self):
        raise NotImplementedError
    
    def add_receive_listener(self, callback):
        self._receive_listener.append(callback)
        
    def receive(self, event):
        self._receive(event)
        [callback(event) for callback in self._receive_listener]
    
    def send(self, *args):
        self._send(*args)

    def _receive(self, event):
        pass
    
    def _send(self, *args):
        pass

class CommandListener(object):
    """
    A listener that will be notified from client commands.
    """
    
    def receive(self, event):
        raise NotImplementedError
    
    def send(self, event):
        raise NotImplementedError
