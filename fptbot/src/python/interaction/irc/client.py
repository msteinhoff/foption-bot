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

@since 06.01.2010
@author Mario Steinhoff
"""

from core.messages              import message
from interaction.irc.connection import Connection

class Client( object ):
    """
    A IRC client implementation according to RFC 2812

    this list describes which messages are implemented: 
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
     """
    
    
    """
    User data
    
    This dictionary should contain the following keys:
    """
    user = {}
    
    """
    Connection data
    """
    server = {}
    
    def __init__(self, user, server):
        """
        the constructor
        
        @param user:   A dictionary with user information, should contain the following keys:
                       nickname
                       realname
                       ident
                       
        @param server: a dictionary with server connection data, should contain the following keys:
                       address: An IP address or DNS name
                       port:    The port
        """

        """
        self.nick = "foption"
        self.anick = "fptbot"
        self.cnick = "foption"
        self.Ident = "foption"
        self.Realname = "teh slut"
        self.Channel = "#foption"
        self.Server = "irc.quakenet.org"
        self.Port = 6668
        self.admin = ["rack","whg|abc","Marrek","diggen"]
        """

        if user == None:
            raise ValueError("user data missing")
        
        if server == None:
            raise ValueError("server data missing")
        
        self.user   = user
        self.server = server
        
        self.connection  = connection.Connection()
        self.isConnected = False
        self.terminateConnection = False

    
    def connect(self):
        '''
        open the irc connection
        '''
        
        while True:
            # open socket
            
            isStreamOpened = True
            
            while isStreaming:
                if self.terminateConnection:
                    log.info(message[20003])    

                    # close socket                                      
                    break
                    
                data = ""
            
                #receive
                #parse data and dispatch to listener methods functions
                    
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
        '''
        aaa
        '''
        
        pass

    def __registerConnection(self):
        '''
        aaa
        '''
        
        pass

    def __msgRegistrationNick(self, nickname):
        '''
        aaa
        '''
        
        self.socket.send("NICK %s\r\n" % nickname)
    
    def __msgRegistrationUser(self, ident, mode, realname):
        '''
        aaa
        '''
        
        self.socket.send("USER %s %d %s :%s\r\n" % (ident mode, realname))
    
    def __msgRegistrationMode(self, nickname, mode):
        '''
        aaa
        '''
        
        self.socket.send("MODE %s %s", % (nickname, mode))
        
    
    def __msgRegistrationQuit(self):
        
        '''
        aaa
        '''
        
        pass
    
    def __msgChannelJoin(self):
        '''
        aaa
        '''
        
        pass
    
    def __msgChannelPart(self):
        '''
        aaa
        '''

        pass
    
    def __msgChannelMode(self):
        '''
        aaa
        '''
        
        pass
    
    def __msgChannelTopic(self):
        '''
        aaa
        '''

        pass
    
    def __msgChannelNames(self):
        '''
        aaa
        '''

        pass
    
    def __msgChannelKick(self):
        '''
        aaa
        '''

        pass
    
    def __msgMessagePrivmsg(self):
        '''
        aaa
        '''

        pass
    
    def __msgMessageNotice(self):
        '''
        aaa
        '''

        pass
    
    def __msgServerMotd(self):
        '''
        aaa
        '''

        pass
    
    def __msgUserWho(self):
        '''
        aaa
        '''

        pass
    
    def __msgUserWhois(self):
        '''
        aaa
        '''

        pass
    
    def __msgMiscPing(self):
        '''
        aaa
        '''

        pass
    
    def __msgMiscPong(self):
        '''
        aaa
        '''

        pass
    
    def __msgNick(self):
        '''
        aaa
        '''

        pass
