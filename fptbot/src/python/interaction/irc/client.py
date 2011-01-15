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

__version__ = "$Rev$"

from socket   import AF_INET, SOCK_STREAM
from asyncore import loop
from asynchat import async_chat

from core.messages                   import message
from core.config                     import Config
from interaction.interaction         import Interaction
from interaction.irc.user            import Userlist, User
from interaction.irc.message.message import Message, Event

SPACE      = "\x20"
CRLF       = "\x0D\x0A"
MIRC_COLOR = "\x03"

class Client(Interaction, async_chat):
    """
    Provide a RFC 2812 compilant IRC client implementation using asyncore.
    """
    
    class ClientConfig(Config):
        def name(self):
            return "interaction.irc"
            
        def valid(self):
            return [
                "nickname",
                "anickname",
                "realname",
                "ident",
                "address",
                "port",
                "modules"
            ]
        
        def defaults(self):
            return {
                "nickname"  : "bot-test---",
                "anickname" : "bot-test-",
                "realname"  : "bot",
                "ident"     : "bot",
                "address"   : "de.quakenet.org",
                "port"      : 6667
            }

    def __init__(self, bot):
        """
        Initialize the IRC client.
        
        @param bot: The bot instance that this client should use.
        """
        
        Interaction.__init__(self, bot)
        async_chat.__init__(self)
        
        self._logger = self._bot.getLogger("interaction.irc")
        self._config = self.ClientConfig(self._bot.getPersistence())
        self._userlist = Userlist()
        self._modules = {}
        
        self._isConnected = False
        
        self.set_terminator(CRLF)

    def register_module(self, name):
        """
        Load a module that extends the client's functionality.
        
        @param name: The name of the module that should be registered
        """
        
        moduleName = 'modules.{0}'.format(name)
        
        module = __import__(moduleName, globals(), locals(), [], -1)
        
        clazz = getattr(module, module.moduleName)
        
        self._modules[name] = clazz()
        
    def get_module(self, name):
        """
        Return a given module instance.
        
        @param name: The name of the module that should be returned.
        @return The module instance, a subclass of Module.
        @raise KeyError if there is no such module 
        """
        
        return self._modules[name]
    
    """-------------------------------------------------------------------------
    Connection handling
    -------------------------------------------------------------------------"""
    def start(self):
        """
        Connect to the IRC server.
        """
        
        self._logger.info(message[20001], {
            'address' : self._config.get('address'),
            'port'    : self._config.get('port')
        })
        
        try:
            self.create_socket(AF_INET, SOCK_STREAM)
            self.connect((self._config.get('address'), self._config.get('port')))
            
            self._buffer = []
            
            loop()
        except:
            #TODO: check which exceptions are caught here
            self._logger.info.error(message[20002])

    def stop(self):
        """
        Disconnect from the IRC server.
        """
        
        self._logger.info(message[20003])
        self.close_when_done()

    """-------------------------------------------------------------------------
    Communication interface
    -------------------------------------------------------------------------"""
    def receive_irc(self, event):
        """
        Handle all interaction when there is protocol data received.
        Dispatch events to handler methods according to the internal
        dispatching configuration.
        
        @param event: A event instance with the message data.
        """
        
        self._logger.info('Received: <{0}> {1}: {2}'.format(event.source, event.command, event.parameter))        
        
        if event.command == 'PING':
            self.send_irc(Event(None, 'PONG', event.parameter[0:1]))
            

    def send_irc(self, event):
        """
        Handle all interaction when there is protocol data to send.
        
        Create message, Add IRC protocol control characters, send data.
        
        @param event: A event instance with the message data.
        """
        
        message = event.create_message()
        
        self._logger.info("Sent:     {0}".format(message))
        
        self.push("{0}{1}".format(message, CRLF))
        
    """-------------------------------------------------------------------------
    Implementation of asyncore methods 
    -------------------------------------------------------------------------"""
    def handle_connect(self):
        """
        Implement IRC protocol for connecting and set internal state.
        """
        
        self.send_irc(Event(None, 'NICK', [self._config.get('nickname')]))
        self.send_irc(Event(None, 'USER', [self._config.get('ident'), "0", "*", "{0}".format(self._config.get('realname'))]))
        
        self._isConnected = True
    
    def handle_close(self):
        """
        Implement IRC protocol for disconnecting and set internal state.
        """
        
        #self.send_irc(["QUIT", "i did it for the lulz mkay"])
        
        self._isConnected = False

    """-------------------------------------------------------------------------
    Implementation of asynchat methods 
    -------------------------------------------------------------------------"""
    def collect_incoming_data(self, data):
        """
        Add any received data to the internal buffer.
        """
        
        self._buffer.append(data)

    def found_terminator(self):
        """
        Send event when a command terminator was found.
        
        Strip IRC protocol control characters, parse message, create event.
        """
        
        data = self._buffer
        self._buffer = []
        
        """
        This is possible since this method gets called right after CRLF
        is detected, so there should only be one message in the buffer
        at call-time.
        If there is more than one element/message in the buffer, everthing
        could get screwed really hard.
        TODO: find better way to do this
        """
        data = "".join([line.strip(CRLF) for line in data])
        
        message = Message(data)
        
        self.receive_irc(message.create_event())
