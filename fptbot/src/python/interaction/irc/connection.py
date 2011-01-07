"""
$Header$

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
"""


from socket import socket

from core.messages import message


class Connection( object ):
    """
    This class implements the low level socket required for IRC connections
    
    It opens and closes the socket and sets up socket parameters like timeout or blocking
    
    It handles data sending and receiving and adds/strips required
    control characters like \r or \n where appropriate
    
    please note that this implementation currently does not support SSL encrypted connections
    """
    
    
    def __init__(self, timeout=180, recvBuffer=4096):
        """
        initialize connection parameters
        
        @param timeout:    the socket timeout in seconds
        @param recvBuffer: the socket receive buffer in bytes
        """
        
        self.timeout    = timeout
        self.recvBuffer = recvBuffer
        self.isOpened   = False


    def open(self, server):
        """
        open and connect the socket
        
        @param server: a dictionary with server connection data
        
                       the dictionary should contain the following keys:
                       
                       server.address: An IP address or DNS name
                       server.port:    The port
        """
        
        if server.address == None or server.port == None:
            raise ValueError("invalid server data")
        
        try:
            log.info(message[20001], {'address': server.address, 'port': server.port})

            # open socket
            self.socket = socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((server.address, server.port))
            
            # configure socket
            self.socket.settimeout(self.timeout)
            # todo configure blocking/non-blocking
            
            # set internal state
            self.isOpened = True
               
        except:
            #TODO checken welche exceptions hier runterkommen und entsprechendes fehlerhandling    
            log.error(message[20002])

        
    def send(self, data):
        """
        write data into the socket
        
        @param data: the data to send, without any command characters (like \r or \n)
        """
        
        if not self.isOpened:
            raise IOError("the socket is not open")
        
        try:
                self.socket.send("%s\r\n" % data)
        except:
            log.error(message[20007])


    def receive(self):
        """
        read data from the socket
        """
        
        if not self.isOpened:
            raise IOError("the socket is not open")
        
        try:
            data = self.socket.recv(self.recvBuffer);
            
        except socket.timeout:
            log.error(message[20004], {'seconds': self.timeout})
            
            self.close()
            return

        if data == 0:
            log.error(message[20005])
            
            self.close()
            return
        
        # sanitize input
        data.replace('\r', '')
        
        return data


    def close(self):
        """
        close the socket
        """
        
        log.info(message[20006])
        
        self.socket.close()
        self.socket = None
        
        self.isOpened = False

