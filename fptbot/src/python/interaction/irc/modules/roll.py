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

__version__ = "$$"

import re
import random

from interaction.irc.module import InteractiveModule
from interaction.irc.command import Privmsg

class Roll(InteractiveModule):
    '''
    random roll 1-X
    '''
    
    def receive_listener(self):
        return {
            Privmsg: self.parse
        }
    
    def command_mapping(self):
        return {'roll': self.roll}
    
    def parameter_mapping(self):
        return {'roll': r'^([\d]+)(?:-([\d]+))?$'}
    
    def roll(self, event, command, parameter):
        target = event.parameter[0]
        
        try:
            min = int(parameter[0])
            max = int(parameter[1])
        except KeyError:
            min = 1
            max = int(parameter[0])
    
        if max > 0 and max >= min:
            result = random.randint(min, max)
            
            reply = "{0} has rolled: {1} ({2}-{3})".format(
                event.source.nickname,
                result,
                min,
                max
            )
    
        reply = "Rollapparillo: {0}".format(reply)
        
        self._client.send_command(Privmsg, target, reply)

    def invalid_parameters(self, event, command):
        target = event.parameter[0]
        reply = "usage: .roll zahl[-zahl]"
        
        self._client.send_command(Privmsg, target, reply)
