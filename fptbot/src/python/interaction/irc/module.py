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

from interaction.irc.command import PrivmsgCmd, NoticeCmd

MIRC_COLOR = "\x03"

class Module(object):
    """
    Extend the IRC client's functionality.
    
    This module is loaded and instantiated by the client. It provides
    an interface the IRC by registering callback functions on
    any IRC command known by the client.
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

    def get_receive_listeners(self):
        """
        Return a mapping between commands and callback functions.
        
        This will return a dictionary with the mapping.
        - They keys are command classes
        - the values are pointers to methods provided by the class.
        
        @return list with mapping between commands and class methods   
        """
        raise NotImplementedError
    
    def initialize(self):
        pass
    
    def shutdown(self):
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
    
    COMMAND_TRIGGER = '.'
    PATTERN_BASE = r'^\{0}(?P<command>{1})(\s(?P<parameter>.+)$|$)'
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
        
        self.command_map = self.command_mapping()
        
        regex = self.PATTERN_BASE.format(
            self.COMMAND_TRIGGER,
            self.PATTERN_SEPARATOR.join(self.command_map)
        )
        
        self.command_re = re.compile(regex, re.I)
        
        self.parameter_re = []
        for command, parameter_pattern in self.parameter_mapping().items():
            self.parameter_re[command] = re.compile(parameter_pattern, re.I)
    
    def module_identifier(self):
        """
        Return a verbose string that identifies the module.
        
        This prefix is used when sending replies.
        
        @return An identifier, e.g. 'Rollapparillo'
        """
        
        raise NotImplementedError
    
    def command_mapping(self):
        """
        Return a definition of commands/sub-commands and callbacks.
        
        The module will respond on every command defined. The commands
        must be given without the trigger character.
        
        Sub-commands are defined as ordinary commands separated by a
        space (0x20) character.
        
        Examples:
        {'roll': callback}
        {'black': callback, 'white': callback, 'pink': callback}
        {'calendar add': callback, 'calendar delete': callback}
        
        @return A dictionary with the command/sub-command keywords.
        """
        
        raise NotImplementedError
    
    def parameter_mapping(self):
        """
        Return a dictionary that maps parameters to commands or
        sub-commands.
        
        Example:
        {'roll': r'^([\d]+)(?:-([\d]+))$'}
        {'calendar add': r'^([\d]+)(?:-([\d]+))?$'}
        """
        
        raise NotImplementedError
    
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
        
        message = event.parameter[1]
        
        message_match = self.command_re.search(message)
        
        if message_match is None:
            return
        
        command = message_match.group('command')
        parameter = message_match.group('parameter')
        
        try:
            parameter_match = self.parameter_re[command].findall(parameter)
            
            try:
                parameter = parameter_match[0]
            except KeyError:
                self.invalid_parameters(event, command)
                return
        
        except KeyError:
            parameter = None
        
        callback = self.command_map[command]
        
        try:
            callback(event, command, parameter_match)
            
        except Exception as ex:
            """
            Should not happen, but just in case.
            
            TODO: throw stack trace
            """
            
            self.client.logger.error('Unhandled exception {1} thrown in {0}'.format(
                self.__class__.__name__,
                str(ex)
            ))
    
    def invalid_parameters(self, event, command):
        pass
    
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
        
        reply = '{}: {}'.format(self.module_identifier(), reply)
        
        self.client.send_command(command, target, reply)
