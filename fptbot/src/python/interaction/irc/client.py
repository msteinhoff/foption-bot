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

import socket
import asyncore
import asynchat
import traceback

from core import runlevel
from core.config import Config
from objects.irc import User
from interaction.interaction import Interaction
from interaction.irc import commands
from interaction.irc.source import ClientSource
from interaction.irc.message import Message
from interaction.irc.networks import quakenet

#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------
CRLF = '\x0D\x0A'

#-------------------------------------------------------------------------------
# Business Logic
#-------------------------------------------------------------------------------
class Client(Interaction, asynchat.async_chat):
    RUNLEVEL = runlevel.Runlevel(
        autoboot=True,
        minimum_start=runlevel.NETWORK_INTERACTION
    )
    
    """
    Provide a RFC 2812 compilant IRC client implementation using asyncore.
    """
    
    def __init__(self, bot):
        """
        Initialize the IRC client.
        
        @param bot: The bot instance that this client should use.
        """
        
        Interaction.__init__(self, bot)
        asynchat.async_chat.__init__(self)
        
        self.set_terminator(CRLF)
        
        self._commands = {}
        self._recvname = {}
        self._recvtoken = {}
        self._modules = {}
        
        self.bot.register_config(ClientConfig)

        self.config = self.bot.get_config(ClientConfig.identifier)
        self.logger = self.bot.get_logger(ClientConfig.identifier)
        
        self.me = User(
            source=ClientSource(nickname=self.config.get('nickname'), ident=self.config.get('ident')),
            realname=self.config.get('realname')
        )
        
        self.register_commands()
        self.load_modules()

    #---------------------------------------------------------------------------
    # protocol commands
    #---------------------------------------------------------------------------
    def register_commands(self):
        """
        Register default command handlers that implement protocol
        functionality.
        """
        
        for command in commands.list:
            self.register_command(getattr(commands, command, None))
            
        for command in quakenet.list:
            self.register_command(getattr(quakenet, command, None))
    
    def register_command(self, command):
        """
        Register a command handler.
        
        The command will be registered by it's token. If a command with
        the same token already exists, it will be overwritten.
        
        @param command: A pointer to the handler class.
        """
        
        if command is None:
            return
        
        name = command.__name__
        token = command.token
        
        self.logger.debug('registering command handler: (Name=%s,IRCToken=%s)', name, token)
        
        instance = command(self)
        receiver = instance.get_receiver()
        
        self._commands[name] = instance
        self._recvname[name] = receiver
        self._recvtoken[token] = receiver
        
    def get_command(self, name):
        """
        Get a command handler.
        
        @param name: The command name.
        """
        
        return self._commands[name]
    
    def unregister_command(self, name):
        """
        Remove a command handler.
        
        @param token: The command token.
        """
        
        token = self._commands[name].token
        
        del self._commands[name]
        del self._recvname[name]
        del self._recvtoken[token]
            
    #---------------------------------------------------------------------------
    # client modules
    #---------------------------------------------------------------------------
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
        
        self.logger.debug('initializing module: %s', name)
        
        classname  = 'interaction.irc.modules.{0}.{1}'.format(name, name.capitalize())
        
        clazz = self.bot.get_object(classname)
        
        instance = clazz(self)
        
        self._modules[name] = instance
        
        for command_name, listener in instance.get_receive_listeners().items():
            self.logger.debug('registering receive listener: (Module=%s,Listener=%s)', name, command_name)
            self._recvname[command_name].add_listener(listener)
        
        self.logger.debug('initialized module: %s', name)
            
        return instance
        
    def get_module(self, name):
        """
        Return a given module instance.
        
        @param name: The name of the module that should be returned.
        @return The module instance, a subclass of Module.
        @raise KeyError if there is no such module 
        """
        
        return self._modules[name]
        
    #---------------------------------------------------------------------------
    # connection handling
    #---------------------------------------------------------------------------
    def _start(self):
        """
        Connect to the IRC server.
        
        This method creates a streaming socket, connects to the IRC
        server defined in the local Config-object and starts the
        asyncore event loop.
        
        Implementation of Subsystem.start()
        """
        
        self.logger.info('starting client')
        
        try:
            self.logger.info('starting modules')
            
            for module_name, module in self._modules.items():
                try:
                    self.logger.info('starting module %s', module_name)
                    module.start()
                except Exception as msg:
                    self.logger.error('starting module %s failed: %s', module_name, msg)
                
            self.logger.info('starting modules done')
            
            self.logger.info('connecting to %s:%d', self.config.get('address'), self.config.get('port'))

            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect((self.config.get('address'), self.config.get('port')))
            
            self._buffer = []
            
            asyncore.loop()
            
        except Exception as msg:
            #TODO: check which exceptions are caught here
            #TODO  print errors
            self.logger.error('starting client failed: %s', msg)

    def _stop(self):
        """
        Disconnect from the IRC server.
        
        This message tells asyncore to close the connection after all
        queued messages were sent.
        
        Implementation of Subsystem.stop()
        """
        
        self.logger.info('stopping client')
        
        self.pre_disconnect()
        
        self.close_when_done()
        
    #---------------------------------------------------------------------------
    # connection trigger
    #---------------------------------------------------------------------------
    def pre_connect(self):
        """
        This trigger is called after the socket is opened.
        
        It will send the USER and NICK commands according to the RFC.
        The parameters are retrieved from the local Config-Object.
        
        As this method is only called once, error conditions such as
        nickname in use are catched and handled by high-level IRC commands.
        """
        
        self.logger.info('Registering connection, Nickname: %s, Realname: %s, Ident: %s', self.me.source.nickname, self.me.realname, self.me.source.ident)
        
        nick = self.get_command('Nick').get_sender()
        nick.nickname = self.me.source.nickname
        
        user = self.get_command('User').get_sender()
        user.ident = self.me.source.ident
        user.realname = self.me.realname
        
        nick.send()
        user.send()
    
    def post_connect(self):
        """
        This trigger is called after the MOTD or the NoMotdError was
        received.
        """
        
        channels = self.config.get('channels')
        
        self.logger.info('Connected to server.')
        self.logger.info('Joining channels: %s', ','.join(channels))
        
        join = self.get_command('Join').get_sender()
        join.channels = channels
        join.send()
        
        self._running()
    
    def pre_disconnect(self):
        """
        This trigger is called before the connection will be closed.
        """
        
        self.get_command('Quit').get_sender().send()
        
    def post_disconnect(self):
        """
        This trigger is called after the connection was closed.
        """
        
        self._halted()

    #---------------------------------------------------------------------------
    # low-level communication
    #---------------------------------------------------------------------------
    def receive_event(self, event):
        """
        Handle all incoming IRC events.
        
        This method is called every time an IRC event is generated by
        asyncore. It receives the Event and implements the dispatching
        for both low-level IRC functionality and bot commands based on
        IRC commands.
        
        @param event: A event instance with the message data.
        """
        
        self.logger.info('Received: <%s> %s: %s', event.source, event.command, event.parameter)
        
        try:
            receiver = self._recvtoken[event.command]
        except KeyError:
            return
        
        try:
            receiver.receive(event)
        except:
            traceback.print_exc()
    
    def send_event(self, event):
        """
        Handle all outgoing IRC events.
        
        This method creates a Message object from the Event, adds
        message separation characters to the string representation of
        the message and pushes that data to the asyncore socket.
        
        @param event: A event instance with the message data.
        """
        
        message = event.create_message()
        
        self.logger.info('Sent:     <%s> %s: %s', event.source, event.command, event.parameter)
        
        self.push('{0}{1}'.format(message, CRLF))
        
    #---------------------------------------------------------------------------
    # asyncore implementation
    #---------------------------------------------------------------------------
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
            try:
                self.logger.info('stopping module %s', module_name)
                module.stop()
            except Exception as msg:
                self.logger.error('stopping module %s failed: %s', module_name, msg)

    #---------------------------------------------------------------------------
    # asynchat implementation
    #---------------------------------------------------------------------------
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




