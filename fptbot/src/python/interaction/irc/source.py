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

@since Jan 14, 2011
@author Mario Steinhoff
"""

__version__ = '$Rev$'

class ServerSource(object):
    """
    A IRC server source entity.
    """
    
    def __init__(self, servername=None):
        """
        Create a new instance.
        
        @param servername: The servername of the entity
        """
        
        self.servername = servername or ''
        
    def __str__(self):
        """
        Return the string representation in the format 'servername'.
        """
         
        return '{0}'.format(self.servername)


class ClientSource(object):
    """
    A IRC client source entity.
    """
    
    def __init__(self, nickname=None, ident=None, host=None):
        """
        Create a new instance.
        
        @param nickname: The nickname of the entity
        @param ident: The ident of the entity
        @param host: The hostname of the entity
        """
        
        self.nickname = nickname or ''
        self.ident = ident or ''
        self.host = host or ''
        
    def __str__(self):
        """
        Return the string representation in the format 'nickname!ident@host'.
        """
         
        return '{0}!{1}@{2}'.format(self.nickname, self.ident, self.host)
