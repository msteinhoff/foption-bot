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

from interaction.irc.message import Event

class Command(object):
    """
    A IRC client command.
    """
    
    def __init__(self, client):
        """
        Initialize the command.
        
        @param client: The IRC client instance.
        """
        
        self.client = client
        self._receive_listener = []
    
    @staticmethod
    def token(self):
        """
        Return the IRC command token.
        
        This method must be overriden each sub-class.
        """
        
        raise NotImplementedError
    
    def add_receive_listener(self, callback):
        """
        Add a receive listener to the command instance.
        
        The callback function is called everytime a receive event
        occured.
        
        @param callback: A pointer to the callback function. 
        """
        
        self._receive_listener.append(callback)
        
    def receive(self, event):
        """
        Push a receive event to the command handler.
        
        This will first call the internal command logic and then notice
        additional listeners about the event. The event itself can be
        modified at any time, altough this is not encouraged.
        
        @param event: The event.
        """
        
        self._receive(event)
        
        [callback(event) for callback in self._receive_listener]
    
    def send(self, *args):
        """
        Push a send event to the command handler.
        
        This enables a high-level API for IRC commands. Each command
        handler can define python parameters, clean user input and
        format input data according to the IRC specifications. 
        """
        
        self._send(*args)

    def _receive(self, event):
        """
        Implement general command logic for receive events.
        
        This method can be overriden in sub-classes to implement
        module-independent logic.
        
        @param event: The event. 
        """
        
        pass
    
    def _send(self, *args):
        """
        Implement general command logic for receive events.
        
        This method can be overriden in sub-classes to implement
        module-independent logic.
        
        @param event: The event. 
        """
        
        pass

"""-------------------------------------------------------------------------
Section: 3.1 Connection Registration
----------------------------------------------------------------------------
The commands described here are used to register a connection with an
IRC server as a user as well as to correctly disconnect.

A "PASS" command is not required for a client connection to be
registered, but it MUST precede the latter of the NICK/USER
combination (for a user connection) or the SERVICE command (for a
service connection). The RECOMMENDED order for a client to register
is as follows:

                        1. Pass message
        2. Nick message                 2. Service message
        3. User message

Upon success, the client will receive an RPL_WELCOME (for users) or
RPL_YOURESERVICE (for services) message indicating that the
connection is now registered and known the to the entire IRC network.
The reply message MUST contain the full client identifier upon which
it was registered.
----------------------------------------------------------------------------
3.1.1  Password message ..................................  10    - not needed
3.1.2  Nick message ......................................  10    - needed
3.1.3  User message ......................................  11    - needed
3.1.4  Oper message ......................................  12    - not needed
3.1.5  User mode message .................................  12    - needed
3.1.6  Service message ...................................  13    - not needed
3.1.7  Quit ..............................................  14    - needed
3.1.8  Squit .............................................  15    - not needed
-------------------------------------------------------------------------"""

class NickCmd(Command):
    """
    Command: NICK
    Parameters: <nickname>
    
    NICK command is used to give user a nickname or change the existing
    one.
    
    Numeric Replies:
    
            ERR_NONICKNAMEGIVEN             ERR_ERRONEUSNICKNAME
            ERR_NICKNAMEINUSE               ERR_NICKCOLLISION
            ERR_UNAVAILRESOURCE             ERR_RESTRICTED
    """
    
    @staticmethod
    def token():
        return 'NICK'
    
    def _receive(self, event):
        """
        Update the client's identity with the current nickname.
        """
        
        if event.source.nickname == self.client.me.source.nickname:
            self.client.me.rename(event.parameter[0])
    
    def _send(self, nickname):
        """
        Send a request to set/change the client's nickname.
        """
        
        self.client.send_event(Event(None, self.token(), [nickname]))

class UserCmd(Command):
    """
    Command: USER
    Parameters: <user> <mode> <unused> <realname>
    
    The USER command is used at the beginning of connection to specify
    the username, hostname and realname of a new user.
    
    The <mode> parameter should be a numeric, and can be used to
    automatically set user modes when registering with the server.  This
    parameter is a bitmask, with only 2 bits having any signification: if
    the bit 2 is set, the user mode 'w' will be set and if the bit 3 is
    set, the user mode 'i' will be set.  (See Section 3.1.5 "User
    Modes").
    
    The <realname> may contain space characters.
    
    Numeric Replies:
    
            ERR_NEEDMOREPARAMS              ERR_ALREADYREGISTRED
    """
    
    @staticmethod
    def token():
        return 'USER'
    
    def _send(self, realname, ident):
        """
        Register with the IRC server.
        """
        
        self.client.send_event(Event(None, self.token(), [ident, '0', '*', '{0}'.format(realname)]))


class ModeCmd(Command):
    """
    Command: MODE
    Parameters: <nickname>
               *( ( "+" / "-" ) *( "i" / "w" / "o" / "O" / "r" ) )
    
    The user MODE's are typically changes which affect either how the
    client is seen by others or what 'extra' messages the client is sent.
    
    [...] If no other parameter is given, then the server will return
    the current  settings for the nick.
    
      The available modes are as follows:
    
           a - user is flagged as away;
           i - marks a users as invisible;
           w - user receives wallops;
           r - restricted user connection;
           o - operator flag;
           O - local operator flag;
           s - marks a user for receipt of server notices.
    
    Additional modes may be available later on.
    
    [...]
    
    Numeric Replies:
    
           ERR_NEEDMOREPARAMS              ERR_USERSDONTMATCH
           ERR_UMODEUNKNOWNFLAG            RPL_UMODEIS
    
    [...]
    
    Command: MODE
    Parameters: <channel> *( ( "-" / "+" ) *<modes> *<modeparams> )
    
    The MODE command is provided so that users may query and change the
    characteristics of a channel.  For more details on available modes
    and their uses, see "Internet Relay Chat: Channel Management" [IRC-
    CHAN].  Note that there is a maximum limit of three (3) changes per
    command for modes that take a parameter.
    
    Numeric Replies:
    
            ERR_NEEDMOREPARAMS              ERR_KEYSET
            ERR_NOCHANMODES                 ERR_CHANOPRIVSNEEDED
            ERR_USERNOTINCHANNEL            ERR_UNKNOWNMODE
            RPL_CHANNELMODEIS
            RPL_BANLIST                     RPL_ENDOFBANLIST
            RPL_EXCEPTLIST                  RPL_ENDOFEXCEPTLIST
            RPL_INVITELIST                  RPL_ENDOFINVITELIST
            RPL_UNIQOPIS
    """

    
    @staticmethod
    def token():
        return 'MODE'
    
    def _receive(self, event):
        pass
    
    def _send(self, event):
        pass

class QuitCmd(Command):
    """
    3.1.7 Quit
    
          Command: QUIT
       Parameters: [ <Quit Message> ]
    
       A client session is terminated with a quit message.  The server
       acknowledges this by sending an ERROR message to the client.
    
       Numeric Replies:
    
               None.
    
       Example:
    
       QUIT :Gone to have lunch        ; Preferred message format.
    
       :syrk!kalt@millennium.stealth.net QUIT :Gone to have lunch ; User
                                       syrk has quit IRC to have lunch.
    """
    
    @staticmethod
    def token():
        return 'QUIT'
    
    def _send(self, message=None):
        """
        Send a quit command with a optional quit message.
        
        @param message: The quit message.
        """
        
        parameter = []
        
        if message is not None:
            parameter.append(message)
        
        self.client.send_event(Event(None, self.token(), parameter))


"""
----------------------------------------------------------------------------
Section: 3.2 Channel operations
----------------------------------------------------------------------------
This group of messages is concerned with manipulating channels, their
properties (channel modes), and their contents (typically users).
For this reason, these messages SHALL NOT be made available to
services.

All of these messages are requests which will or will not be granted
by the server.  The server MUST send a reply informing the user
whether the request was granted, denied or generated an error.  When
the server grants the request, the message is typically sent back
(eventually reformatted) to the user with the prefix set to the user
itself.
----------------------------------------------------------------------------
3.2.1  Join message ......................................  16    - needed
3.2.2  Part message ......................................  17    - needed
3.2.3  Channel mode message ..............................  18    - needed
3.2.4  Topic message .....................................  19    - needed
3.2.5  Names message .....................................  20    - needed
3.2.6  List message ......................................  21    - not needed
3.2.7  Invite message ....................................  21    - not needed (maybe implemented in the future)
3.2.8  Kick command ......................................  22    - needed
-------------------------------------------------------------------------"""

class JoinCmd(Command):
    """
    Command: JOIN
    Parameters: ( <channel> *( "," <channel> ) [ <key> *( "," <key> ) ] )
                / "0"
    
    The JOIN command is used by a user to request to start listening to
    the specific channel.  Servers MUST be able to parse arguments in the
    form of a list of target, but SHOULD NOT use lists when sending JOIN
    messages to clients.
    
    Once a user has joined a channel, he receives information about
    all commands his server receives affecting the channel.  This
    includes JOIN, MODE, KICK, PART, QUIT and of course PRIVMSG/NOTICE.
    This allows channel members to keep track of the other channel
    members, as well as channel modes.
    
    If a JOIN is successful, the user receives a JOIN message as
    confirmation and is then sent the channel's topic (using RPL_TOPIC) and
    the list of users who are on the channel (using RPL_NAMREPLY), which
    MUST include the user joining.
    
    [...]
    
    Numeric Replies:
    
            ERR_NEEDMOREPARAMS              ERR_BANNEDFROMCHAN
            ERR_INVITEONLYCHAN              ERR_BADCHANNELKEY
            ERR_CHANNELISFULL               ERR_BADCHANMASK
            ERR_NOSUCHCHANNEL               ERR_TOOMANYCHANNELS
            ERR_TOOMANYTARGETS              ERR_UNAVAILRESOURCE
            RPL_TOPIC
    """
    @staticmethod
    def token():
        return 'JOIN'
    
    def _send(self, channels, keys=None):
        """
        Join a channel.
        
        @param channels: The channel names.
        @param keys: The optional channel keys.
        """
        
        if channels is None:
            parameter = ['0']
        
        else:
            parameter = [','.join(channels)]
            
            if keys is not None:
                parameter.append(','.join(keys))
        
        self.client.send_event(Event(None, self.token(), parameter))

class PartCmd(Command):
    """
    Command: PART
    Parameters: <channel> *( "," <channel> ) [ <Part Message> ]
    
    The PART command causes the user sending the message to be removed
    from the list of active members for all given channels listed in the
    parameter string.  If a "Part Message" is given, this will be sent
    instead of the default message, the nickname.  This request is always
    granted by the server.
    
    Servers MUST be able to parse arguments in the form of a list of
    target, but SHOULD NOT use lists when sending PART messages to
    clients.
    
    Numeric Replies:
    
            ERR_NEEDMOREPARAMS              ERR_NOSUCHCHANNEL
            ERR_NOTONCHANNEL
    """
    @staticmethod
    def token():
        return 'PART'
    
    def _send(self, channel, message=None):
        """
        Part a channel.
        
        @param channel: The channel name.
        @param message: The optional part message.
        """
        
        parameter = [channel]
        
        if message is not None:
            parameter.append(message)
        
        self.client.send_event(Event(None, self.token(), parameter))

"""
Because user mode message and channel mode are using the same command,
user mode and channel mode logic are implemented in the same class at 
the user section. 
"""

class TopicCmd(Command):
    """
    Command: TOPIC
    Parameters: <channel> [ <topic> ]
    
    The TOPIC command is used to change or view the topic of a channel.
    The topic for channel <channel> is returned if there is no <topic>
    given.  If the <topic> parameter is present, the topic for that
    channel will be changed, if this action is allowed for the user
    requesting it.  If the <topic> parameter is an empty string, the
    topic for that channel will be removed.

    Numeric Replies:
    
            ERR_NEEDMOREPARAMS              ERR_NOTONCHANNEL
            RPL_NOTOPIC                     RPL_TOPIC
            ERR_CHANOPRIVSNEEDED            ERR_NOCHANMODES
    """
    @staticmethod
    def token():
        return 'TOPIC'
    
    def _send(self, channel, topic=None):
        """
        Get/set a channels topic.
        """
        
        self.client.send_event(Event(None, self.token(), [topic]))

class NamesCmd(Command):
    """
    Command: NAMES
    Parameters: [ <channel> *( "," <channel> ) [ <target> ] ]
    
    By using the NAMES command, a user can list all nicknames that are
    visible to him. For more details on what is visible and what is not,
    see "Internet Relay Chat: Channel Management" [IRC-CHAN].  The
    <channel> parameter specifies which channel(s) to return information
    about.  There is no error reply for bad channel names.
    
    If no <channel> parameter is given, a list of all channels and their
    occupants is returned.  At the end of this list, a list of users who
    are visible but either not on any channel or not on a visible channel
    are listed as being on `channel' "*".
    
    If the <target> parameter is specified, the request is forwarded to
    that server which will generate the reply.
    
    Wildcards are allowed in the <target> parameter.
    
    Numerics:
    
            ERR_TOOMANYMATCHES              ERR_NOSUCHSERVER
            RPL_NAMREPLY                    RPL_ENDOFNAMES
    """
    @staticmethod
    def token():
        return 'NAMES'
    
    def _send(self, channels):
        """
        Request a NAMES list.
        """
        
        self.client.send_event(Event(None, self.token(), [','.join(channels)]))

class InviteCmd(Command):
    """
    Command: INVITE
    Parameters: <nickname> <channel>
    
    The INVITE command is used to invite a user to a channel.  The
    parameter <nickname> is the nickname of the person to be invited to
    the target channel <channel>.  There is no requirement that the
    channel the target user is being invited to must exist or be a valid
    channel.  However, if the channel exists, only members of the channel
    are allowed to invite other users.  When the channel has invite-only
    flag set, only channel operators may issue INVITE command.

    Only the user inviting and the user being invited will receive
    notification of the invitation.  Other channel members are not
    notified.  (This is unlike the MODE changes, and is occasionally the
    source of trouble for users.)
    
    Numeric Replies:
    
            ERR_NEEDMOREPARAMS              ERR_NOSUCHNICK
            ERR_NOTONCHANNEL                ERR_USERONCHANNEL
            ERR_CHANOPRIVSNEEDED
            RPL_INVITING                    RPL_AWAY
    """
    @staticmethod
    def token():
        return 'INVITE'
    
    def _send(self, nickname, channel):
        self.client.send_event(Event(None, self.token(), [nickname, channel]))

class KickCmd(Command):
    """
    Command: KICK
    Parameters: <channel> *( "," <channel> ) <user> *( "," <user> )
                [<comment>]
    
    The KICK command can be used to request the forced removal of a user
    from a channel.  It causes the <user> to PART from the <channel> by
    force.  For the message to be syntactically correct, there MUST be
    either one channel parameter and multiple user parameter, or as many
    channel parameters as there are user parameters.  If a "comment" is
    given, this will be sent instead of the default message, the nickname
    of the user issuing the KICK.
    
    The server MUST NOT send KICK messages with multiple channels or
    users to clients.  This is necessarily to maintain backward
    compatibility with old client software.
    
    Numeric Replies:
    
            ERR_NEEDMOREPARAMS              ERR_NOSUCHCHANNEL
            ERR_BADCHANMASK                 ERR_CHANOPRIVSNEEDED
            ERR_USERNOTINCHANNEL            ERR_NOTONCHANNEL
    """
    @staticmethod
    def token():
        return 'KICK'
    
    def _send(self, channels, users, message=None):
        parameter = [','.join(channels), ','.join(users)]
        
        if message is not None:
            parameter.append(message)
        
        self.client.send_event(Event(None, self.token(), parameter))


"""
----------------------------------------------------------------------------
Section: 3.3 Sending messages
----------------------------------------------------------------------------
The main purpose of the IRC protocol is to provide a base for clients
to communicate with each other.  PRIVMSG, NOTICE and SQUERY
(described in Section 3.5 on Service Query and Commands) are the only
messages available which actually perform delivery of a text message
from one client to another - the rest just make it possible and try
to ensure it happens in a reliable and structured manner.
----------------------------------------------------------------------------
3.3.1  Private messages ..................................  23    - needed
3.3.2  Notice ............................................  24    - needed
-------------------------------------------------------------------------"""

class PrivmsgCmd(Command):
    """
    Command: PRIVMSG
    Parameters: <msgtarget> <text to be sent>
    
    PRIVMSG is used to send private messages between users, as well as to
    send messages to channels.  <msgtarget> is usually the nickname of
    the recipient of the message, or a channel name.
    
    The <msgtarget> parameter may also be a host mask (#<mask>) or server
    mask ($<mask>).  In both cases the server will only send the PRIVMSG
    to those who have a server or host matching the mask.  The mask MUST
    have at least 1 (one) "." in it and no wildcards following the last
    ".".  This requirement exists to prevent people sending messages to
    "#*" or "$*", which would broadcast to all users.  Wildcards are the
    '*' and '?'  characters.  This extension to the PRIVMSG command is
    only available to operators.
    
    Numeric Replies:
    
            ERR_NORECIPIENT                 ERR_NOTEXTTOSEND
            ERR_CANNOTSENDTOCHAN            ERR_NOTOPLEVEL
            ERR_WILDTOPLEVEL                ERR_TOOMANYTARGETS
            ERR_NOSUCHNICK
            RPL_AWAY
    """
    @staticmethod
    def token():
        return 'PRIVMSG'
    
    def _receive(self, event):
        if not event.parameter[0].startswith('#') and event.parameter[1] == 'fotzenscheisse':
            self.client.send_command(QuitCmd)
    
    def _send(self, target, text):
        self.client.send_event(Event(None, self.token(), [target, text]))

class NoticeCmd(Command):
    """
    Command: NOTICE
    Parameters: <msgtarget> <text>
    
    The NOTICE command is used similarly to PRIVMSG.  The difference
    between NOTICE and PRIVMSG is that automatic replies MUST NEVER be
    sent in response to a NOTICE message.  This rule applies to servers
    too - they MUST NOT send any error reply back to the client on
    receipt of a notice.  The object of this rule is to avoid loops
    between clients automatically sending something in response to
    something it received.
    
    This command is available to services as well as users.
    
    This is typically used by services, and automatons (clients with
    either an AI or other interactive program controlling their actions).
    
    See PRIVMSG for more details on replies and examples.
    """
    @staticmethod
    def token():
        return 'NOTICE'
    
    def _send(self, target, text):
        self.client.send_event(Event(None, self.token(), [target, text]))


"""
----------------------------------------------------------------------------
Section: 3.4 Server queries and commands
----------------------------------------------------------------------------
3.4.1  Motd message ......................................  25    - needed
3.4.2  Lusers message ....................................  25    - not needed
3.4.3  Version message ...................................  26    - not needed
3.4.4  Stats message .....................................  26    - not needed
3.4.5  Links message .....................................  27    - not needed
3.4.6  Time message ......................................  28    - not needed
3.4.7  Connect message ...................................  28    - not needed
3.4.8  Trace message .....................................  29    - not needed
3.4.9  Admin command .....................................  30    - not needed
3.4.10 Info command ......................................  31    - not needed
-------------------------------------------------------------------------"""
class MotdCmd(Command):
    """
    Command: MOTD
    Parameters: [ <target> ]
    
    The MOTD command is used to get the "Message Of The Day" of the given
    server, or current server if <target> is omitted.
    
    Wildcards are allowed in the <target> parameter.
    
    Numeric Replies:
    
            RPL_MOTDSTART                   RPL_MOTD
            RPL_ENDOFMOTD                   ERR_NOMOTD

    """
    @staticmethod
    def token():
        return 'MOTD'
    
    def _send(self, target=None):
        parameter = []
        
        if target is not None:
            parameter.append(target)
        
        self.client.send_event(Event(None, self.token(), parameter))


"""
----------------------------------------------------------------------------
Section: 3.5 Service query and commands
----------------------------------------------------------------------------
3.5.1  Servlist message ..................................  31    - not needed
3.5.2  Squery ............................................  32    - not needed
-------------------------------------------------------------------------"""

"""
----------------------------------------------------------------------------
Section: 3.6 User based queries
----------------------------------------------------------------------------
3.6.1  Who query .........................................  32    - needed
3.6.2  Whois query .......................................  33    - needed
3.6.3  Whowas ............................................  34    - not needed
-------------------------------------------------------------------------"""
class WhoCmd(Command):
    """
    Command: WHO
    Parameters: [ <mask> [ "o" ] ]
    
    The WHO command is used by a client to generate a query which returns
    a list of information which 'matches' the <mask> parameter given by
    the client.  In the absence of the <mask> parameter, all visible
    (users who aren't invisible (user mode +i) and who don't have a
    common channel with the requesting client) are listed.  The same
    result can be achieved by using a <mask> of "0" or any wildcard which
    will end up matching every visible user.
    
    The <mask> passed to WHO is matched against users' host, server, real
    name and nickname if the channel <mask> cannot be found.
    
    If the "o" parameter is passed only operators are returned according
    to the <mask> supplied.
    
    Numeric Replies:
    
            ERR_NOSUCHSERVER
            RPL_WHOREPLY                  RPL_ENDOFWHO
    """
    @staticmethod
    def token():
        return 'WHO'
    
    def _send(self, mask, operators=False):
        parameter = mask
        
        if operators:
            parameter.append('o')
        
        self.client.send_event(Event(None, self.token(), parameter))


class WhoisCmd(Command):
    """
    Command: WHOIS
    Parameters: [ <target> ] <mask> *( "," <mask> )
    
    This command is used to query information about particular user.
    The server will answer this command with several numeric messages
    indicating different statuses of each user which matches the mask (if
    you are entitled to see them).  If no wildcard is present in the
    <mask>, any information about that nick which you are allowed to see
    is presented.
    
    If the <target> parameter is specified, it sends the query to a
    specific server.  It is useful if you want to know how long the user
    in question has been idle as only local server (i.e., the server the
    user is directly connected to) knows that information, while
    everything else is globally known.
    
    Wildcards are allowed in the <target> parameter.
    
    Numeric Replies:
    
            ERR_NOSUCHSERVER              ERR_NONICKNAMEGIVEN
            RPL_WHOISUSER                 RPL_WHOISCHANNELS
            RPL_WHOISCHANNELS             RPL_WHOISSERVER
            RPL_AWAY                      RPL_WHOISOPERATOR
            RPL_WHOISIDLE                 ERR_NOSUCHNICK
            RPL_ENDOFWHOIS

    """
    @staticmethod
    def token():
        return 'WHOIS'
    
    def _send(self, user, server=None):
        parameter = []
        
        if server is not None:
            parameter.append(server)
        
        # add user 2x for extended whois
        parameter.append(user)
        parameter.append(user)
        
        self.client.send_event(Event(None, self.token(), parameter))

"""
----------------------------------------------------------------------------
Section: 3.7 Miscellaneous messages
----------------------------------------------------------------------------
3.7.1  Kill message ......................................  35    - not needed
3.7.2  Ping message ......................................  36    - needed
3.7.3  Pong message ......................................  37    - needed
3.7.4  Error .............................................  37    - not needed
-------------------------------------------------------------------------"""
class PingCmd(Command):
    """
    Command: PING
    Parameters: <server1> [ <server2> ]
    
    The PING command is used to test the presence of an active client or
    server at the other end of the connection.  Servers send a PING
    message at regular intervals if no other activity detected coming
    from a connection.  If a connection fails to respond to a PING
    message within a set amount of time, that connection is closed.  A
    PING message MAY be sent even if the connection is active.
    
    When a PING message is received, the appropriate PONG message MUST be
    sent as reply to <server1> (server which sent the PING message out)
    as soon as possible.  If the <server2> parameter is specified, it
    represents the target of the ping, and the message gets forwarded
    there.
    
    Numeric Replies:
    
            ERR_NOORIGIN                  ERR_NOSUCHSERVER
    """
    @staticmethod
    def token():
        return 'PING'
    
    def _receive(self, event):
        if len(event.parameter) == 1:
            self.client.send_command(PongCmd, event.parameter[0])
        
        if len(event.parameter) == 2:
            self.client.send_command(PongCmd, event.parameter[0], event.parameter[1])

class PongCmd(Command):
    """
    Command: PONG
    Parameters: <server> [ <server2> ]
    
    PONG message is a reply to ping message.  If parameter <server2> is
    given, this message MUST be forwarded to given target.  The <server>
    parameter is the name of the entity who has responded to PING message
    and generated this message.
    
    Numeric Replies:
    
            ERR_NOORIGIN                  ERR_NOSUCHSERVER
    """
    @staticmethod
    def token():
        return 'PONG'
    
    def _send(self, server, server2=None):
        parameter = [server]
        
        if server2 is not None:
            parameter.append(server2)
        
        self.client.send_event(Event(None, self.token(), parameter))

"""-----------------------------------------------------------------------------
   5.  Replies ....................................................  43
      5.1  Command responses ......................................  43
      5.2  Error Replies ..........................................  53
      5.3  Reserved numerics ......................................  59

Numerics in the range from 001 to 099 are used for client-server
connections only and should never travel between servers.
-----------------------------------------------------------------------------"""
class WelcomeReply(Command):
    @staticmethod
    def token():
        return '001'

class YourHostReply(Command):
    @staticmethod
    def token():
        return '002'

class CreatedReply(Command):
    @staticmethod
    def token():
        return '003'

class MyInfoReply(Command):
    @staticmethod
    def token():
        return '004'
    
class BounceReply(Command):
    @staticmethod
    def token():
        return '005'

"""-----------------------------------------------------------------------------
Replies generated in the response to commands are found in the
range from 200 to 399.
-----------------------------------------------------------------------------"""
class AwayReply(Command):
    @staticmethod
    def token():
        return '301'

class WhoisUserReply(Command):
    @staticmethod
    def token():
        return '311'

class WhoisServerReply(Command):
    @staticmethod
    def token():
        return '312'

class WhoisOperatorReply(Command):
    @staticmethod
    def token():
        return '313'

class WhoEndReply(Command):
    @staticmethod
    def token():
        return '315'

class WhoisIdleReply(Command):
    @staticmethod
    def token():
        return '317'

class WhoisEndReply(Command):
    @staticmethod
    def token():
        return '318'

class WhoisChannelsReply(Command):
    @staticmethod
    def token():
        return '319'

class UniqueOpIsReply(Command):
    @staticmethod
    def token():
        return '325'

class ChannelModeIsReply(Command):
    @staticmethod
    def token():
        return '324'

class NoTopicReply(Command):
    @staticmethod
    def token():
        return '331'

class TopicReply(Command):
    @staticmethod
    def token():
        return '332'

class InvitingReply(Command):
    @staticmethod
    def token():
        return '341'

class InviteListReply(Command):
    @staticmethod
    def token():
        return '346'

class InviteListEndReply(Command):
    @staticmethod
    def token():
        return '347'

class ExceptListReply(Command):
    @staticmethod
    def token():
        return '348'

class ExceptListEndReply(Command):
    @staticmethod
    def token():
        return '349'

class WhoReply(Command):
    @staticmethod
    def token():
        return '352'

class NamesReply(Command):
    """
    353    RPL_NAMREPLY
    "( "=" / "*" / "@" ) <channel>
    
    :[ "@" / "+" ] <nick> *( " " [ "@" / "+" ] <nick> )
            
      "@" is used for secret channels
      "*" for private channels, and
      "=" for others (public channels).
    """
    @staticmethod
    def token():
        return '353'

class NamesEndReply(Command):
    @staticmethod
    def token():
        return '366'

class BanListReply(Command):
    @staticmethod
    def token():
        return '367'

class BanListEndReply(Command):
    @staticmethod
    def token():
        return '368'

class MotdReply(Command):
    @staticmethod
    def token():
        return '372'

class MotdStartReply(Command):
    @staticmethod
    def token():
        return '375'

class MotdEndReply(Command):
    @staticmethod
    def token():
        return '376'
    
    def _receive(self, event):
        self.client.post_connect()

"""-----------------------------------------------------------------------------
Error replies are found in the range from 400 to 599.
-----------------------------------------------------------------------------"""
class NoSuchNickError(Command):
    @staticmethod
    def token():
        return '401'

class NoSuchServerError(Command):
    @staticmethod
    def token():
        return '402'

class NoSuchChannelError(Command):
    @staticmethod
    def token():
        return '403'

class CannotSendToChannelError(Command):
    @staticmethod
    def token():
        return '404'

class TooManyChannelsError(Command):
    @staticmethod
    def token():
        return '405'

class TooManyTargetsError(Command):
    @staticmethod
    def token():
        return '407'

class NoOriginError(Command):
    @staticmethod
    def token():
        return '409'

class NoRecipientError(Command):
    @staticmethod
    def token():
        return '411'

class NoTextToSendError(Command):
    @staticmethod
    def token():
        return '412'

class NoToplevelError(Command):
    @staticmethod
    def token():
        return '413'

class WildTopLevelError(Command):
    @staticmethod
    def token():
        return '414'

class NoMotdError(Command):
    @staticmethod
    def token():
        return '422'
    
    def _receive(self, event):
        self.client.post_connect()

class NoNicknameGivenError(Command):
    @staticmethod
    def token():
        return '431'

class ErroneusNicknameError(Command):
    @staticmethod
    def token():
        return '432'

class NicknameInUseError(Command):
    @staticmethod
    def token():
        return '433'

class NickCollisionError(Command):
    @staticmethod
    def token():
        return '436'

class UnavailableResourceError(Command):
    @staticmethod
    def token():
        return '437'

class UserNotInChannelError(Command):
    @staticmethod
    def token():
        return '441'

class NotOnChannelError(Command):
    @staticmethod
    def token():
        return '442'

class UserOnChannelError(Command):
    @staticmethod
    def token():
        return '443'

class NeedMoreParamsError(Command):
    @staticmethod
    def token():
        return '461'

class AlreadyRegisteredError(Command):
    @staticmethod
    def token():
        return '462'

class KeySetError(Command):
    @staticmethod
    def token():
        return '467'

class ChannelIsFullError(Command):
    @staticmethod
    def token():
        return '471'

class UnknownModeError(Command):
    @staticmethod
    def token():
        return '472'

class InviteOnlyChannelError(Command):
    @staticmethod
    def token():
        return '473'

class BannedFromChannelError(Command):
    @staticmethod
    def token():
        return '474'

class BadChannelKeyError(Command):
    @staticmethod
    def token():
        return '475'
    
class BadChannelMaskError(Command):
    @staticmethod
    def token():
        return '476'

class NoChannelModesError(Command):
    @staticmethod
    def token():
        return '477'

class ChanOpPrivilegesNeededError(Command):
    @staticmethod
    def token():
        return '482'

class RestrictedError(Command):
    @staticmethod
    def token():
        return '484'

class UsersDontMachtError(Command):
    @staticmethod
    def token():
        return '502'
