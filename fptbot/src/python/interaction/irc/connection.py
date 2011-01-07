'''
Created on Jan 6, 2011

@author: msteinhoff

low level network connection
'''

from core.messages import message
from socket import socket

class Connection( object ):
    """
    This class implements the low level socket required for IRC connections
    
    It opens and closes the socket and sets up socket parameters like timeout or blocking
    
    It handles data sending and receiving and adds/strips required
    control characters like \r or \n where appropriate
    """
    
    ' the socket connection '
    socket = None
    
    ' the timeout after the connection is closed '
    timeout = 180
    
    ' the receive buffer of the socket '
    recvBuffer = 4096

    ' determines whether the socket is opened '
    isOpened = False
    

    def __init__(self, timeout, buffer):
        """
        initialize connection parameters
        """
        
        if timeout != None:
            self.timeout = timeout
            
        if buffer != None:
            self.recvBuffer = buffer


    def open(self, server):
        """
        opens and connects the socket
        """
        
        try:
            log.info(message[20001], {'address': server.address, 'port': server.port})

            # open socket
            self.socket = socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((server.address, server.port))
            
            # configure socket
            self.socket.settimeout(self.timeout)
            # todo configure blocking/non-blocking
            
            # set internal state
            self.socketOpened = True
               
        except:
            #TODO checken welche exceptions hier runterkommen und entsprechendes fehlerhandling    
            log.error(message[20002])

        
    def close(self):
        """
        closes the socket
        """
        log.info(message[20006])
        
        self.socket.close()
        self.socket = None
        
        self.isSocketOpened = False
        
    
    def send(self, data):
        """
        write data into the socket
        
        @param data: the data to send, without any command characters (like \r or \n)
        """
        
        if not self.isSocketOpened:
            raise IOError("the socket is not open")
        
        try:
                self.socket.send("%s\r\n" % data)
        except:
            log.error(message[20007])


    def receive(self):
        """
        read data from the socket
        """
        
        if not self.isSocketOpened:
            raise IOError("the socket is not open")
        
        try:
            data = self.socket.recv(self.socketRecvBuffer);
            
        except socket.timeout:
            log.error(message[20004], {'seconds': self.socketTimeout})
            
            self.close()
            return

        if data == 0:
            log.error(message[20005])
            
            self.close()
            return
        
        # sanitize input
        data.replace('\r', '')
        
        return data
    