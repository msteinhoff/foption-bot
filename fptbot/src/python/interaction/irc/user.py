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

@since Jan 11, 2011
@author Mario Steinhoff
"""

class Privilege(object):
    USER = 1
    ADMIN = 2

class Userlist(object):
    def __init__(self):
        self._userlist = {}
    
    def getList(self):
        return self._userlist
    
    def addUser(self, userObject):
        self._userlist[userObject.nickname] = userObject
    
    def changeNickname(self, old, new):
        self._userlist[new] = self._userlist[old]
        
        self._userlist[new].nickname = new
        
        self.deleteUser(old)
    
    def deleteUser(self, nickname):
        del self._userlist[nickname]

    def findUserByAuth(self, auth):
        for userObject in self._userlist.values():
            if userObject.auth == auth:
                return userObject

        return None

class User(object):
    AWAY         = "a"
    INVISIBLE    = "i"
    WALLOPS      = "w"
    RESTRICTED   = "r"
    OPER         = "o"
    LOCALOPER    = "O"
    SERVERNOTICE = "s"
    
    def __init__(self, nickname, hostmask, auth="", channels=[]):
        self.nickname = nickname
        self.hostmask = hostmask
        self.auth     = auth
        self.channels = channels
        
    
