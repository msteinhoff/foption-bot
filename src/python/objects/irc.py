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

@since May 3, 2011
@author Mario Steinhoff
"""

__version__ = '$Rev$'

_all = [
    'ServerSource',
    'ClientSource',
    'User',
    'Channel',
    'Location'
]

CHANNEL_TOKEN = '\x23'

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

class User(object):
    AWAY         = 'a'
    INVISIBLE    = 'i'
    WALLOPS      = 'w'
    RESTRICTED   = 'r'
    OPER         = 'o'
    LOCALOPER    = 'O'
    SERVERNOTICE = 's'
    
    def __init__(self, source=None, realname=None):
        """
        Initialize the user.
        
        @param source: The Source object.
        @param realname: The realname of the user.
        """
        
        self.source   = source
        self.realname = realname or ''
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

class Channel(object):
    """
    A channel entity.
    """
    
    USERMODE_NONE  = 1
    USERMODE_OP    = 2
    USERMODE_VOICE = 4
    
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
    
    def add_user(self, user, mode=USERMODE_NONE):
        """
        Add a user object to the channel.
        
        @param user: The user object.
        @param mode: The user mode in the channel.
        """
        
        self.users[user.source.nickname] = (user, mode)
        
    def get_user(self, nickname):
        """
        Return a user object by its nickname.
        
        @param nickname: The nickname of the user object.
        """
        
        return self.users[nickname][0]
    
    def set_user_mode(self, nickname, mode):
        """
        Updates the user mode.
        
        @param nickname: The nickname of the user.
        @param mode: The new user mode.
        """
        
        self.users[nickname] = (self.get_user(nickname), mode)
        
    def get_user_mode(self, nickname):
        """
        Return the mode of a user by its nickname.
        
        @param nickname: The nickname of the user object.
        """
        
        return self.users[nickname][1]
    
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
        
"""class Location(object):
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name
        
    def __str__(self):
        return self.name"""

class Location(object):
    """
    Represent a location determining where a ModuleCommand can be executed.
    
    TODO: need real object here or maybe move to own python module?
    """
    
    CHANNEL = 1
    QUERY   = 2
    BOTH    = CHANNEL | QUERY

    def __init__(self):
        """
        This class may currently not be instantiated. 
        """
        
        raise NotImplementedError

    @staticmethod
    def get(target):
        """
        Derive the location from the target.
        
        @param target: The target to check.
        
        @return CHANNEL If the target starts with a channel token,
        QUERY otherwise.
        """
        
        if target.startswith(CHANNEL_TOKEN):
            location = Location.CHANNEL
        else:
            location = Location.QUERY
        
        return location

    @staticmethod
    def valid(required, location):
        """
        Check whether the location matches the requirements.
        
        @param required: The locations that are valid.
        @param location: The actual location.
        
        @return True if the actual location is within the required location,
        False otherwise.
        """
        
        return (required | location == required)
    
    @staticmethod
    def string(location):
        """
        Return the string representation of the given location.
        
        @param location: The location.
        
        @return The location string.
        """
        
        strings = {
            1: 'Channel',
            2: 'Query'
        }
        
        return strings[location]
