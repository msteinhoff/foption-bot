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

import random

from interaction.irc.module import InteractiveModule, Location, Role
from interaction.irc.command import PrivmsgCmd

class Roll(InteractiveModule):
    '''
    random roll 1-X
    '''
    
    def module_identifier(self):
        return 'Rollapparillo'
    
    def init_commands(self):
        self.add_command('roll',     r'^([\d]+)(?:-([\d]+))?$', Location.CHANNEL, Role.USER,  self.roll)
        self.add_command('rollqry',  None,                      Location.QUERY,   Role.USER,  self.rollquery)
        self.add_command('rollboth', None,                      Location.BOTH,    Role.USER,  self.rollboth)
        self.add_command('rolladm',  None,                      Location.QUERY,   Role.ADMIN, self.rolladmin)
    
    def roll(self, event, location, command, parameter):
        target = self.get_target(location, event)
        
        if parameter[1]:
            min = int(parameter[0])
            max = int(parameter[1])
        else:
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
        
        self.send_reply(PrivmsgCmd, target, reply)
        
    def rollquery(self, event, location, command, parameter):
        target = self.get_target(location, event)
        
        self.send_reply(PrivmsgCmd, target, 'Mich gibts nur als user im query')

    def rollboth(self, event, location, command, parameter):
        target = self.get_target(location, event)
        
        self.send_reply(PrivmsgCmd, target, 'Mich gibts nur als user im chan und query')

    def rolladmin(self, event, location, command, parameter):
        target = self.get_target(location, event)
        
        self.send_reply(PrivmsgCmd, target, 'Mich gibts nur als admin im query')

    def invalid_parameters(self, event, location, command, parameter):
        target = event.parameter[0]
        
        reply = "usage: .roll zahl[-zahl]"
        
        self.send_reply(PrivmsgCmd, target, reply)
