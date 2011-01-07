'''
Created on Jan 6, 2011

@author: msteinhoff

Implements a IRC client according to RFC 2812

this list describes which messages defined by RFC 2812 are implemented: 

   3.  Message Details ............................................   9
      3.1  Connection Registration ................................  10
         3.1.1  Password message ..................................  10    - not needed
         3.1.2  Nick message ......................................  10    - needed
         3.1.3  User message ......................................  11    - needed
         3.1.4  Oper message ......................................  12    - not needed
         3.1.5  User mode message .................................  12    - needed
         3.1.6  Service message ...................................  13    - not needed
         3.1.7  Quit ..............................................  14    - needed
         3.1.8  Squit .............................................  15    - not needed
      3.2  Channel operations .....................................  15
         3.2.1  Join message ......................................  16    - needed
         3.2.2  Part message ......................................  17    - needed
         3.2.3  Channel mode message ..............................  18    - needed
         3.2.4  Topic message .....................................  19    - needed
         3.2.5  Names message .....................................  20    - needed
         3.2.6  List message ......................................  21    - not needed
         3.2.7  Invite message ....................................  21    - not needed (maybe implemented in the future)
         3.2.8  Kick command ......................................  22    - needed
      3.3  Sending messages .......................................  23
         3.3.1  Private messages ..................................  23    - needed
         3.3.2  Notice ............................................  24    - needed
      3.4  Server queries and commands ............................  25
         3.4.1  Motd message ......................................  25    - needed
         3.4.2  Lusers message ....................................  25    - not needed
         3.4.3  Version message ...................................  26    - not needed
         3.4.4  Stats message .....................................  26    - not needed
         3.4.5  Links message .....................................  27    - not needed
         3.4.6  Time message ......................................  28    - not needed
         3.4.7  Connect message ...................................  28    - not needed
         3.4.8  Trace message .....................................  29    - not needed
         3.4.9  Admin command .....................................  30    - not needed
         3.4.10 Info command ......................................  31    - not needed
      3.5  Service Query and Commands .............................  31
         3.5.1  Servlist message ..................................  31    - not needed
         3.5.2  Squery ............................................  32    - not needed
      3.6  User based queries .....................................  32
         3.6.1  Who query .........................................  32    - needed
         3.6.2  Whois query .......................................  33    - needed
         3.6.3  Whowas ............................................  34    - not needed
      3.7  Miscellaneous messages .................................  34
         3.7.1  Kill message ......................................  35    - not needed
         3.7.2  Ping message ......................................  36    - needed
         3.7.3  Pong message ......................................  37    - needed
         3.7.4  Error .............................................  37    - not needed
'''

import socket

from core.messages import *
from . import connection


class Client(object):
    

    
    ' determines whether the irc connection is established '
    isConnected = False
    
    ' determines whether the connection should be terminated  '
    terminateConnection = False
    
    '''
    User data
    
    This dictionary should contain the following keys:
    user.nickname
    user.realname
    user.ident
    '''
    user = {}
    
    '''
    Connection data
    
    This dictionary should contain the following keys:
    
    server.address: An IP address or DNS name
    server.port:    The port
    
    please note that this implementation currently does not support SSL encrypted connections
    '''
    server = {}
    
    '''
    the constructor
    '''
    def __init__(self, user, server):
        
        if not user or not server:
            raise ValueError("user and address needed")
        
        self.user   = user
        self.server = server
    
    '''
    opens the irc connection
    '''
    def connect(self):
        while True:
                ' open socket
                isStreaming = True
                
                while isStreaming:
                    if self.terminateConnection:
                        log.info(message[20003])    

                        ' close socket                                      
                        break
                        
                    data = ""
                
                    'receive
                    'parse data and dispatch to listener methods functions
        
                    while data.find('\n') != -1:
                        parts = data.split('\n', 1)
                        rawmsg = parts[0]
                        data = parts[1]
                        
                        #print str(rawmsg)
                        
                        for i in Conf.Modlist:
                            try:
                                r = re.findall(i.regexpattern,rawmsg)
                                if (r):
                                    i.handleInput(r[0])
                            except:
                                ServerSocket.send("PRIVMSG " + Conf.Channel \
                                + " :4Error in '" + str(i) + "' --> '" \
                                + str(sys.exc_info()[1]) + "'\n")
    
    
                if (Conf.Run == False):
                    break


    
    for i in Conf.Modlist:
        try:
            i.shutdown()
        except:
            pass
    
    def disconnect(self):
        pass

    '''
    aaa
    '''
    def __registerConnection(self):
        pass

    '''
    aaa
    '''
    def __msgRegistrationNick(self, nickname):
        self.socket.send("NICK %s\r\n" % nickname)
    
    '''
    aaa
    '''
    def __msgRegistrationUser(self, ident, mode, realname):
        self.socket.send("USER %s %d %s :%s\r\n" % (ident mode, realname))
    
    '''
    aaa
    '''
    def __msgRegistrationMode(self, nickname, mode):
        self.socket.send("MODE %s %s", % (nickname, mode))
    
    '''
    aaa
    '''
    def __msgRegistrationQuit(self):
        pass
    
    '''
    aaa
    '''
    def __msgChannelJoin(self):
        pass
    
    '''
    aaa
    '''
    def __msgChannelPart(self):
        pass
    
    '''
    aaa
    '''
    def __msgChannelMode(self):
        pass
    
    '''
    aaa
    '''
    def __msgChannelTopic(self):
        pass
    
    '''
    aaa
    '''
    def __msgChannelNames(self):
        pass
    
    '''
    aaa
    '''
    def __msgChannelKick(self):
        pass
    
    '''
    aaa
    '''
    def __msgMessagePrivmsg(self):
        pass
    
    '''
    aaa
    '''
    def __msgMessageNotice(self):
        pass
    
    '''
    aaa
    '''
    def __msgServerMotd(self):
        pass
    
    '''
    aaa
    '''
    def __msgUserWho(self):
        pass
    
    '''
    aaa
    '''
    def __msgUserWhois(self):
        pass
    
    '''
    aaa
    '''
    def __msgMiscPing(self):
        pass
    
    '''
    aaa
    '''
    def __msgMiscPong(self):
        pass
    
    '''
    aaa
    '''
    def __msgNick(self):
        pass
