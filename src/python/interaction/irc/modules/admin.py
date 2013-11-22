# -*- coding: UTF-8 -*-
"""
$Id: calendar.py 270 2012-02-01 22:59:11Z steinhoff.mario $

$URL: https://fptbot.googlecode.com/svn/trunk/fptbot/src/python/interaction/irc/modules/calendar.py $

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

@since Mar, 03 2012
@author Rack Rackowitsch
@author Mario Steinhoff
"""

from objects.principal import Role
from objects.irc import Location
from interaction.irc.module import InteractiveModule, InteractiveModuleCommand, InteractiveModuleResponse, ModuleError

#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Exceptions
#-------------------------------------------------------------------------------
class AdminError(ModuleError): pass

#-------------------------------------------------------------------------------
# Business Logic
#-------------------------------------------------------------------------------
class Admin(InteractiveModule):
    """
    Control the bots IRC behavior.
    """
    
    #---------------------------------------------------------------------------
    # Module implementation
    #---------------------------------------------------------------------------
    def initialize(self):
        """
        Initialize the module.
        """
        
        self.me = self.client.me
        
    #---------------------------------------------------------------------------
    # InteractiveModule implementation
    #---------------------------------------------------------------------------
    def module_identifier(self):
        return 'IRC-Administration'
    
    def init_commands(self):
        return [
            InteractiveModuleCommand(
                keyword='nick',
                callback=self.change_nickame,
                location=Location.QUERY,
                role=Role.ADMIN,
                pattern=r'^$',
                syntaxhint='???'
            ),
            InteractiveModuleCommand(
                keyword='join',
                callback=self.join_channel,
                location=Location.QUERY,
                role=Role.ADMIN,
                pattern=r'^$',
                syntaxhint='???'
            ),
            InteractiveModuleCommand(
                keyword='part',
                callback=self.part_channel,
                location=Location.QUERY,
                role=Role.ADMIN, 
                pattern=r'^$',
                syntaxhint='???'
            ),
            InteractiveModuleCommand(
                keyword='quit',
                callback=self.quit,
                location=Location.QUERY,
                role=Role.ADMIN,
                pattern=r'^$',
                syntaxhint='???'
            )
        ]
    
    def change_nickname(self, request):
        response = InteractiveModuleResponse('not implemented')
        
        return response
    
    def join_channel(self, request):
        response = InteractiveModuleResponse('not implemented')
        
        return response
    
    def part_channel(self, request):
        response = InteractiveModuleResponse('not implemented')
        
        return response

    def quit(self, request):
        response = InteractiveModuleResponse('not implemented')
        
        return response
