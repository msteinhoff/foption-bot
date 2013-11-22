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
class InvalidParameterError(InteractiveModuleError): pass
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
            parameter = command_object.match_parameter(parameter)
            
            request = InteractiveModuleRequest(
                event=event,
                source=event.source,
                target=target,
                message=message,
                location=location,
                role=role,
                command=command,
                parameter=parameter
            )
            
            response = callback(request)
        
        except InvalidLocationError as required_location:
            response = InteractiveModuleResponse()
            response.send_to(event.source.nickname)
            response.use_notice()
            response.add_line('Befehl {0} geht nur im {1}'.format(command, Location.string(required_location[0])))
        
        except InvalidRoleError as required_role:
            response = InteractiveModuleResponse()
            response.send_to(event.source.nickname)
            response.use_notice()
            response.add_line('Nicht genug Rechte (benötigt: {0})'.format(Role.string(required_role[0])))
        
        except InvalidParameterError:
            response = InteractiveModuleResponse()
            response.add_line('usage: .{0} {1}'.format(command_object.keyword, command_object.syntaxhint))
        
        except Exception as ex:
            response = InteractiveModuleResponse()
            response.add_line('Es ist ein interner Fehler aufgetreten, lol opfeeeeeer!')
            
            self.client.logger.exception('Unhandled exception "{1}" thrown in {0}'.format(
                self.__class__.__name__,
                str(ex)
            ))
            
        #-----------------------------------------------------------------------
        # send reply
        #-----------------------------------------------------------------------
        if response and not hasattr(response, 'target'):
            if location == Location.CHANNEL:
                response.send_to(event.parameter[0])
                
            elif location == Location.QUERY:
                response.send_to(event.source.nickname)
        
        self.send_response(response.target, response)
    
    def send_response(self, target, response):
        """
        Send a response to the target.
        
        @param target: The receiver of the response.
        @param response: The response to send.
        """
        
        if hasattr(response, 'replies') and hasattr(response, 'type'):
            sender = self.client.get_command(response.type).get_sender()
            sender.target = target
            
            for line in response.replies:
                sender.text = '{0}: {1}'.format(self.identifier, line)
                sender.send()
                time.sleep(0.2)
            
        else:
            sender = self.client.get_command('Privmsg').get_sender()
            sender.target = target
            sender.text = '{0}: {1}'.format(self.identifier, response)
            sender.send()

class InteractiveModuleCommand(object):
    """
    The static definition of an InteractiveModule command.
    
    Module commands can be triggered by other IRC clients sending
    messages in a pre-defined format. When a command is detected,
    a InteractiveModuleRequest is generated and sent to the command
    handler callback.
    
    After the callback has been finished with processing the request,
    it returns a InteractiveModuleResponse which is sent back to the
    IRC server.
    """
    
    def __init__(self, keyword, callback, pattern=None, location=Location.CHANNEL, role=Role.USER, syntaxhint=None, help=None):
        """
        Define a module command.

        @param keyword: The keyword that triggers the command.
        @param callback: The callback function that handles the command.
        @param pattern: A regex pattern that defines the command parameters.
        @param location: The location where the command can be executed.
        @param role: The role the calling user needs to have.
        @param syntaxhint: A string that is sent when using invalid parameters.
        @param help: A string that describes the command.
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
        
    def match_parameter(self, data):
        """
        Match and extract data according to the commands's pattern.
        
        @param data: The raw parameter string.
        
        @return: A tuple, the format depends on the command's pattern.
        
        @raise ValueError If the data format is invalid.
        @raise InvalidParameterError If there were no matches found.
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
            raise InvalidParameterError
        
        return arguments

class InteractiveModuleRequest(object):
    """
    The runtime request of an InteractiveModule command.
    
    A runtime request is generated each time the command is triggered
    and passed to the command handler callback.
    It contains context information about the incoming command that
    can be processed by the command handler.
    """
    
    def __init__(self, event=None, source=None, target=None, message=None, location=None, role=None, command=None, parameter=None):
        """
        Initialize a runtime request.
        
        @param event: The original event of the command.
        @param source: Who sent the command.
        @param target: Where the command was sent to.
        @param message: The raw message, extracted from the event.
        @param location: The location where the command was sent.
        @param role: The role of the user sending the command.
        @param command: The actual command name.
        @param parameter"The command parameters.
        """
        
        self.event = event
        self.source = source
        self.target = target
        self.message = message
        self.location = location
        self.role = role
        self.command = command
        self.parameter = parameter

class InteractiveModuleResponse(object):
    """
    The runtime response of an InteractiveModule command.
    
    A response is created by the command handler callback and
    contains 1-n reply lines.
    """
    def __init__(self, firstline=None):
        """
        Initialize a runtime response.
        
        The default IRC command used is Privmsg.
        
        @param firstline: The first line of the response.
        @param target: The target to send the response to.
        """
        
        self.use_message()
        
        self.replies = []
        
        if firstline:
            self.replies.append(firstline)
            
    def add_line(self, line):
        """
        Add another line to the reponse.
        
        @param line: The text to add.
        """
        self.replies.append(line)
    
    def send_to(self, target):
        """
        Override the target to send the response to.
        
        The target where the response is sent to is computed by the
        InteractiveModule framework. It can be overridden using this
        method.
        
        @param target: A valid channel or nickname to send the response to.
        """
        
        self.target = target
    
    def use_message(self):
        """
        Use the Privmsg IRC command for the reply.
        """
        self.type = 'Privmsg'

    def use_notice(self):
        """
        Use the Notice IRC command for the reply.
        """
        self.type = 'Notice'
