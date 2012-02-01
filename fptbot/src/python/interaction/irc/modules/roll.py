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

from interaction.irc.module import InteractiveModule, InteractiveModuleCommand, InteractiveModuleResponse 

#-------------------------------------------------------------------------------
# Business Logic
#-------------------------------------------------------------------------------
class Roll(InteractiveModule):
    """
    This module provides a virtual dice.
    """
    
    #---------------------------------------------------------------------------
    # InteractiveModule implementation
    #---------------------------------------------------------------------------
    def module_identifier(self):
        return 'Rollapparillo'
    
    def init_commands(self):
        return [
            InteractiveModuleCommand(
                keyword='roll',
                callback=self.roll,
                pattern=r'^([\d]+)(?:-([\d]+))?$',
                syntaxhint='zahl[-zahl]'
            )
        ]
    
    #---------------------------------------------------------------------------
    # module commands
    #---------------------------------------------------------------------------
    def roll(self, request):
        response = InteractiveModuleResponse()
        
        if request.parameter[1]:
            min_value = int(request.parameter[0])
            max_value = int(request.parameter[1])
        else:
            min_value = 1
            max_value = int(request.parameter[0])
    
        if max_value <= 0:
            response.add_line('Zahl muss groesser als 0 sein')
            return response
            
        if max_value <= 1:
            response.add_line('Zahl muss groesser als 1 sein')
            return response
        
        if max_value == min_value:
            response.add_line('Erste Zahl ({0}) == zweite Zahl ({0}), wie soll das denn gehen du Trottel?'.format(min_value, min_value))
            return response
        
        if max_value < min_value:
            max_value, min_value = min_value, max_value
            
        result = random.randint(min_value, max_value)
        
        response.add_line('{0} has rolled: {1} ({2}-{3})'.format(
            request.source.nickname,
            result,
            min_value,
            min_value
        ))
        
        return response
