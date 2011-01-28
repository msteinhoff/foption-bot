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

from core.messages           import message
from core.config             import Config
from interaction.interaction import Interaction
from interaction.irc.user    import User
from interaction.irc.message import Message, ClientSource
from interaction.irc.commands import rfc2812

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
                "nickname"  : "Bot-test",
                "anickname" : "Bot-test-",
                "realname"  : "Bot",
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
        self.set_terminator(CRLF)
        
        self._logger = self._bot.getLogger("interaction.irc")
        self._config = self.ClientConfig(self._bot.getPersistence())
        
        self._commands = {}
        self._modules = {}
        
        self.me = User(
            ClientSource(
                self._config.get('nickname'),
                self._config.get('ident'),
                ''
            ),
            self._config.get('realname')
        )
        self.channels = []
        
        rfc2812.register_with_client(self)

    """-------------------------------------------------------------------------
    Modules
    -------------------------------------------------------------------------"""
    def register_module(self, name):
        """
        Load a module that extends the client's functionality.
        
        @param name: The name of the module that should be registered
        """
        
        moduleName = 'modules.{0}'.format(name)
        
        module = __import__(moduleName, globals(), locals(), [], -1)
        
        clazz = getattr(module, module.moduleName)
        
        self._modules[name] = clazz(self)
        
    def get_module(self, name):
        """
        Return a given module instance.
        
        @param name: The name of the module that should be returned.
        @return The module instance, a subclass of Module.
        @raise KeyError if there is no such module 
        """
        
        return self._modules[name]
        
    """-------------------------------------------------------------------------
    IRC commands
    -------------------------------------------------------------------------"""
    def register_command(self, clazz):
        """
        Register a command handler.
        
        @param clazz: A pointer to the handler class.
        """
        
        instance = clazz(self)
        
        self._commands[instance.token()] = instance
        
    def send_command(self, clazz, *parameters):
        """
        Send a command.
        
        @param clazz: A pointer to the handler class.
        @param parameters:
        """
        
        if clazz.token() not in self._commands:
            return
        
        self._commands[clazz.token()].send(*parameters)
        
    def unregister_command(self, clazz):
        """
        Remove a command handler.
        
        @param clazz: A pointer to the handler class.
        """
        del self._commands[clazz.token()]
            
    
    """-------------------------------------------------------------------------
    Channel
    -------------------------------------------------------------------------"""
    def get_channel(self, name):
        """
        Return a channel object.
        
        @param name: The name of the channel that should be returned.
        @return The channel instance.
        @raise KeyError if there is no such channel
        """
        return self.channels[name]
        
    
    """-------------------------------------------------------------------------
    Connection handling
    -------------------------------------------------------------------------"""
    def start(self):
        """
        Connect to the IRC server.
        
        This method creates a streaming socket, connects to the IRC
        server defined in the local Config-object and starts the
        asyncore event loop.  
        """
        
        self._logger.info(message[20001], {
            'address' : self._config.get('address'),
            'port'    : self._config.get('port')
        })
        
        try:
            self.pre_connect()
            
            self.create_socket(AF_INET, SOCK_STREAM)
            self.connect((self._config.get('address'), self._config.get('port')))
            
            self._buffer = []
            
            loop()
        except:
            """TODO: check which exceptions are caught here
            """
            self._logger.info.error(message[20002])

    def stop(self):
        """
        Disconnect from the IRC server.
        
        This message tells asyncore to close the connection after all
        queued messages were sent.
        """
        
        self._logger.info(message[20003])
        
        self.pre_disconnect()
        
        self.close_when_done()
        
    """-------------------------------------------------------------------------
    Connection trigger
    -------------------------------------------------------------------------"""
    def pre_connect(self):
        """
        This trigger is called before the socket is created.
        """
        pass
    
    def post_connect(self):
        """
        This trigger is called after the MOTD was received.
        """
        self.send_command(rfc2812.Join, ['#test'])
    
    def pre_disconnect(self):
        """
        This trigger is called before the connection will be closed.
        """
        pass
        
    def post_disconnect(self):
        """
        This trigger is called after the connection was closed.
        """
        pass

    """-------------------------------------------------------------------------
    Communication interface
    -------------------------------------------------------------------------"""
    def receive_irc(self, event):
        """
        Handle all incoming IRC events.
        
        This method is called every time an IRC event is generated by
        asyncore. It receives the Event and implements the dispatching
        for both low-level IRC functionality and bot commands based on
        IRC commands.
        
        @param event: A event instance with the message data.
        """
        
        self._logger.info('Received: <{0}> {1}: {2}'.format(event.source, event.command, event.parameter))        
        
        if event.command in self._commands:
            self._commands[event.command].receive(event)
        
        """
        if event.command == '376':
            self.post_connect()
        """

    def send_irc(self, event):
        """
        Handle all outgoing IRC events.
        
        This method creates a Message object from the Event, adds
        message separation characters to the string representation of
        the message and pushes that data to the asyncore socket.
        
        @param event: A event instance with the message data.
        """
        
        message = event.create_message()
        
        self._logger.info("Sent:     <{0}> {1}: {2}".format(event.source, event.command, event.parameter))
        
        self.push("{0}{1}".format(message, CRLF))
        
    """-------------------------------------------------------------------------
    Implementation of asyncore methods 
    -------------------------------------------------------------------------"""
    def handle_connect(self):
        """
        Send IRC specific commands when connecting.
        
        This method is called by asyncore after the first read or write
        event occured and will send the USER and NICK commands
        according to the RFC. The parameters are retrieved from the
        local Config-Object.
        
        As this method is only called once, error conditions such as
        nickname in use are catched and handled by receive_irc().
        """
        
        self.send_command(rfc2812.Nick, self.me.source.nickname)
        self.send_command(rfc2812.User, self.me.source.ident, self.me.realname)
        
    def handle_close(self):
        """
        Send IRC specific commands when disconnecting.
        
        TODO: sending quit does not work, check why
        """
        
        #self.send_command(rfc2812.Quit(), "i did it for the lulz mkay")

    """-------------------------------------------------------------------------
    Implementation of asynchat methods 
    -------------------------------------------------------------------------"""
    def collect_incoming_data(self, data):
        """
        Add any received data to the internal buffer.
        
        This will be called by asynchat whenever new data hits the
        socket. The data gets added to the internal buffer. The buffer
        gets cleaned as soon as found_terminator() is called.
        """
        
        self._buffer.append(data)

    def found_terminator(self):
        """
        Send event when a command terminator was found.
        
        This will be called by asynchat whenever the command terminator
        was found. It will copy all received data from the internal
        buffer and reset the buffer. Then the IRC message separator
        characters are removed from the end of the line. The message
        will be parsed into an Event object with the content of the
        message cleanly separated. Finally, receive_irc() is called,
        where the message can be further dispatched.
        """
        
        data = self._buffer
        self._buffer = []
        
        """
        This is possible since this method gets called right after CRLF
        is detected, so there should only be one message in the buffer
        at call-time. If there is more than one element/message in the
        buffer, everthing could get screwed really hard.
        
        TODO: find better way to do this
        """
        data = "".join([line.strip(CRLF) for line in data])
        
        message = Message(data)
        
        self.receive_irc(message.create_event())
