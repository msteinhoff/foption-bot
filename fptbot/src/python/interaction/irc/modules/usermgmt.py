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

from time import sleep
from hashlib import md5

from persistence.sqlite import DatabaseError
from interaction.irc.message import SPACE, Location
from interaction.irc.source import ClientSource
from interaction.irc.channel import Channel, ChannelList, UserList
from interaction.irc.module import InteractiveModule, ModuleError
from interaction.irc.command import JoinCmd, PartCmd, KickCmd, QuitCmd, \
                                    NickCmd, TopicCmd, PrivmsgCmd, InviteCmd,\
                                    WhoisCmd, \
                                    NamesReply, NamesEndReply, \
                                    WhoReply, WhoEndReply, \
                                    WhoisChannelsReply, WhoisIdleReply, \
                                    WhoisUserReply, WhoisServerReply, \
                                    WhoisEndReply

from interaction.irc.networks.quakenet import WhoisAuthReply

"""-----------------------------------------------------------------------------
Constants
-----------------------------------------------------------------------------"""
TOKEN_OP    = '@'
TOKEN_VOICE = '+'

"""-----------------------------------------------------------------------------
Exceptions
-----------------------------------------------------------------------------"""
class UserError(ModuleError): pass
class UserInvalid(UserError): pass
class UserExists(UserError): pass
class UserNotAuthenticated(UserError): pass
class UserNotAuthorized(UserError): pass

"""-----------------------------------------------------------------------------
Business Logic
-----------------------------------------------------------------------------"""
class Usermgmt(InteractiveModule):
    """
    Maintain a list of channels the bot has joined and users known to the bot.
    """
    
    """-------------------------------------------------------------------------
    Implementation of Module methods
    -------------------------------------------------------------------------"""
    def get_receive_listeners(self):
        """
        Return a mapping between commands and callback functions.
        
        TODO: add who/whois handling
        """
        
        listeners = InteractiveModule.get_receive_listeners(self)

        listeners.update({
            JoinCmd: self.process_join,
            PartCmd: self.process_part,
            KickCmd: self.process_kick,
            QuitCmd: self.process_quit,
            NickCmd: self.process_nick,
            InviteCmd: self.process_invite,
            
            TopicCmd: self.process_topic,
            
            NamesReply: self.process_userinfo,
            NamesEndReply: self.process_userinfo,
            WhoReply: self.process_userinfo,
            WhoEndReply: self.process_userinfo,
            WhoisUserReply: self.process_userinfo,
            WhoisChannelsReply: self.process_userinfo,
            WhoisServerReply: self.process_userinfo,
            WhoisIdleReply: self.process_userinfo,
            WhoisEndReply: self.process_userinfo
        })
        
        return listeners
        
    """-------------------------------------------------------------------------
    Implementation of InteractiveModule methods 
    -------------------------------------------------------------------------"""
    def initialize(self):
        """
        Initialize the module.
        """
        
        self.me = self.client.me
        
        self.chanlist = ChannelList(self.client)
        self.userlist = UserList(self.client)

    def module_identifier(self):
        return 'Benutzerverwaltung'
    
    def init_commands(self):
        self.add_command('listuser', None,  Location.QUERY, PrivmsgCmd, Role.ADMIN, self.list_user)
        self.add_command('adduser',  r'^$', Location.QUERY, PrivmsgCmd, Role.ADMIN, self.add_user)
        self.add_command('chguser',  r'^$', Location.QUERY, PrivmsgCmd, Role.ADMIN, self.change_user)
        self.add_command('deluser',  r'^$', Location.QUERY, PrivmsgCmd, Role.ADMIN, self.delete_user)

    def invalid_parameters(self, event, location, command, parameter):
        """
        Notify the user about invalid command syntax.
        """
        
        messages = {}
        messages['listuser'] = 'usage: .listuser'
        messages['adduser']  = 'usage: .adduser ???'
        messages['chguser']  = 'usage: .chguser ???'
        messages['deluser']  = 'usage: .deluser ???'
        
        return messages[command]
    
    """-------------------------------------------------------------------------
    Protocol handling
    -------------------------------------------------------------------------"""
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
        
        self.client.logger.info('User {0} joined {1}'.format(user, channel_name))
        
        channel = self.chanlist.request(channel_name)
        channel.add_user(user)
        
        if event.source.nickname != self.me.source.nickname:
            self.client.send_command(WhoisCmd, event.source.nickname)
    
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
            user = self.userlist.get(event.source)
            channel = self.chanlist.get(channel_name)
            
            self.client.logger.info('User {0} parted {1}'.format(user, channel_name))
            
            user.remove_channel(channel)
            
    def process_kick(self, event):
        """
        Process all incoming KICK events.
        
        This is currently mapped to process_part
        """
        # remove user from channel list
        # if user==self, notify someone
        # if user==self, on autorejoin join channel again

        channel_name = event.parameter[0]
        
        if event.source.nickname == self.me.source.nickname:
            self.client.logger.info('I was kicked from {0}'.format(channel_name))

            sleep(1)
            self.client.send_command(JoinCmd, channel_name)
        
        else:
            self.client.logger.info('User {0} was kicked from {1}'.format(channel_name))
            
            self.process_part(event)
    
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
            
        else:
            self.userlist.remove(event.source)
    
    def process_nick(self, event):
        """
        Process all incoming NICK events.
        """
        
        if event.source.nickname == self.me.source.nickname:
            return
        
        new_nickname = event.parameter[0]
        
        self.userlist.rename(event.source.nickname, new_nickname)
    
    def process_invite(self, event):
        """
        Process all incoming INVITE events.
        """
        
        pass
    
    def process_topic(self, event):
        """
        Process all incoming topic events.
        """
        
        channel_name, topic = event.parameter[1:3]
        
        channel = self.chanlist.get(channel_name)
        channel.topic = topic
    
    def process_userinfo(self, event):
        """
        Process all events regarding user information.
        
        This includes the following events:
        - NAMES
        - WHO
        - WHOIS
        
        TODO: NAMES - handle user modes
        """
        
        if event.command == NamesReply.token():
            channel_name, nicklist = event.parameter[2:4]
                    
            channel = self.chanlist.get(channel_name)
            
            for nickname in nicklist.split(SPACE):
                if nickname.startswith(TOKEN_OP):
                    nickname = nickname[1:]
                    mode = Channel.USERMODE_OP

                if nickname.startswith(TOKEN_VOICE): 
                    nickname = nickname[1:]
                    mode = Channel.USERMODE_VOICE
                
                else:
                    mode = None
                
                user = self.userlist.request(ClientSource(nickname))
                
                channel.add_user(user, mode)
                
                if nickname != self.me.source.nickname:
                    self.client.send_command(WhoisCmd, nickname)
        
        elif event.command == WhoReply.token():
            print event.parameter
        
        elif event.command == WhoisUserReply.token():
            print event.parameter
        
        elif event.command == WhoisChannelsReply.token():
            print event.parameter
        
        elif event.command == WhoisServerReply.token():
            print event.parameter
        
        elif event.command == WhoisIdleReply.token():
            print event.parameter
        
        elif event.command == WhoisAuthReply.token():
            print event.parameter

    """-------------------------------------------------------------------------
    Authorization
    -------------------------------------------------------------------------"""
    def list_user(self, event, location, command, parameter):
        return "Adminliste: (not implemented)"
    
    def add_user(self, event, location, command, parameter):
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
        
            password_hash = md5(password).hexdigest()
            
            self.persistence.insertUser(user, password_hash)
        
        except DatabaseError:
            return "Fehler beim der Accounterstellung!"
        
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

class Role(object):
    """
    Represent a role neccessary to execute a InteractiveModuleCommand.
    
    TODO: need real object here or maybe move to own python module?
    """
    
    USER  = 1 # Right.USER
    ADMIN = 3 # Right.USER | Right.ADMIN
    
    def __init__(self):
        """
        This class may currently not be instantiated. 
        """
        
        raise NotImplementedError
    
    @staticmethod
    def valid(required, role):
        """
        Check whether the user role contains sufficient rights.
        
        @param required: The minimum rights to validate.
        @param role: The actual rights.
        
        @return True if there are sufficient rights, False otherwise.
        """
        
        return (required & role == required) 
