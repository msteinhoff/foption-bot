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

@since Jan 17, 2011
@author Mario Steinhoff
"""

__version__ = '$Rev$'

from interaction.irc.module import Role

class Channellist(object):
    """
    Maintain a list of channels the bot has joined.
     
    The information this module contains include 
    - the channel name
    - the channel topic
    - the channel modes
    - a list of ban bamsks
    - a list of invite masks
    - a list of users currently on each channel
    """
    
    def __init__(self):
        """
        Initialize the channel list.
        """
        
        self.channels = {}
    
    def __str__(self):
        """
        Return a string representation for debugging purposes.
        """
        
        return 'Channellist(Channels={0})'.format('|'.join(self.channels))
    
    def add(self, channel):
        """
        Add a channel object to the channel list.
        
        If the channel object exists, it will be overwritten.
        
        @param channel: A channel object.
        """
        
        self.channels[channel.name] = channel
    
    def get(self, name):
        """
        Return a channel object from the channel list.
        
        @param name: The channel name.
        
        @return A channel object.
        
        @raise KeyError If the channel does not exist.
        """
        
        return self.channels[name]
    
    def request(self, name):
        """
        Request a channel from the channel list by name.
        
        If the channel does not exist, it will be created and returned.
        
        @param name: The channel name.
        
        @return A channel object.
        """
        
        try:
            return self.get(name)
        
        except KeyError:
            channel = Channel(name)
            
            self.add(channel)
            
            return channel
    
    def remove(self, name):
        """
        Remove a channel object from the channel list.
        
        @param name: The channel name.
        
        @raise KeyError If the channel does not exist.
        """
        
        del self.channels[name]
        
class Userlist(object):
    """
    Provide a List with User entities that are known to the bot. Each
    user on a given IRC network only exists once in this list, even if
    the user shares multiple channels with the bot.
    
    Every channel is also maintaining a user list, but only uses
    references to Userlist objects.
    """
    
    def __init__(self):
        """
        Create an empty user list.
        """
        
        self.users = {}
        
    def __str__(self):
        """
        Return a string representation for debugging purposes.
        """

        return 'Userlist(Users={0})'.format('|'.join(self.users))
    
    def add(self, user):
        """
        Add a new User object to the list.
        
        @param user: The user object.
        """
        
        self.users[user.source.nickname] = user
    
    def get(self, source):
        """
        Return a user object by its nickname.
        
        @param source: The source object of the user.
        
        @return The user object, if existent.
        
        @raise KeyError if no such user was found.
        """
        
        return self.users[source.nickname]
    
    def request(self, source, realname=''):
        """
        Request a user from the user list by source.
        
        If the user object does not exist, it will be created and returned.
        
        @param name: The channel name.
        
        @return A channel object.
        """
        
        try:
            return self.get(source)
        
        except KeyError:
            user = User(source, realname)
            
            self.add(user)
            
            return user

    def rename(self, current_nickname, new_nickname):
        """
        Changes the nickname of a user.
        
        @param current_nickname: The current nickname of the user
        @param new_nickname: The new nickname of the user
        """
        
        user = self.users[current_nickname]
        
        user.rename(new_nickname)
        
        self.users[new_nickname] = user
        
        del self.users[current_nickname]
    
    def remove(self, source):
        """
        Remove a user object by its nickname from the user list.
        
        Any references to channels the user had joined are also
        removed.
        
        @param source: The source object of the user.
        
        @raise KeyError if no such user was found.
        """
        
        for channel in self.users[source.nickname].getChannels():
            channel.removeUser(source.nickname)
            
        del self.users[source.nickname]
        
class Channel(object):
    """
    A channel entity.
    """
    
    MODE_OP    = 1
    MODE_VOICE = 2
    
    def __init__(self, name):
        """
        Initialize a channel.
        """
        
        self.name = name
        self.topic = ''
        self.modes = []
        self.banlist = []
        self.invitelist = []
        self.users = {}
        
    def __str__(self):
        """
        Return a string representation for debugging purposes.
        """
        
        return 'Channel(Name={0},Users={1})'.format(self.name, '|'.join(self.users))
        
    def getModes(self):
        """
        Yeah, what to do here? do we need this actually?
        """
        
        pass
    
    def addUser(self, user, mode=None):
        """
        Add a user object to the channel.
        The user object is notified about being added to the channel. 
        
        @param user: The user object.
        @param mode: The user mode in the channel.
        """
        
        self.users[user.source.nickname] = (user, mode)
        user.addChannel(self)
        
    def updateUserMode(self, nickname, mode):
        """
        Updates the user mode.
        
        @param nickname: The nickname of the user.
        @param mode: The new user mode.
        """
        
        self.users[nickname] = (self.getUser(nickname), mode)
        
    def getUser(self, nickname):
        """
        Return a user object by its nickname.
        
        @param nickname: The nickname of the user object.
        """
        
        return self.users[nickname][0]
    
    def getUserList(self):
        """
        Return the current user list of the channel.
        
        @return The user list.
        """
        
        return self.users
    
    def renameUser(self, current_nickname, new_nickname):
        """
        Rename a user object.
        
        This will only modify the internal user key but will not touch
        the user object directly.
        
        @param current_nickname: The current nickname of the user object.
        @param new_nickname: The new nickname of the user object.
        """
        
        user = self.users[current_nickname]
        
        self.users[new_nickname] = user
        
        del self.users[current_nickname]

    def removeUser(self, nickname):
        """
        Remove a user object from the channel.
        
        @param nickname: The nickname of the user.
        """
        
        self.users[nickname].removeChannel(self)
        del self.users[nickname]

class User(object):
    AWAY         = 'a'
    INVISIBLE    = 'i'
    WALLOPS      = 'w'
    RESTRICTED   = 'r'
    OPER         = 'o'
    LOCALOPER    = 'O'
    SERVERNOTICE = 's'
    
    def __init__(self, source, realname):
        """
        Initialize the user.
        
        @param source: The Source object.
        @param realname: The realname of the user.
        """
        
        self.source   = source
        self.realname = realname
        self.channels = []
        self.information = {}
        
    def __str__(self):
        """
        Return a string representation for debugging purposes.
        """

        return 'User(Nickname={0},Ident={1},Host={2},Realname={3},Channels={4})'.format(
            self.source.nickname,
            self.source.ident,
            self.source.host,
            self.realname,
            '|'.join(self.channels)
        )
        
    def rename(self, new_nickname):
        """
        Rename the user.
        
        Notify all channels the user and bot have in common.
        
        @param new_nickname: The user's new nickname.
        """
        
        for channel in self.channels:
            channel.renameUser(self.source.nickname, new_nickname)
        
        self.source.nickname = new_nickname

    def addChannel(self, channel):
        """
        Adds a channel to the user.

        This should never be called directly but only by the
        Channellist module.
        
        @param channel: The channel object to add.
        """
        
        if channel in self.channels:
            return
        
        self.channels.append(channel)
        
    def getChannels(self):
        """
        Return a list of all channels that user and bot have in common.
        """
        
        return self.channels
    
    def removeChannel(self, channel):
        """
        Removes a channel from the user.
        
        This should never be called directly but only by the
        Channellist module.
        
        @param channel: The channel object to remove.
        """
        
        if channel not in self.channels:
            return
        
        self.channels.remove(channel)

    def isOn(self, channel):
        """
        Determines whether the user is on the given channel.
        
        @param channel: The channel object to check against.
        """
        
        return channel in self.channels

    def setInfo(self, module, information):
        """
        Set module-specific information, e.g. a dictionary or a data
        object.
        
        Each module can have independent information on a per-user
        basis.
        
        @param module: The module name.
        @param information: Any python object.
        """
        
        self.information[module] = information
    
    def getInfo(self, module):
        """
        Retrieve module-specific information.
        
        @param module: The module name.
        """
        
        return self.information[module]
