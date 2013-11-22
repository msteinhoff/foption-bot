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

@since Apr, 07 2010
@author Rack Rackowitsch
@author Mario Steinhoff
"""

__version__ = '$Rev$'

import logging
import random

from interaction.irc.module import Module

class Facts(Module):
    """
    This module posts random facts in the channel.
    """
    
    #---------------------------------------------------------------------------
    # Module implementation
    #---------------------------------------------------------------------------
    def initialize(self):
        self.logger = logging.getLogger('interaction.irc.facts')
        self.component = self.client.bot.get_subsystem('facts-component')
        
    def get_receive_listeners(self):
        return {'Privmsg': self.random_post}
    
    #---------------------------------------------------------------------------
    # module commands
    #---------------------------------------------------------------------------
    def random_post(self, event):
        if random.randint(1,88) != 12:
            return
        
        fact = self.component.find_random_fact()
        
        reply = self.client.get_command('Privmsg').get_sender()
        reply.target = event.parameter[0]
        reply.text = 'ACTION ist kluK und weiss: "{0}"'.format(fact.text)
        reply.send()
        
        self.logger.info('posted random fact number %s', fact.id)
