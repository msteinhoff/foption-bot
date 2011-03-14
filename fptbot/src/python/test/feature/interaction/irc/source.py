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

@since Mar 10, 2011
@author msteinhoff
"""
__version__ = '$Rev$'

import unittest

from interaction.irc.source import ServerSource, ClientSource

class TestServerSource(unittest.TestCase):
    def test_00_instantiation(self):
        servername = 'irc.example.org'
        
        self.source = ServerSource(servername)
        
        self.assertTrue(isinstance(self.source, ServerSource))
        self.assertEquals(self.source.servername, servername)
        
class TestClientSource(unittest.TestCase):
    def test_00_instantiation(self):
        nickname = 'Testnick'
        ident = 'testident'
        host = 'test.example.org'
        
        self.source = ClientSource(nickname, ident, host)
        
        self.assertTrue(isinstance(self.source, ClientSource))
        self.assertEquals(self.source.nickname, nickname)
        self.assertEquals(self.source.ident, ident)
        self.assertEquals(self.source.host, host)
