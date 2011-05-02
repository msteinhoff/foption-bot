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

@since Jan 06, 2011
@author Mario Steinhoff
"""

__version__ = '$Rev$'

from traceback import print_exc
from socket    import AF_INET, SOCK_STREAM
from asyncore  import loop
from asynchat  import async_chat

from core.config             import Config
from interaction.interaction import Interaction
from interaction.irc.message import Message
from interaction.irc.source  import ClientSource
from interaction.irc.command import *
from interaction.irc.channel import User
from interaction.irc.networks.quakenet import WhoisAuthReply

CRLF = '\x0D\x0A'

class Client(Interaction, async_chat):
    """
    Provide a RFC 2812 compilant IRC client implementation using asyncore.
    """
    
    def __init__(self, bot):
        """
        Initialize the IRC client.
        
        @param bot: The bot instance that this client should use.
        """
        
        Interaction.__init__(self, bot)
        async_chat.__init__(self)
        
        self.set_terminator(CRLF)
        
        self._commands = {}
        self._modules = {}
        
        self.bot.register_config(ClientConfig)

        self.config = self.bot.get_config(ClientConfig.identifier)
        self.logger = self.bot.get_logger(ClientConfig.identifier)
        
        self.me = User(
            ClientSource(
                self.config.get('nickname'),
                self.config.get('ident')
            ),
            self.config.get('realname')
        )
        
        self.register_commands()
        self.load_modules()

    """-------------------------------------------------------------------------
    Protocol commands
    -------------------------------------------------------------------------"""
    def register_commands(self):
        """
        Register default command handlers that implement protocol
        functionality.
        """
        
        commands = [
            NickCmd, UserCmd, ModeCmd, QuitCmd,
            JoinCmd, PartCmd, TopicCmd, NamesCmd, InviteCmd, KickCmd,
            PrivmsgCmd, NoticeCmd,
            MotdCmd, WhoCmd, WhoisCmd,
            PingCmd, PongCmd,
            WelcomeReply, YourHostReply, CreatedReply, MyInfoReply, BounceReply,
            MotdStartReply, MotdReply, MotdEndReply,
            AwayReply, UniqueOpIsReply, ChannelModeIsReply, InvitingReply,
            TopicReply, NoTopicReply,
            WhoisUserReply, WhoisServerReply, WhoisOperatorReply,
            WhoisIdleReply, WhoisChannelsReply, WhoisAuthReply, WhoisEndReply,
            WhoReply, WhoEndReply,
            NamesReply, NamesEndReply,
            BanListReply, BanListEndReply,
            InviteListReply, InviteListEndReply,
            ExceptListReply, ExceptListEndReply
        ]
        
        for command in commands:
            self.register_command(command)
    
    def register_command(self, command):
        """
        Register a command handler.
        
        The command will be registered by it's token. If a command with
        the same token already exists, it will be overwritten.
        
        @param command: A pointer to the handler class.
        """
        
        instance = command(self)
        
        self._commands[instance.token()] = instance
    
    def get_command(self, command):
        """
        Get a command handler.
        
        @param command: A pointer to the handler class.
        """
        
        return self._commands[command.token()]
    
    def unregister_command(self, command):
        """
        Remove a command handler.
        
        @param command: A pointer to the handler class.
        """
        
        del self._commands[command.token()]
            
    def send_command(self, command, *parameters):
        """
        Send a command.
        
        @param command: A pointer to the handler class.
        @param parameters: The command parameters.
        """
        
        self._commands[command.token()].send(*parameters)
    
    """-------------------------------------------------------------------------
    Client modules
    -------------------------------------------------------------------------"""
    def load_modules(self):
        """
        Load all configured modules.
        """
        
        for module in self.config.get('modules'):
            self.load_module(module)
    
    def load_module(self, name):
        """
        Load a client module that extends the client's functionality.
        
        This will import a python module located in interaction.irc.modules
        using python's __import__ builtin.
        
        The class that contains all the module logic must be named after
        the module name and must be in CamelCase.
        
        If the import was successful, the class is instanciated and its
        receive listeners are registered with all commands currently known.
        
        @param name: The name of the module that should be loaded.
        
        @return The module object.
        """
        
        classname  = 'interaction.irc.modules.{0}.{1}'.format(name, name.capitalize())
        
        clazz = self.bot.get_object(classname)
        
        self._modules[name] = clazz(self)
        
        for command, listener in self._modules[name].get_receive_listeners().items():
            self.get_command(command).add_receive_listener(listener)
            
        return self.get_module(name)
            
        
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
        
        This method creates a streaming socket, connects to the IRC
        server defined in the local Config-object and starts the
        asyncore event loop.
        """
        
        self.logger.info('starting client');
        
        try:
            self.logger.info('starting modules');
            
            for module_name, module in self._modules.items():
                self.logger.info('starting module %(name)s', {'name': module_name})
                module.start()
                
            self.logger.info('starting modules done');
            
            self.logger.info('connecting to %(address)s:%(port)d', {
                'address' : self.config.get('address'),
                'port'    : self.config.get('port')
            })

            self.create_socket(AF_INET, SOCK_STREAM)
            self.connect((self.config.get('address'), self.config.get('port')))
            
            self._buffer = []
            
            loop()
            
        except:
            """TODO: check which exceptions are caught here
            """
            self.logger.error('starting client failed')

    def stop(self):
        """
        Disconnect from the IRC server.
        
        This message tells asyncore to close the connection after all
        queued messages were sent.
        """
        
        self.logger.info('closing connection')
        
        self.pre_disconnect()
        
        self.close_when_done()
        
    """-------------------------------------------------------------------------
    Connection trigger
    -------------------------------------------------------------------------"""
    def pre_connect(self):
        """
        This trigger is called after the socket is opened.
        
        It will send the USER and NICK commands according to the RFC.
        The parameters are retrieved from the local Config-Object.
        
        As this method is only called once, error conditions such as
        nickname in use are catched and handled by high-level IRC commands.
        """
        
        self.logger.info('Registering connection, Nickname: {0}, Realname: {1}, Ident: {2}'.format(self.me.source.nickname, self.me.realname, self.me.source.ident))
        
        self.send_command(NickCmd, self.me.source.nickname)
        self.send_command(UserCmd, self.me.realname, self.me.source.ident)
    
    def post_connect(self):
        """
        This trigger is called after the MOTD or the NoMotdError was
        received.
        """
        
        self.logger.info('Connected to server.')
        self.logger.info('Joining channels: {0}'.format(self.config.get('channels')))
        
        self.send_command(JoinCmd, self.config.get('channels'))
    
    def pre_disconnect(self):
        """
        This trigger is called before the connection will be closed.
        """
        
        self.send_command(QuitCmd)
        
    def post_disconnect(self):
        """
        This trigger is called after the connection was closed.
        """
        
        pass

    """-------------------------------------------------------------------------
    Low-level communication
    -------------------------------------------------------------------------"""
    def receive_event(self, event):
        """
        Handle all incoming IRC events.
        
        This method is called every time an IRC event is generated by
        asyncore. It receives the Event and implements the dispatching
        for both low-level IRC functionality and bot commands based on
        IRC commands.
        
        @param event: A event instance with the message data.
        """
        
        self.logger.info('Received: <{0}> {1}: {2}'.format(event.source, event.command, event.parameter))
        
        if event.command not in self._commands:
            return
        
        try:
            self._commands[event.command].receive(event)
        except:
            print_exc()
            
        
    def send_event(self, event):
        """
        Handle all outgoing IRC events.
        
        This method creates a Message object from the Event, adds
        message separation characters to the string representation of
        the message and pushes that data to the asyncore socket.
        
        @param event: A event instance with the message data.
        """
        
        message = event.create_message()
        
        self.logger.info('Sent:     <{0}> {1}: {2}'.format(event.source, event.command, event.parameter))
        
        self.push('{0}{1}'.format(message, CRLF))
        
    """-------------------------------------------------------------------------
    Implementation of asyncore methods 
    -------------------------------------------------------------------------"""
    def handle_connect(self):
        """
        Send IRC specific commands when connecting.
        
        This method is called by asyncore after the first read or write
        event occured and will call the pre_connect hook.
        """
        
        self.pre_connect()
        
    def handle_close(self):
        """
        Close socket after connection is closed.
        """
        
        self.close()
        
        self.post_disconnect()
        
        for module_name, module in self._modules.items():
            self.logger.info('stopping module %(name)s', {'name': module_name})
            module.stop()

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
        message cleanly separated. Finally, receive_event() is called,
        where the message can be further dispatched.
        """
        
        data = self._buffer
        self._buffer = []
        
        """
        This is possible since this method gets called right after CRLF
        is detected, so there should only be one message in the buffer
        at call-time. If there is more than one element/message in the
        buffer, everthing could get screwed really hard.
        
        FIXME: find better way to do this
        """
        data = ''.join([line.strip(CRLF) for line in data])
        
        try:
            data = unicode(data, 'utf8')
        except UnicodeDecodeError:
            pass
        
        message = Message(data)
        
        self.receive_event(message.create_event())
    
class ClientConfig(Config):
    identifier = 'interaction.irc'
        
    def valid_keys(self):
        return [
            'nickname',
            'anickname',
            'realname',
            'ident',
            'address',
            'port',
            'modules',
            'channels',
        ]
    
    def default_values(self):
        return {
            'nickname'  : 'Bot',
            'anickname' : 'Bot-',
            'realname'  : 'Bot',
            'ident'     : 'bot',
            'address'   : 'irc.example.org',
            'port'      : 6667,
            'modules'   : ['usermgmt'],
            'channels'  : ['#test']
        }
