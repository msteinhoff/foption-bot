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

@since 06.01.2010
@author Mario Steinhoff
"""

__version__ = '$Rev$'

from interaction.irc.commands import Command

list = [
    'WhoisAuthReply'
]

class Auth(Command):
    """
    Command: AUTH
    Parameters: <username> <password>
    
    AUTH command is used to authenticate user with Quakenet Q9 service.
    """
    
    token = 'AUTH'
    
    class Sender(Command.Sender):
        def _send(self):
            """
            Authenticate with Quakenet Q9 service.
            """
            
            self.check_attr('username')
            self.check_attr('password')
            
            return self.create_event(Auth, [self.username, self.password])

class WhoisAuthReply(Command):
    token = '330'
