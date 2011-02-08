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

__version__ = "$Rev$"

import re

from interaction.irc.message import CHANNEL_TOKEN
from interaction.irc.command import PrivmsgCmd, NoticeCmd

MIRC_COLOR = "\x03"

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

    """-------------------------------------------------------------------------
    IRC interface 
    -------------------------------------------------------------------------"""
    def get_receive_listeners(self):
        """
        Return a mapping between commands and callback functions.
        
        This will return a dictionary with the mapping.
        - They keys are command classes
        - the values are pointers to methods provided by the class.
        
        @return list with mapping between commands and class methods   
        """
        raise NotImplementedError
    
    """-------------------------------------------------------------------------
    State handling
    -------------------------------------------------------------------------"""
    def initialize(self):
        """
        Initialization hook.
        
        This will execute additional initialization code in the module
        without overriding the constructor.
        """
        pass
    
    def shutdown(self):
        """
        Cleanup hook.
        
        This will execute additional cleanup code in the module without
        overriding the destructor.
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
        
        # cache reference to userlist
        self.userlist = self.client.get_module('usermgmt').userlist
        
        self.identifier = self.module_identifier()
        self.command_dict = {}

        self.init_commands()
        
        pattern = self.PATTERN_BASE.format(
            self.PATTERN_SEPARATOR.join(self.command_dict)
        )
        
        self.module_re = re.compile(pattern, re.I)
    
    """-------------------------------------------------------------------------
    Overridden methods
    -------------------------------------------------------------------------"""
    def get_receive_listeners(self):
        """
        Setup default receive listeners needed for Privmsg handling.
        """
        
        return {PrivmsgCmd: self.parse}

    """-------------------------------------------------------------------------
    Identification and behavior
    -------------------------------------------------------------------------"""
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
        self.addCommand('roll', r'^([\d]+)(?:-([\d]+))$', Role.USER, self.roll)
        
        self.add_command('black', None, Role.USER, self.choose)
        self.add_command('white', None, Role.USER, self.choose)
        self.add_command('pink',  None, Role.USER, self.choose)
        
        self.add_command('calendar add',    '???', Role.USER, self.add)
        self.add_command('calendar delete', '???', Role.USER, self.delete)
        
        @return none
        """
        
        raise NotImplementedError
    
    """-------------------------------------------------------------------------
    Module command handling
    -------------------------------------------------------------------------"""
    def add_command(self, keyword, pattern, location, role, callback):
        """
        Add a command to the internal command dictionary.
        
        @param keyword: The keyword that triggers the command.
        @param pattern: A regex pattern that defines the arguments.
        @param location: The location where the command can be executed.
        @param role: The role the calling user needs to have.
        @param callback: The callback function.
        """
        self.command_dict[keyword] = ModuleCommand(self, keyword, pattern, location, role, callback)
    
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
        
        @param event: The Privmsg or Notice event.
        """
        
        if event.command not in (PrivmsgCmd.token(), NoticeCmd.token()):
            return
        
        """---------------------------------------------------------------------
        Handle command
        ---------------------------------------------------------------------"""

        target, message = event.parameter[0:2]
        
        message_match = self.module_re.search(message)
        
        if message_match is None:
            return
        
        command = message_match.group('command')
        
        command_object = self.command_dict[command]
        
        # check location and access
        # TODO: print error message on insufficient privileges?
        if not command_object.valid_location(target) or \
           not command_object.check_access(event.source):
            return
        
        """---------------------------------------------------------------------
        Handle parameter
        ---------------------------------------------------------------------"""
        parameter = message_match.group('parameter')

        try:
            callback = command_object.callback
            parameter = command_object.match_arguments(parameter)
        except ValueError:
            callback = self.invalid_parameters
            parameter = None
        
        """---------------------------------------------------------------------
        Dispatch
        ---------------------------------------------------------------------"""

        location = Location.get(target)

        try:
            callback(event, location, command, parameter)
            
        except Exception as ex:
            """
            Should not happen, but just in case.
            
            TODO: throw stack trace
            """
            
            self.client.logger.error('Unhandled exception "{1}" thrown in {0}'.format(
                self.__class__.__name__,
                str(ex)
            ))
    
    def invalid_parameters(self, event, command, parameter):
        """
        Handle invalid argument errors.
        
        @param command: The command keyword.
        @param parameter: The raw parameter data.
        """
        
        pass
    
    def get_target(self, location_from, event):
        """
        Based on the location, extract the target for the reply.
        
        TODO: handle reply in parse, make reply the return string or None for no reply
        
        @param location_from: The location value (CHANNEL or QUERY)
        @param event: The event to analyze.
        
        @return The target from the event.
        
        @raise ValueError: If the location is invalid.
        """
        if location_from == Location.CHANNEL:
            target = event.parameter[0]
            
        elif location_from == Location.QUERY:
            target = event.source.nickname
            
        else:
            raise ValueError("location_from may only be channel or query")
        
        return target
    
    def send_reply(self, command, target, reply):
        """
        Send a pretty reply with module identifier and color
        formatting.
        
        Only Privmsg and Notice are allowed here. The target may be
        either a nickname or a channel.
        
        TODO: add mirc color codes
        TODO: fallback to privmsg instead of raising exception?
        
        @param command: The reply type.
        @param target: The target to send the reply to.
        @param reply: The reply string to send.
        """
        
        if command.token() not in (PrivmsgCmd.token(), NoticeCmd.token()):
            raise ValueError('only Privmsg or Notice are valid commands')
        
        reply = '{0}: {1}'.format(self.identifier, reply)
        
        self.client.send_command(command, target, reply)

class ModuleCommand(object):
    """
    Represent a module command that can be triggered by IRC users.
    """
    
    def __init__(self, module, keyword, pattern, location, role, callback):
        """
        Initialize the command.
        
        @param module: The module instance the command belongs to.
        @param keyword: The keyword that triggers the command.
        @param pattern: A regex pattern that defines the arguments.
        @param role: The role the calling user needs to have.
        @param callback: The callback function.
        """
        
        self.module = module
        self.keyword = keyword
        
        if pattern:
            self.pattern = re.compile(pattern, re.I)
        else:
            self.pattern = None
        
        self.location = location
        self.role = role
        self.callback = callback
        
    def valid_location(self, target):
        """
        Determine whether the command can be executed in the location.
        
        @param target: The location to check against.
        """
        
        return Location.valid(self.location, Location.get(target))
    
    def check_access(self, source):
        """
        Check if the given source has sufficient access privileges.
        """
        
        user = self.module.userlist.get(source)
        role = user.getInfo('Privileges')
        
        return Role.valid(self.role, role)
        
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
        
        # TypeError when data can not be matched
        # KeyError when no match was found
        except TypeError, KeyError:
            raise ValueError
        
        except IndexError:
            raise ValueError

        return arguments
    
class Role(object):
    """
    Represent a role neccessary to execute a ModuleCommand.
    
    TODO: need real object here or maybe move to own python module?
    """
    
    USER  = 1 # Right.USER
    ADMIN = 3 # Right.USER | Right.ADMIN
    
    def __init__(self):
        raise NotImplementedError
    
    @staticmethod
    def valid(required, role):
        return (required & role == required) 

class Location(object):
    """
    Represent a location determining where a ModuleCommand can be executed.
    TODO: need real object here or maybe move to own python module?
    """
    
    CHANNEL = 1
    QUERY   = 2
    BOTH    = CHANNEL | QUERY

    def __init__(self):
        raise NotImplementedError

    @staticmethod
    def get(target):
        if target.startswith(CHANNEL_TOKEN):
            location = Location.CHANNEL
        else:
            location = Location.QUERY
        
        return location


    @staticmethod
    def valid(required, location):
        return (required | location == required)
