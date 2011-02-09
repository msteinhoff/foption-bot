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

@since Mar, 03 2010
@author Rack Rackowitsch
@author Mario Steinhoff
"""

__version__ = '$$'

import random
import re

from interaction.irc.module import InteractiveModule, Location, Role
from interaction.irc.command import PrivmsgCmd

class Orakel(InteractiveModule):
    """
    This module aids the user to make a decision.
    """

    def module_identifier(self):
        return 'Orakel'
    
    def init_commands(self):
        self.add_command('wer',    None,         Location.CHANNEL, PrivmsgCmd, Role.USER, self.who)
        self.add_command('decide', '^((.+)$|$)', Location.CHANNEL, PrivmsgCmd, Role.USER, self.decide)
    
    def who(self, event, location, command, parameter):
        channel_name = event.parameter[0]
        
        channel = self.usermgmt.chanlist.get(channel_name)
        
        user = random.choice(channel.getUserList().keys())
        
        reply = 'Meine Wahl fällt auf {0}!'.format(user)
        
        return reply
    
    def decide(self, event, location, command, parameter):
        issue = parameter[0]
        
        if len(issue) == 0:
            if (random.randint(1,1000) % 2 == 0):
                reply = 'Du solltst dich dafür entscheiden!'
            else:
                reply = 'Du solltst dich dagegen entscheiden!'
        
        else:
            choices = re.sub('( oder | or )', ',', issue).split(',')
            
            if len(choices) == 1:
                pick = choices[0]
                
                if random.randint(1,1000) % 2 == 0:
                    reply = 'Du solltst dich für \'{0}\' entscheiden!'.format(pick.strip())
                else:
                    reply = 'Du solltst dich gegen \'{0}\' entscheiden'.format(pick.strip())
            else:
                pick = random.choice(choices)
                
                reply = 'Du solltst dich für \'{0}\' entscheiden'.format(pick.strip())
        
        return reply
    
    def invalid_parameters(self, event, location, command, parameter):
        if command == 'wer':
            reply = 'usage: .wer'
            
        elif command == 'decide':
            reply = 'usage: .decide [Auswahl1[, [Auswahl2[, ...]]]]'
            
        return reply
