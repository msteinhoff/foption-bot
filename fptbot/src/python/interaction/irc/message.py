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

@since Jan 12, 2011
@author Mario Steinhoff
"""

__version__ = '$Rev$'

import string

from interaction.irc.source import ServerSource, ClientSource

SPACE      = '\x20'
COLON      = '\x3A'
SPACECOLON = '\x20\x3A'
EXMARK     = '\x21'
AT         = '\x40'

CHANNEL_TOKEN = '\x23'

class Message(object):
    """
    A IRC message in plaintext.
    """
    
    MAXLENGTH = 510
    
    def __init__(self, message):
        """
        Create a new instance.
        
        @param message: The raw IRC message.
        """
        
        if len(message) == 0:
            raise ValueError('empty message')
        
        if len(message) > self.MAXLENGTH:
            raise ValueError('message exceeds maximum length')
        
        self.message = message
    
    def __str__(self):
        """
        Return The string representation of the message.
        """
        
        return self.message
    
    def create_event(self):
        """
        Parse the class' message attribute and return a new Event instance.
        
        TODO: cleaner implementation using regex
        
        @return An Event instance.
        """
        
        result = self.message
        
        #-----------------------------------------------------------------------
        # Extract the source if available
        # ----------------------------------------------------------------------
        if result.startswith(COLON):
            source, result = string.split(result[1:], SPACE, 1)
            
            # when source contains a EXMARK we assume that source is not a
            # servername, because EXMARK are not allowed in ip addresses or
            # dns names.
            
            if EXMARK in source:
                nick, ident_host = string.split(source, EXMARK)
                ident, host = string.split(ident_host, AT)
                
                source = ClientSource(nickname=nick, ident=ident, host=host)
            else:
                source = ServerSource(servername=source)
            
        else:
            source = None
    
        #-----------------------------------------------------------------------
        # Separate command and parameters
        #-----------------------------------------------------------------------
        try:
            # First case: There is a parameter with spaces after SPACECOLON
            msg_without_space, msg_with_space = string.split(result, SPACECOLON, 1)
            msg_parts = string.split(msg_without_space, SPACE)
            
            command = msg_parts[0]
            parameter = msg_parts[1:]
            parameter.append(msg_with_space)
            
        except ValueError:
            try:
                # Second case: There are multiple parameters without space
                msg = string.split(result, SPACE)
                command = msg[0]
                parameter = msg[1:]
                
            except ValueError:
                # Third case: There is only one command
                command = msg
                parameter = None
        
        return Event(source, command, parameter)


class Event(object):
    """
    An IRC message event.
    """
    
    def __init__(self, source=None, command=None, parameter=None):
        """
        Create a new instance.
        
        @param source: a Source instance or None
        @param command: the IRC command/reply
        @param parameter: a list with all parameters or None
        """
        
        self.source = source or ''
        self.command = command or ''
        self.parameter = parameter or []

    def __str__(self):
        """
        Return the string representation of the event.
        """
        
        return self.compose(self)
    
    def compose(self):
        """
        Compose a IRC message from this Event.
        
        @return A string with the IRC message.
        
        @raise ValueError if any of the first n-1 parameters contain spaces.
        """
        
        #-----------------------------------------------------------------------
        # Handle the source if existent
        #-----------------------------------------------------------------------
        if self.source == None:
            prefix = ''
            
        else:
            prefix = '{0}{1}{2}'.format(COLON, self.source, SPACE)
            
        #-----------------------------------------------------------------------
        # Handle the command
        #-----------------------------------------------------------------------
        command = self.command
        
        #-----------------------------------------------------------------------
        # Handle parameters
        #-----------------------------------------------------------------------
        if self.parameter == None:
            paramlist = ''
            
        elif len(self.parameter) == 0:
            paramlist = ''
        
        elif len(self.parameter) == 1:
                paramlist = '{0}{1}'.format(SPACECOLON, self.parameter[0])
            
        else:
            rest = self.parameter[:-1]
            last = self.parameter[-1:][0]
            
            for param in rest:
                if SPACE in param:
                    raise ValueError('only the last parameter may contain spaces')
            
            if SPACE in last:
                paramlist = '{0}{1}{2}{3}'.format(SPACE, SPACE.join(rest), SPACECOLON, last)
            else:
                paramlist = '{0}{1}'.format(SPACE, SPACE.join(self.parameter))
            
        message = '{0}{1}{2}'.format(prefix, command, paramlist)

        return message
    
    def create_message(self):
        """
        Create a new Message instance.
        """
        return Message(self.compose())
