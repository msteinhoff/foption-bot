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

COMMAND_TOKEN = '.'
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

    def get_receive_listeners(self):
        """
        Return a mapping between commands and callback functions.
        
        This will return a dictionary with the mapping.
        - They keys are command classes
        - the values are pointers to methods provided by the class.
        
        @return list with mapping between commands and class methods   
        """
        raise NotImplementedError

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
    
    class Matcher(object):
        def __init__(self, command, parameter):
            pattern = r'\{}{} {}'.format(COMMAND_TOKEN, command, parameter)
            
            self.regex = re.compile(pattern, re.I)
            
        def match(self, data):
            return self.regex.findall(data)[0]
    
    def __init__(self, client):
        Module.__init__(self, client)
        
        """
        TODO pre-compile optimized regular expressions for every
        command/parameter pair.
        """
        
        """
        for prefix, regex in self.valid_commands().items():
            token = '{0}{1}'.format(COMMAND_TOKEN, prefix)
            pattern = r'\{0}{1} {2}'.format(COMMAND_TOKEN, prefix, regex)
            
            self.tokens[token] = re.compile(pattern, re.I)
        """
        
        self.keywords = {}
        
        parameter_map = self.parameter_mapping()
        
        for key_name, key_map in self.command_keywords().items():
            matcher = self.Matcher(key_name, parameter_map[key_name])
            self.keywords[key_name] = (matcher, key_map[0]) 
        
            if len(key_map) > 1:
                for subkey_name, callback in key_map[1].items():
                
                    matcher = self.Matcher(subkey_name, parameter_map[subkey_name])
                
                    self.keywords[subkey_name] = (matcher, callback) 
    
    def module_identifier(self):
        """
        Return a verbose string that identifies the module.
        
        This prefix is used when sending replies.
        
        @return An identifier, e.g. 'Rollapparillo'
        """
        
        raise NotImplementedError
    
    def command_keywords(self):
        """
        Return a dictionary with a command/sub-command keywords.
        
        The module will respond on every keyword defined. The keywords
        must be given without the control character.
        
        Examples:
        {'roll': (callback)}
        {'black': (callback), 'white': (callback), 'pink': (callback)}
        {'calendar': (callback, {'add': callback, 'delete': callback})}
        
        @return A dictionary with the command/sub-command keywords.
        """
        
        raise NotImplementedError
    
    def parameter_mapping(self):
        """
        Return a dictionary that maps parameters to commands or
        sub-commands.
        
        Example:
        {('roll'): r'([\d]+)(?:-([\d]+))?$'}
        {('calendar', 'add'): r'([\d]+)(?:-([\d]+))?$'}
        """
        
        raise NotImplementedError
    
    def parse(self, event):
        """
        Parse the event and dispatch it to the actual module logic.
        
        This will do basic preparation work that is needed in every
        module, e.g. removing the module prefix, extracting parameters,
        etc.
        
        This module will only accept Privmsg or Notice events.
        
        @param event: The Privmsg or Notice event.
        """
        
        if event.command not in (PrivmsgCmd.token(), NoticeCmd.token()):
            return
        
        for token, params in self.keywords:
            
        
        target, message = event.parameter[0:2]
        
        """
        for command, pattern_object in self.prefixes:
            if message.startswith(token):
                found_command = token
                found_parameter = pattern_object.findall(message)
                break
    
        """
        
        try:
            self.handle_valid(event, target, message[0])
            
        except Exception as ex:
            self.handle_invalid(event, target, ex)
            
        except:
            """
            Should not happen, but just in case.
            
            TODO: throw stack trace
            """
            self.client.logger.error('Unhandled exception thrown in {0}'.format(self.__class__.__name__))

    def handle_valid(self, event, target, parameters):
        """
        Process input when the parameters are valid.
        
        This implements the actual module logic.
        
        @param event: A Privmsg or Notice event.
        @param target: The target entity (nickname or channel).
        @param parameters: The parsed command parameters.
        """
        
        raise NotImplementedError
    
    def handle_invalid(self, event, target, ex):
        """
        Process input when the parameters are invalid.
        
        This implements error conditions.
        
        @param event: A Privmsg or Notice event.
        @param target: The target entity (nickname or channel).
        @param ex: The exception instance.
        """
        
        raise NotImplementedError
    
    def send_reply(self, command, target, reply):
        """
        Send a pretty reply with module identifier and color
        formatting.
        
        Only Privmsg and Notice are allowed here. The target may be
        either a nickname or a channel.
        
        TODO: add mirc color codes
        
        @param command: The command type.
        @param target: The target to send the reply to.
        @param reply: The reply string to send.
        """
        
        if command.token() not in (PrivmsgCmd.token(), NoticeCmd.token()):
            raise ValueError('only Privmsg or Notice are valid commands')
        
        reply = '{0}: {1}'.format(self.module_identifier(), reply)
        
        self.client.send_command(command, target, reply)
