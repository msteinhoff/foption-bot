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

class Channel(object):
    """
    A channel entity.
    """
    
    USERMODE_OP    = 1
    USERMODE_VOICE = 2
    
    def __init__(self, name, topic=None):
        """
        Initialize a channel.
        """
        
        self.name = name
        self.topic = topic or ''
        
        self.users = {}
        self.modes = []
        
    def __str__(self):
        """
        Return a string representation for debugging purposes.
        """
        
        return 'Channel(Name={0}, Users={1})'.format(self.name, '|'.join(self.users))
        
    def get_modes(self):
        """
        Yeah, what to do here? do we need this actually?
        """
        
        pass
    
    def add_user(self, user, mode=None):
        """
        Add a user object to the channel.
        
        @param user: The user object.
        @param mode: The user mode in the channel.
        """
        
        self.users[user.source.nickname] = (user, mode)
        
    def set_user_mode(self, nickname, mode):
        """
        Updates the user mode.
        
        @param nickname: The nickname of the user.
        @param mode: The new user mode.
        """
        
        self.users[nickname] = (self.get_user(nickname), mode)
        
    def get_user(self, nickname):
        """
        Return a user object by its nickname.
        
        @param nickname: The nickname of the user object.
        """
        
        return self.users[nickname][0]
    
    def get_users(self):
        """
        Return the current user list of the channel.
        
        @return The user list.
        """
        
        return self.users
    
    def rename_user(self, current_nickname, new_nickname):
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

    def remove_user(self, nickname):
        """
        Remove a user object from the channel.
        
        @param nickname: The nickname of the user.
        """
        
        del self.users[nickname]
        
class ChannelList(object):
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
    
    def __init__(self, client):
        """
        Initialize the channel list.
        """
        
        self.client = client
        self.channels = {}
    
    def __str__(self):
        """
        Return a string representation for debugging purposes.
        """
        
        return 'ChannelList(Channels={0})'.format('|'.join([str(channel) for channel in self.channels.values()]))
    
    def add(self, channel):
        """
        Add a channel object to the channel list.
        
        If the channel name exists, it will be overwritten.
        
        @param channel: A channel object.
        """
        
        self.channels[channel.name] = channel
    
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
    
    def get(self, name):
        """
        Return a channel object from the channel list.
        
        @param name: The channel name.
        
        @return A channel object.
        
        @raise KeyError If the channel does not exist.
        """
        
        return self.channels[name]
    
    def get_channels(self):
        """
        Return the current user list of the channel.
        
        @return The user list.
        """
        
        return self.channels
    
    def remove(self, name):
        """
        Remove a channel object from the channel list.
        
        This will remove the channel from every user's channel list
        who had joined chat channel.
        
        @param name: The channel name.
        
        @raise KeyError If the channel does not exist.
        """
        
        channel = self.channels[name]
        
        for user_tuple in channel.get_users().values():
            user = user_tuple[0]
            user.remove_channel(channel)
            
        channel = None
        
        del self.channels[name]

        
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
        self.nicklist = [source.nickname]
        self.data = {}
        
    def __str__(self):
        """
        Return a string representation for debugging purposes.
        """

        return 'User(Nickname={0},Ident={1},Host={2},Realname={3},Channels={4})'.format(
            self.source.nickname,
            self.source.ident,
            self.source.host,
            self.realname,
            '|'.join(map(str, self.channels))
        )
        
    def set_data(self, identifier, data):
        """
        Set arbitrary information on a per-user basis.
        
        @param identifier: The identifier name.
        @param data: Any python object.
        """
        
        self.data[identifier] = data
    
    def get_data(self, identifier):
        """
        Retrieve user-based information.
        
        @param identifier: The identifier name.
        """
        
        return self.data[identifier]

    def rename(self, new_nickname):
        """
        Rename the user.
        
        Notify all channels the user and bot have in common.
        
        @param new_nickname: The user's new nickname.
        """
        
        for channel in self.channels:
            channel.rename_user(self.source.nickname, new_nickname)
            
        if new_nickname not in self.nicklist:
            self.nicklist.append(new_nickname)
        
        self.source.nickname = new_nickname

    def add_channel(self, channel, mode=None):
        """
        Adds a channel to the user.

        This should never be called directly but only by the
        Channellist module.
        
        @param channel: The channel object to add.
        """
        
        if channel in self.channels:
            raise KeyError
        
        channel.add_user(self, mode)
        self.channels.append(channel)
    
    def get_channel(self, channel):
        """
        Return a channel object by its name.
        
        @param channel: The name of the channel object.
        """
        
        return self.channel[channel]
    
    def get_channels(self):
        """
        Return a list of all channels that user and bot have in common.
        """
        
        return self.channels
    
    def is_on(self, channel):
        """
        Determines whether the user is on the given channel.
        
        @param channel: The channel object to check against.
        """
        
        return channel in self.channels

    def remove_channel(self, channel):
        """
        Removes a channel from the user.
        
        @param channel: The channel object to remove.
        """
        
        if channel not in self.channels:
            raise KeyError
        
        channel.remove_user(self.source.nickname)
        self.channels.remove(channel)


class UserList(object):
    """
    Provide a List with User entities that are known to the bot. Each
    user on a given IRC network only exists once in this list, even if
    the user shares multiple channels with the bot.
    
    Every channel is also maintaining a user list, but only uses
    references to Userlist objects.
    """
    
    def __init__(self, client):
        """
        Create an empty user list.
        """
        
        self.client = client
        self.users = {}
        
    def __str__(self):
        """
        Return a string representation for debugging purposes.
        """

        return 'Userlist(Users={0})'.format('|'.join([str(user) for user in self.users.values()]))
    
    def add(self, user):
        """
        Add a new User object to the list.
        
        @param user: The user object.
        """
        
        self.users[user.source.nickname] = user
        
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

    def get(self, nickname):
        """
        Return a user object by its nickname.
        
        @param source: The source object of the user.
        
        @return The user object, if existent.
        
        @raise KeyError if no such user was found.
        """
        
        return self.users[nickname]
    
    def get_users(self):
        """
        Return the current list of users known to the bot.
        
        @return The user list.
        """
        
        return self.users
    
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
    
    def remove(self, nickname):
        """
        Remove a user object by its nickname from the user list.
        
        Any references to channels the user had joined are also
        removed.
        
        @param source: The source object of the user.
        
        @raise KeyError if no such user was found.
        """
        
        user = self.get(nickname)
        
        for channel in user.get_channels():
            user.remove_channel(channel)
            
        user = None
            
        del self.users[nickname]
        