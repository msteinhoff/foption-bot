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

__version__ = "$Rev$"

from string import split

from interaction.irc.message.source import Source, ClientSource, ServerSource

class Message(object):
    MAXLENGTH = 510
    
    """
    A IRC message in plaintext.    
    """
    
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
        Parse an incoming IRC message and return a new Event instance.
        
        @param message: The raw message.
        @return An Event instance.
        """
        
        result = self.message
        
        """---------------------------------------------------------------------
        Extract the source if available
        ---------------------------------------------------------------------"""
        if result[0] == ':':
            source, result = split(result[1:], ' ', 1)
            
            """when source contains a ! we assume that source is not a
            # servername because ! are not allowed in ip addresses or
            dns names."""
            
            if '!' in source:
                nick, identhost = split(source, '!')
                ident, host = split(identhost, '@')
                source = ClientSource(nick, ident, host)
            else:
                source = ServerSource(source)
            
        else:
            source = None
    
        """---------------------------------------------------------------------
        Separate command and parameters
        ---------------------------------------------------------------------"""
        try:
            # First case: There is a parameter with spaces after ' :'
            msg_nospace, msg_space = split(result, ' :', 1)
            msg_split = split(msg_nospace, ' ')
            
            command = msg_split[0]
            parameter = msg_split[1:]
            parameter.append(msg_space)
            
        except ValueError:
            try:
                # Second case: There are multiple parameters without space
                msg = split(result, ' ')
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
    
    def __init__(self, source, command, parameter):
        """
        Create a new instance.
        
        @param source: a Source instance or None  
        @param command: the IRC command or reply
        @param parameter: a list with all parameters or None
        """
        
        if source != None and not isinstance(source, Source):
            raise ValueError
        
        self.source = source
        self.command = command
        self.parameter = parameter

    def __str__(self):
        """
        Return the string representation of the event.
        """
        
        return self.compose(self)
    
    def compose(self):
        """
        Compose a valid IRC message from an Event instance.
        
        @param event: The Event instance.
        @return A string with the IRC message.
        @raise ValueError if any of the first n-1 parameters contain spaces.
        """
        
        """---------------------------------------------------------------------
        Handle the source if existent
        ---------------------------------------------------------------------"""
        if self.source == None:
            prefix = ''
            
        else:
            prefix = ':{0} '.format(self.source)
            
        """---------------------------------------------------------------------
        Handle the command
        ---------------------------------------------------------------------"""
        command = self.command
        
        """---------------------------------------------------------------------
        Handle parameters
        ---------------------------------------------------------------------"""
        if self.parameter == None:
            paramlist = ''
        
        else:
            for param in self.parameter[:-1]:
                if ' ' in param:
                    raise ValueError('only the last parameter may contain spaces')
            
            if ' ' in self.parameter[-1:1]:
                paramlist = ' {0} :{1}'.format(' '.join(self.parameter[:-1]), self.parameter[-1:1])
            else:
                paramlist = ' {0}'.format(' '.join(self.parameter))
            
        message = '{0}{1}{2}'.format(prefix, command, paramlist)
        
        if len(message) > Message.MAXLENGTH:
            raise ValueError('message exceeds maximum length')

        return message
    
    def create_message(self):
        """
        Create a new Message instance.
        """
        return Message(self.compose())
