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

__version__ = '$Rev$'

import random
import re

from objects.irc import Location
from interaction.irc.module import InteractiveModule, InteractiveModuleCommand, InteractiveModuleResponse

#-------------------------------------------------------------------------------
# Business Logic
#-------------------------------------------------------------------------------
class Orakel(InteractiveModule):
    """
    This module aids the user to make a decision.
    """

    #---------------------------------------------------------------------------
    # InteractiveModule implementation
    #---------------------------------------------------------------------------
    def module_identifier(self):
        return 'Orakel'
    
    def init_commands(self):
        return [
            InteractiveModuleCommand(
                keyword='wer', 
                callback=self.who,
                location=Location.CHANNEL
            ),
            InteractiveModuleCommand(
                keyword='decide',
                callback=self.decide,
                pattern=r'^((.+)$|$)',
                syntaxhint='[Auswahl1[, [Auswahl2[, ...]]]]'
            ),
            InteractiveModuleCommand(
                keyword='makemyday',
                callback=self.sort,
                pattern=r'^(.+)$',
                syntaxhint='[Item1[, Item2[, ...]]]'
            )
        ]
    
    #---------------------------------------------------------------------------
    # module commands
    #---------------------------------------------------------------------------
    def who(self, request):
        response = InteractiveModuleResponse()
        
        channel_name = request.target
        
        channel = self.usermgmt.chanlist.get(channel_name)
        
        user = random.choice(channel.get_users().keys())
        
        response.add_line('Meine Wahl fällt auf {0}!'.format(user))
        
        return response
    
    def decide(self, request):
        response = InteractiveModuleResponse()
        
        issue = request.parameter[0]
        
        if len(issue) == 0:
            if random.randint(1,1000) % 2 == 0:
                response.add_line('Du solltst dich dafür entscheiden!')
            else:
                response.add_line('Du solltst dich dagegen entscheiden!')
        
        else:
            choices = re.sub('( oder | or )', ',', issue).split(',')
            
            if len(choices) == 1:
                pick = choices[0]
                
                if random.randint(1,1000) % 2 == 0:
                    response.add_line('Du solltst dich für \'{0}\' entscheiden!'.format(pick.strip()))
                else:
                    response.add_line('Du solltst dich gegen \'{0}\' entscheiden'.format(pick.strip()))
            
            else:
                pick = random.choice(choices)
                
                response.add_line('Du solltst dich für \'{0}\' entscheiden'.format(pick.strip()))
        
        return response
    

    def sort(self,request):
        """
        Reorder the given items.
        
        @return: InteractiveModuleResponse()
        """
        response = InteractiveModuleResponse()
        
        items_unsorted = request.parameter[0].split(',')
        items_sorted = []
        
        while len(items_unsorted) > 0:
            num = random.randint(0,len(items_unsorted)-1)
            items_sorted.append(items_unsorted[num].strip())
            del items_unsorted[num]
        
        response.add_line(", ".join(items_sorted))
        
        return response