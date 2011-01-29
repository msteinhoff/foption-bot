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

from interaction.irc.module import Module
from interaction.irc.commands.rfc2812 import Privmsg

class Roll(Module):
    '''
    random roll 1-X
    '''
    
    def receive_listener(self):
        return {
            Privmsg: self.privmsg
        }
    
    def privmsg(self, event):
        target, message = event.parameter[0:2]
        
        if not message.startswith('.roll'):
            return
        
        try:
            message = re.findall(r'.roll ([\d]+)(?:-([\d]+))?$', message)[0]
            
            if message[1]:
                min = int(message[0])
                max = int(message[1])
            else:
                min = 1
                max = int(message[0])
        
            if max > 0 and max >= min:
                result = random.randint(min, max)
                
                reply = "{0} has rolled: {1} ({2}-{3})".format(
                    event.source.nickname,
                    result,
                    min,
                    max
                )
        except IndexError, ValueError:
            reply = "usage: .roll zahl[-zahl]"
        
        
        reply = "Rollapparillo: {0}".format(reply)
        
        print reply
            
        self._client.send_command(Privmsg, target, reply)
