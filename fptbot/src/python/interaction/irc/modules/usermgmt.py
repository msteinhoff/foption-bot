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

@since Feb 2, 2011
@author Mario Steinhoff
"""

__version__ = '$Rev$'

import time
import hashlib

from objects.principal import Role
from objects.irc import User, Channel, Location
from interaction.irc.source import ClientSource
from interaction.irc.message import SPACE
from interaction.irc.module import InteractiveModule, InteractiveModuleCommand, ModuleError

#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------
KEY_ROLE       = 'usermgmt.role'
KEY_AUTH       = 'usermgmt.auth'
KEY_IDLETIME   = 'usermgmt.idletime'
KEY_SIGNONTIME = 'usermgmt.signontime'

TOKEN_OP    = '\x40'
TOKEN_VOICE = '\x2B'

#-------------------------------------------------------------------------------
# Exceptions
#-------------------------------------------------------------------------------
class UserError(ModuleError): pass
class UserInvalid(UserError): pass
class UserExists(UserError): pass
class UserNotAuthenticated(UserError): pass
class UserNotAuthorized(UserError): pass

#-------------------------------------------------------------------------------
# Business Logic
#-------------------------------------------------------------------------------
class Usermgmt(InteractiveModule):
    """
    Maintain a list of channels the bot has joined and users known to the bot.
    """
    
    #---------------------------------------------------------------------------
    # Module implementation
    #---------------------------------------------------------------------------
    def initialize(self):
        """
        Initialize the module.
        """
        
        self.me = self.client.me
        
        self.chanlist = ChannelList(self.client)
        self.userlist = UserList(self.client)

    def get_receive_listeners(self):
        """
        Return a mapping between commands and callback functions.
        """
        
        listeners = InteractiveModule.get_receive_listeners(self)

        listeners.update({
            'Join': self.process_join,
            'Part': self.process_part,
            'Kick': self.process_kick,
            'Quit': self.process_quit,
            'Nick': self.process_nick,
            'Invite': self.process_invite,
            
            'Topic': self.process_topic,
            
            'NamesReply': self.process_names,
            'WhoReply': self.process_who,
            'WhoisUserReply': self.process_whois_user,
            'WhoisIdleReply': self.process_whois_idle,
            'WhoisAuthReply': self.process_whois_auth,
        })
        
        return listeners
        
    #---------------------------------------------------------------------------
    # InteractiveModule implementation
    #---------------------------------------------------------------------------
    def module_identifier(self):
        return 'Benutzerverwaltung'
    
    def init_commands(self):
        return [
            InteractiveModuleCommand(
                keyword='listuser',
                callback=self.list_user,
                location=Location.QUERY,
                role=Role.ADMIN),
            InteractiveModuleCommand(
                keyword='adduser',
                callback=self.insert_user,
                location=Location.QUERY,
                role=Role.ADMIN,
                pattern=r'^$',
                syntaxhint='???'
            ),
            InteractiveModuleCommand(
                keyword='chguser',
                callback=self.change_user,
                location=Location.QUERY,
                role=Role.ADMIN, 
                pattern=r'^$',
                syntaxhint='???'
            ),
            InteractiveModuleCommand(
                keyword='deluser',
                callback=self.delete_user,
                location=Location.QUERY,
                role=Role.ADMIN,
                pattern=r'^$',
                syntaxhint='???'
            )
        ]

    #---------------------------------------------------------------------------
    # protocol handling
    #---------------------------------------------------------------------------
    def process_join(self, event):
        """
        Process all incoming JOIN events.
        
        If the bot joins a channel, the channel is requested from the
        channel list. The bot is getting added as the first user to that
        channel.
        
        TODO: Check whether the bot's nickname is included in NAMES.
        TODO: If yes, do not add the bot here but check for client.me 
        TODO: in process_names.
        
        If another user joins a channel, that user is requested from
        the userlist. Then the channel is requested from the channel
        list to prevent race-conditions on close-together JOIN events
        and the user is added to the channel.
        """
        
        channel_name = event.parameter[0]
        
        if event.source.nickname == self.me.source.nickname:
            user = self.me
            
        else:
            user = self.userlist.request(event.source)
            user.set_data(KEY_ROLE, Role.USER)
        
        self.client.logger.info('User {0} joined {1}'.format(user, channel_name))
        
        channel = self.chanlist.request(channel_name)
        user.add_channel(channel, None)
        
        if event.source.nickname != self.me.source.nickname:
            whois = self.client.get_command('Whois').get_sender()
            whois.user = event.source.nickname
            whois.send()
            
    
    def process_part(self, event):
        """
        Process all incoming PART events.
        
        If the bot parts a channel, the channel is removed from the
        channel list.
        
        TODO: Moar GC when the bot parts a channel. Remove users that
        TODO: are not on any channels the bot has joined. Priority 3
        TODO: because the bot is currently only in one channel
        TODO: simultaneously.
        
        If another user parts a channel, the user is removed from that
        channel's userlist and the channel is removed from the user's
        channel list.
        """
        
        channel_name = event.parameter[0]
        
        if event.source.nickname == self.me.source.nickname:
            self.client.logger.info('I am parting {0}'.format(channel_name))

            channel = self.chanlist.remove(channel_name)
            
        else:
            user = self.userlist.get(event.source.nickname)
            channel = self.chanlist.get(channel_name)
            
            self.client.logger.info('User {0} left channel {1}'.format(user, channel_name))
            
            user.remove_channel(channel)
            
            if len(user.get_channels()) == 0:
                self.userlist.remove(user.source.nickname)
            
    def process_kick(self, event):
        """
        Process all incoming KICK events.
        
        This is currently mapped to process_part
        """
        # remove user from channel list
        # if user==self, notify someone
        # if user==self, on autorejoin join channel again

        channel_name = event.parameter[0]
        victim = event.parameter[1]
        
        if victim == self.me.source.nickname:
            self.client.logger.info('I was kicked from {0}'.format(channel_name))

            channel = self.chanlist.remove(channel_name)
            
            # remove all users that were on the channel we were kicked from
            for user in self.userlist.get_users().values():
                if len(user.get_channels()) == 0:
                    self.userlist.remove(user.source.nickname)
            
            time.sleep(1)
            
            join = self.client.get_command('Join').get_sender()
            join.channels = [channel_name]
            join.send()
        
        else:
            self.client.logger.info('User {0} was kicked from {1} by {2}'.format(victim, channel_name, event.source.nickname))
            
            user = self.userlist.get(victim)
            channel = self.chanlist.get(channel_name)
            
            user.remove_channel(channel)
            
            if len(user.get_channels()) == 0:
                self.userlist.remove(user.source.nickname)
    
    def process_quit(self, event):
        """
        Process all incoming QUIT events.
        
        If the bot quits, the channel list and user list are deleted.
        
        If another user quits, the user is removed from the user list
        and every channel's userlist the user had joined.
        """
        
        if event.source.nickname == self.me.source.nickname:
            self.chanlist = None
            self.userlist = None
            
            self.client.logger.info('I have quit from IRC')
            
        else:
            self.client.logger.info('User {0} has quit IRC'.format(event.source.nickname))
            
            self.userlist.remove(event.source)
    
    def process_nick(self, event):
        """
        Process all incoming NICK events.
        """
        
        if event.source.nickname == self.me.source.nickname:
            return
        
        new_nickname = event.parameter[0]
        
        self.client.logger.info('User {0} is now known as {1}'.format(event.source.nickname, new_nickname))
        
        self.userlist.rename(event.source.nickname, new_nickname)
        
    def process_invite(self, event):
        """
        Process all incoming INVITE events.
        """
        
        channel_name = ''
        nickname = ''
        
        self.client.logger.info('I were invited into {0} by {1}'.format(channel_name, nickname))
        
        pass
    
    def process_topic(self, event):
        """
        Process all incoming topic events.
        """
        
        channel_name, topic = event.parameter[1:3]
        
        channel = self.chanlist.get(channel_name)
        channel.topic = topic
    
    def process_names(self, event):
        """
        Process NAMES events.
        
        TODO: handle user modes
        """
        
        channel_name, nicklist = event.parameter[2:4]
                
        channel = self.chanlist.get(channel_name)
        
        for nickname in nicklist.split(SPACE):
            if nickname.startswith(TOKEN_OP):
                nickname = nickname[1:]
                mode = Channel.USERMODE_OP

            elif nickname.startswith(TOKEN_VOICE): 
                nickname = nickname[1:]
                mode = Channel.USERMODE_VOICE
            
            else:
                mode = None
            
            user = self.userlist.request(ClientSource(nickname=nickname))
            user.set_data(KEY_ROLE, Role.USER)
            user.add_channel(channel, mode)
            
            if nickname != self.me.source.nickname:
                whois = self.client.get_command('Whois').get_sender()
                whois.user = nickname
                whois.send()
        
    def process_who(self, event):
        """
        Process WHO events.
        """
        
        print event.parameter
    
    def process_whois_user(self, event):
        """
        Process the user part of a WHOIS event.
        """
        
        nickname = event.parameter[1]
        ident = event.parameter[2]
        host = event.parameter[3]
        realname = event.parameter[5]
        
        user = self.userlist.get(nickname)
        user.source.ident = ident
        user.source.host = host
        user.source.realname = realname
        
        self.client.logger.info('User information: {0} has Ident {1}, Hostname {2}, Realname {3}'.format(nickname, ident, host, realname))
    
    def process_whois_idle(self, event):
        """
        Process the idle part of a WHOIS event.
        """
        
        nickname = event.parameter[1]
        idle_time = event.parameter[2]
        signon_time = event.parameter[3]
        
        user = self.userlist.get(nickname)
        user.set_data(KEY_IDLETIME, idle_time)
        user.set_data(KEY_SIGNONTIME, signon_time)
        
        self.client.logger.info('User information: {0} has idled {1} seconds'.format(nickname, idle_time))
        self.client.logger.info('User information: {0} has signed on at {1}'.format(nickname, signon_time))
    
    def process_whois_auth(self, event):
        """
        Process the auth part of a WHOIS event.
        """
        
        nickname = event.parameter[1]
        auth = event.parameter[2]
        
        user = self.userlist.get(nickname)
        user.set_data(KEY_ROLE, Role.AUTHED)
        user.set_data(KEY_AUTH, auth)
        
        self.client.logger.info('User information: {0} is authed as {1}'.format(nickname, auth))
        
    #---------------------------------------------------------------------------
    # User management
    #---------------------------------------------------------------------------
    def list_user(self, event, location, command, parameter):
        return "Adminliste: (not implemented)"
    
    def insert_user(self, event, location, command, parameter):
        """
        .adduser [password]
        """
        
        password = parameter[0]
        
        try:
            user = self.getAuth(event.source)
            return "User '???' wurde als Admin hinzugefügt."
        
            if not user:
                raise UserNotAuthenticated
            
            if self.isPrivateUser(user):
                raise UserExists
        
            # TODO impl
            #password_hash = hashlib.sha1(password).hexdigest()
        
        except UserNotAuthenticated:
            return "Du bist nicht geauthed!"
        
        except UserExists:
            return "Du hast bereits einen Account!"
        
        return "Dein Account wurde erstellt!"
    
    def change_user(self, event, location, command, parameter):
        pass

    def delete_user(self, event, location, command, parameter):
        return "User '???' als Admin entfernt."
        return "User '???' befindet sich nicht in der Liste."

    #---------------------------------------------------------------------------
    # public API
    #---------------------------------------------------------------------------
    def get_role(self, nickname):
        user = self.userlist.get(nickname=nickname)
        
        try:
            return user.get_data(identifier=KEY_ROLE)
        
        except KeyError:
            return Role.USER


class ChannelList(object):
    """
    Maintain a list of channels the bot has joined.
     
    The information this module contains include 
    - the channel name
    - the channel topic
    - the channel modes
    - a list of ban masks
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
            channel = Channel(name=name)
            
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
    
    def get_all(self):
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
            user = User(source=source, realname=realname)
            
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
    
    def get_all(self):
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
        
        self.users[new_nickname] = self.users[current_nickname]
        self.users[new_nickname].rename(new_nickname)
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
