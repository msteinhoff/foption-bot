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

@since Jan 11, 2011
@author Mario Steinhoff
"""

__version__ = '$Rev$'

import re
import time

from core.bot import BotError
from objects.principal import Role
from objects.irc import Location

#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------
MIRC_COLOR = '\x03'

#-------------------------------------------------------------------------------
# Exceptions
#-------------------------------------------------------------------------------
class ModuleError(BotError): pass
class InteractiveModuleError(ModuleError): pass
class InvalidCommandError(InteractiveModuleError): pass
class InvalidArgumentError(InteractiveModuleError): pass
class InvalidLocationError(InteractiveModuleError): pass
class InvalidRoleError(InteractiveModuleError): pass

#-------------------------------------------------------------------------------
# Business Logic
#-------------------------------------------------------------------------------
class Module(object):
    """
    Extend the IRC client's functionality.
    
    A module is loaded and instantiated by the client. An interface
    to the IRC is provided by registering callback functions for each
    IRC command needed and known by the client.
    """
    
    def __init__(self, client):
        """
        Initialize the module.
        
        This will populate the client instance in the module, so the 
        module can interact with the client.
        
        @param client: The client instance. 
        """
        
        self.client = client
        self.initialize()
        
    def __del__(self):
        self.shutdown()

    #---------------------------------------------------------------------------
    # irc interface
    #---------------------------------------------------------------------------
    def get_receive_listeners(self):
        """
        Return a mapping between commands and callback functions.
        
        This will return a dictionary with the mapping.
        - They keys are command classes
        - the values are pointers to methods provided by the class.
        
        @return list with mapping between commands and class methods   
        """
        raise NotImplementedError
    
    #---------------------------------------------------------------------------
    # state handling
    #---------------------------------------------------------------------------
    def initialize(self):
        """
        Initialization hook.
        
        This will execute additional initialization code in the module
        without overriding the constructor.
        
        Code in this method may only initialize data structures.
        This method MUST NOT start or manipulate any external entity, e.g.
        start threads, open connections, write files, etc.
        
        For manipulation, use start().
        """
        pass
    
    def shutdown(self):
        """
        Cleanup hook.
        
        This will execute additional cleanup code in the module without
        overriding the destructor.
        """
        pass
    
    def start(self):
        """
        launch hook.
        
        This will execute additional launch code needed at runtime
        without overriding the constructor.
        It will be called before any IRC connection is available.
        
        Code in this method may  start or manipulate external entities, e.g.
        start threads, open sockets or files, etc.
        
        For initialization, use initialize().
        """
        pass
    
    def stop(self):
        """
        The opposite of start().
        
        It will be called after the IRC connection was closed.
        
        Stop threads, close sockets or files, etc.
        """
        pass


class InteractiveModule(Module):
    """
    Provide a framework for user interaction.
    
    This implementation can parse Privmsg or Notice messages, that
    encapsulate bot/module commands.
    
    Each module can specify one or more keywords. Each keyword can
    either have parameters or further sub-commands. If sub-commands
    are specified, each sub-command can again have parameters.
    Parameters are defined by an arbitrary regular expression.
    
    Parameters can be defined for commands and sub-commands.
    """
    
    PATTERN_BASE = r'^\.(?P<command>{0})(\s(?P<parameter>.+)$|$)'
    PATTERN_SEPARATOR = '|'
    
    def __init__(self, client):
        """
        Initialize the Inactive Module.
        
        Generate and compile a command regex pattern to match all
        defined commands. Compile all parameter regex patterns.
        
        Cache all compiled RegexObjects and the mapping between
        commands and callback functions.
        """
        
        Module.__init__(self, client)
        
        # cache reference to usermgmt module
        if self.__class__.__name__.lower() == 'usermgmt':
            self.usermgmt = self
        else:
            self.usermgmt = self.client.get_module('usermgmt')
        
        self.identifier = self.module_identifier()
        self.command_dict = {}
        
        for command in self.init_commands():
            self.command_dict[command.keyword] = command
        
        pattern = self.PATTERN_BASE.format(
            self.PATTERN_SEPARATOR.join(self.command_dict)
        )
        
        self.module_re = re.compile(pattern, re.I)
        
        self.VALID_TOKENS = (
            self.client.get_command('Privmsg').token,
            self.client.get_command('Notice').token
         )
    
    #---------------------------------------------------------------------------
    # irc interface
    #---------------------------------------------------------------------------
    def get_receive_listeners(self):
        """
        Setup default receive listeners needed for Privmsg handling.
        """
        
        return {'Privmsg': self.parse}

    #---------------------------------------------------------------------------
    # identification and behavior
    #---------------------------------------------------------------------------
    def module_identifier(self):
        """
        Return a verbose string that identifies the module.
        
        This prefix is used when sending replies.
        
        @return An identifier, e.g. 'Rollapparillo'
        """
        
        raise NotImplementedError
    
    def init_commands(self):
        """
        Return a definition of commands/sub-commands and callbacks.
        
        The module will respond on every command defined. The commands
        must be given without the trigger character.
        
        Sub-commands are defined as ordinary commands separated by a
        space (0x20) character.
        
        Examples:
        self.add_command('roll', r'^([\d]+)(?:-([\d]+))$', Role.USER, self.roll)
        
        self.add_command('black', None, Role.USER, self.choose)
        self.add_command('white', None, Role.USER, self.choose)
        self.add_command('pink',  None, Role.USER, self.choose)
        
        self.add_command('calendar add',    '???', Role.USER, self.add)
        self.add_command('calendar delete', '???', Role.USER, self.delete)
        """
        
        raise NotImplementedError
    
    #---------------------------------------------------------------------------
    # interactive command handling
    #---------------------------------------------------------------------------
    def parse(self, event):
        """
        Parse the event and dispatch it to the actual module logic.
        
        This will check if any module command was found in the message.
        
        If no command was found, the method will return.
        
        If a command was found, the corresponding parameter RegexObject
        is retrieved and matched against the parameter raw data. If no
        RegexObject was found, the parameter data will be None.
        
        Then, the command's callback will be called with command and
        parameter data passed as arguments.
        
        This module will only accept Privmsg or Notice events. It needs
        to be activated in get_receive_listeners().

        TODO: add mirc color codes to reply
        
        @param event: The Privmsg or Notice event.
        """
        
        if event.command not in self.VALID_TOKENS:
            raise ValueError('invalid command token')
        
        #-----------------------------------------------------------------------
        # handle input
        #-----------------------------------------------------------------------
        target, message = event.parameter[0:2]
        
        message = message.strip()
        
        message_match = self.module_re.search(message)
        
        if message_match is None:
            return
        
        command = message_match.group('command')
        parameter = message_match.group('parameter') or ''
        
        location = Location.get(target)
        role = self.usermgmt.get_role(event.source.nickname)
        command_object = self.command_dict[command]
            
        #-----------------------------------------------------------------------
        # dispatch
        #-----------------------------------------------------------------------
        try:
            if not Location.valid(required=command_object.location, location=location):
                raise InvalidLocationError(command_object.location)
            
            if not Role.valid(required=command_object.role, role=role):
                raise InvalidRoleError(command_object.role)
            
            callback = command_object.callback
            parameter = command_object.match_arguments(parameter)
            
            reply = callback(event, location, command, parameter)
        
        except InvalidLocationError as required_location:
            reply = InteractiveModuleReply()
            reply.use_notice()
            reply.add_line('Befehl geht nur im {0}'.format(required_location))
        
        except InvalidRoleError as required_role:
            reply = InteractiveModuleReply()
            reply.add_line('Nicht genug rechte (benötigt: {0})'.format(required_role))
        
        except InvalidArgumentError:
            reply = InteractiveModuleReply()
            reply.add_line('usage: .{0} {1}'.format(command_object.keyword, command_object.syntaxhint))
        
        except Exception as ex:
            #Should not happen, but just in case.
            #TODO: throw stack trace
            reply = 'Es ist ein interner Fehler aufgetreten, lol opfeeeeeer!'
            
            self.client.logger.exception('Unhandled exception "{1}" thrown in {0}'.format(
                self.__class__.__name__,
                str(ex)
            ))
            
        #-----------------------------------------------------------------------
        # send reply
        #-----------------------------------------------------------------------
        if reply is not None:
            if location == Location.CHANNEL:
                target = event.parameter[0]
                
            elif location == Location.QUERY:
                target = event.source.nickname
        
        self.send_reply(target, reply)
    
    def send_reply(self, target, reply):
        """
        Send a reply to target.
        
        @param command_object: How the reply should be sent.
        @param target: The receiver of the reply.
        @param reply: The reply to send, String or Reply object.
        """
        
        if hasattr(reply, 'replies') and hasattr(reply, 'type'):
            sender = self.client.get_command(reply.type).get_sender()
            sender.target = target
            
            for reply in reply.replies:
                sender.text = '{0}: {1}'.format(self.identifier, reply)
                sender.send()
                time.sleep(0.2)
            
        else:
            sender = self.client.get_command('Privmsg').get_sender()
            sender.target = target
            sender.text = '{0}: {1}'.format(self.identifier, reply)
            sender.send()

class InteractiveModuleCommand(object):
    """
    Represent a module command that can be triggered by IRC users.
    """
    
    def __init__(self, keyword, callback, pattern=None, location=Location.CHANNEL, role=Role.USER, syntaxhint=None, help=None):
        """
        Initialize the command.

        TODO: fallback to privmsg reply instead of raising exception?
        
        @param keyword: The keyword that triggers the command.
        @param pattern: A regex pattern that defines the arguments.
        @param location: The location where the command can be executed.
        @param reply: The command the reply should be sent with.
        @param role: The role the calling user needs to have.
        @param callback: The callback function.
        """
        
        self.keyword = keyword
        self.callback = callback
        
        if pattern:
            self.pattern = re.compile(pattern, re.I)
        else:
            self.pattern = None
        
        self.location = location
        self.role = role
        
        self.syntaxhint = syntaxhint or ''
        self.help = help or ''
        
    def match_arguments(self, data):
        """
        Match and extract data according to the object's pattern.
        
        @param data: A string.
        
        @return: A tuple, the format depends on the pattern.
        
        @raise ValueError If the data is invalid.
        """
        
        if self.pattern is None:
            return None
        
        try:
            match = self.pattern.findall(data)
            arguments = match[0]
            
            # force tuple for consistent api
            if type(arguments) != tuple:
                arguments = (arguments,)
            
        # TypeError when data can not be matched
        # KeyError when no match was found
        # IndexError when no match was found
        except (TypeError):
            raise ValueError
        
        except (KeyError, IndexError):
            raise InvalidArgumentError
        
        return arguments

class InteractiveModuleReply(object):
    def __init__(self, firstline=None):
        self.use_message()
        
        if firstline == None:
            self.replies = []
        else:
            self.replies = [firstline]
        
    def add_line(self, line):
        self.replies.append(line)
        
        return self
    
    def use_notice(self):
        self.type = 'Notice'
        
    def use_message(self):
        self.type = 'Privmsg'
