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
@author Mario Steinhoff
"""

__version__ = '$Rev$'

import unittest

from interaction.irc.source import ClientSource
from interaction.irc.channel import ChannelList, Channel, UserList, User

class TestModule(unittest.TestCase):
    def setUp(self):
        self.source = ClientSource(nickname='Testnick', ident='testident', host='testhost.example.org')
        
        self.user = User(source=self.source, realname='Testname')
        self.channel = Channel(name='#channel')
        
        self.chanlist = ChannelList(client=None)
        self.userlist = UserList(client=None)
        
class TestChannel(TestModule):
    def test_00_instantiation(self):
        self.assertEquals(self.channel.name, '#channel')
        self.assertEquals(self.channel.users, {})
        
    def test_01_adduser(self):
        lenbefore = len(self.channel.get_users())
        self.channel.add_user(self.user)
        lenafter = len(self.channel.get_users())
        
        self.assertTrue(lenafter-lenbefore == 1)
        self.assertTrue(self.channel.get_user('Testnick') == self.user)
        
    def test_02_getusers(self):
        self.channel.add_user(self.user, None)

        self.assertTrue('Testnick' in self.channel.get_users())
        
    def test_03_renameuser(self):
        self.channel.add_user(self.user, None)

        self.channel.rename_user('Testnick', 'NewTestNick')
        
        self.assertRaises(KeyError, self.channel.get_user, 'Testnick')
        self.assertRaises(KeyError, self.channel.get_user, 'newtestnick')
        self.assertEquals(self.channel.get_user('NewTestNick'), self.user)
        self.assertEquals(self.user.source.nickname, 'Testnick')

class TestChannellist(TestModule):
    def test_00_instantiation(self):
        self.assertEquals(self.chanlist.channels, {})
        
    def test_01_addchannel(self):
        self.chanlist.add(self.channel)
        
        self.assertNotEquals(self.chanlist.channels, {})
        self.assertEquals(self.chanlist.get('#channel'), self.channel)

class TestUser(TestModule):
    pass

class TestUserlist(TestModule):
    pass
