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

from interaction.irc.module  import InteractiveModule, Location, Role
from interaction.irc.message import SPACE
from interaction.irc.command import JoinCmd, PartCmd, KickCmd, QuitCmd, \
                                    NickCmd, TopicCmd, PrivmsgCmd, InviteCmd, \
                                    NamesReply, NamesEndReply, \
                                    WhoReply, WhoEndReply, \
                                    WhoisChannelsReply, WhoisIdleReply, \
                                    WhoisUserReply
from interaction.irc.channel import Channellist, Userlist
from interaction.irc.source  import ClientSource

OP_TOKEN = '@'
VOICE_TOKEN = '+'

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
        return {
            PrivmsgCmd:     self.parse,
            
            JoinCmd:        self.process_join,
            PartCmd:        self.process_part,
            KickCmd:        self.process_kick,
            QuitCmd:        self.process_quit,
            NickCmd:        self.process_nick,
            InviteCmd:      self.process_invite,
            
            TopicCmd:       self.process_topic,
            
            NamesReply:     self.process_names,
            NamesEndReply:  self.process_namesend,
            
            WhoReply:       self.process_who,
            WhoEndReply:    self.process_whoend,
        }
        
    """-------------------------------------------------------------------------
    Implementation of InteractiveModule methods 
    -------------------------------------------------------------------------"""
    def initialize(self):
        """
        Initialize the module.
        """
        
        self.me = self.client.me
        
        self.chanlist = Channellist()
        self.userlist = Userlist()

    def module_identifier(self):
        return 'Benutzerverwaltung'
    
    def init_commands(self):
        self.add_command('listadmin', None, Location.QUERY, PrivmsgCmd, Role.ADMIN, self.list_admin)
        self.add_command('addadmin',  r'^(.+)$', Location.QUERY, PrivmsgCmd, Role.ADMIN, self.add_admin)
        self.add_command('deladmin',  r'^(.+)$', Location.QUERY, PrivmsgCmd, Role.ADMIN, self.delete_admin)
        
    def invalid_parameters(self, event, location, command, parameter):
        pass
    
    """-------------------------------------------------------------------------
    User handling 
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
            channel = self.chanlist.request(channel_name)
            channel.addUser(self.me)
        
        else:
            user = self.userlist.request(event.source)
            
            channel = self.chanlist.request(channel_name)
            channel.addUser(user)
    
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
            channel = self.chanlist.remove(channel_name)
            
        else:
            channel = self.chanlist.get(channel_name)
            channel.removeUser(event.source.nickname)
            
    def process_kick(self, event):
        """
        Process all incoming KICK events.
        
        This is currently mapped to process_part
        """
        # remove user from channel list
        # if user==self, notify someone
        # if user==self, on autorejoin join channel again

        self.process_part(event)
        pass
    
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
    
    def process_names(self, event):
        """
        Process all incoming NAMES replies.
        
        TODO: handle user modes
        """
        
        channel_name, nicklist = event.parameter[2:4]
                
        channel = self.chanlist.get(channel_name)
        
        for nick in nicklist.split(SPACE):
            if nick.startswith(OP_TOKEN) or nick.startswith(VOICE_TOKEN): 
                nick = nick[1:]
            
            user = self.userlist.request(ClientSource(nick, '', ''))
            
            channel.addUser(user)
        
        pass
    
    def process_namesend(self, event):
        """
        Process additional logic after the NAMES reply has finished.
        
        TODO: send WHO command 
        """
        
        pass
        
    def process_who(self, event):
        """
        Process all incoming WHO replies.
        """
        
        pass
        
    def process_whoend(self, event):
        """
        Process additional logic after the WHO reply has finished.
        """
        
        pass

    """-------------------------------------------------------------------------
    Role handling 
    -------------------------------------------------------------------------"""
    def list_admin(self, event, location, command, parameter):
        return "Adminliste: (not implemented)"
    
    def add_admin(self, event, location, command, parameter):
        return "User '???' wurde als Admin hinzugefügt."
    
    def delete_admin(self, event, location, command, parameter):
        return "User '???' als Admin entfernt."
        return "User '???' befindet sich nicht in der Liste."
