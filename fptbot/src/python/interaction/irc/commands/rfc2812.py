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

@since Jan 28, 2011
@author msteinhoff
"""

from interaction.irc.message import Event
from interaction.irc.command import Command

def register_with_client(client):
    handlers = [
        Nick, User, Mode, Quit,
        Join, Part, Topic, Names, Invite, Kick,
        Privmsg, Notice,
        Motd, Who, Whois,
        Ping, Pong,
        ReplyWelcome, ReplyYourHost, ReplyCreated, ReplyMyInfo, ReplyBounce,
        ReplyMotdStart, ReplyMotd, ReplyMotdEnd
    ]

    [client.register_command(handler) for handler in handlers]

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

class Nick(Command):
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
        # self._client.me.source.nickname = event
        # if user==self, change identity
        # change user
        pass
    
    def _send(self, nickname):
        self._client.send_irc(Event(None, self.token(), [nickname]))

class User(Command):
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
        self._client.send_irc(Event(None, self.token(), [ident, '0', '*', '{0}'.format(realname)]))


class Mode(Command):
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

class Quit(Command):
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
        parameter = []
        
        if message is not None:
            parameter.append(message)
        
        self._client.send_irc(Event(None, self.token(), parameter))


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

class Join(Command):
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
    
    def _receive(self, event):
        # add user to client channel list
        # if user==self, add channel to channel list
        pass
    
    def _send(self, channels, keys=None):
        if channels is None:
            parameter = ["0"]
        
        else:
            parameter = [','.join(channels)]
            
            if keys is not None:
                parameter.append(','.join(keys))
        
        self._client.send_irc(Event(None, self.token(), parameter))

class Part(Command):
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
    
    def _receive(self, event):
        # remove user from client channel list
        # if user==self, remove channel from channel list
        pass
    
    def _send(self, channel, message=None):
        parameter = [channel]
        
        if message is not None:
            parameter.append(message)
        
        self._client.send_irc(Event(None, self.token(), parameter))

"""
Because user mode message and channel mode are using the same command,
user mode and channel mode logic are implemented in the same class at 
the user section. 
"""

class Topic(Command):
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
    
    def _receive(self, event):
        # change channel topic
        pass
    
    def _send(self, topic):
        self._client.send_irc(Event(None, self.token(), [topic]))

class Names(Command):
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
    
    def _receive(self, event):
        # update user list
        pass
    
    def _send(self, channels):
        self._client.send_irc(Event(None, self.token(), [','.join(channels)]))

class Invite(Command):
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
    
    def _receive(self, event):
        # notify someone
        # on autoinvite, join channel
        pass
    
    def _send(self, nickname, channel):
        self._client.send_irc(Event(None, self.token(), [nickname, channel]))

class Kick(Command):
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
    
    def _receive(self, event):
        # remove user from channel list
        # if user==self, notify someone
        # if user==self, on autorejoin join channel again
        pass
    
    def _send(self, channels, users, message=None):
        parameter = [','.join(channels), ','.join(users)]
        
        if message is not None:
            parameter.append(message)
        
        self._client.send_irc(Event(None, self.token(), parameter))


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

class Privmsg(Command):
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
        if event.parameter[0].startswith('#') and event.parameter[1] == 'fotzenscheisse':
            self._client.send_command(Quit)
    
    def _send(self, target, text):
        self._client.send_irc(Event(None, self.token(), [target, text]))

class Notice(Command):
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
        self._client.send_irc(Event(None, self.token(), [target, text]))


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
class Motd(Command):
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
        
        self._client.send_irc(Event(None, self.token(), parameter))



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
class Who(Command):
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
        
        self._client.send_irc(Event(None, self.token(), parameter))


class Whois(Command):
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
    
    def _send(self, user):
        parameter = []
        
        if user.server is not None:
            parameter.append(user.server)
            
        parameter.append(user)
        
        self._client.send_irc(Event(None, self.token(), parameter))



"""
----------------------------------------------------------------------------
Section: 3.7 Miscellaneous messages
----------------------------------------------------------------------------
3.7.1  Kill message ......................................  35    - not needed
3.7.2  Ping message ......................................  36    - needed
3.7.3  Pong message ......................................  37    - needed
3.7.4  Error .............................................  37    - not needed
-------------------------------------------------------------------------"""
class Ping(Command):
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
            self._client.send_command(Pong, event.parameter[0])
        
        if len(event.parameter) == 2:
            self._client.send_command(Pong, event.parameter[0], event.parameter[1])

class Pong(Command):
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
        
        self._client.send_irc(Event(None, self.token(), parameter))


"""-----------------------------------------------------------------------------
Define IRC replies.
See below for descriptions from the RFC.
-----------------------------------------------------------------------------"""

"""-----------------------------------------------------------------------------
Numerics in the range from 001 to 099 are used for client-server
connections only and should never travel between servers.
-----------------------------------------------------------------------------"""
class ReplyWelcome(Command):
    @staticmethod
    def token():
        return '001'
    
    def _receive(self, event):
        pass

class ReplyYourHost(Command):
    @staticmethod
    def token():
        return '002'
    
    def _receive(self, event):
        pass

class ReplyCreated(Command):
    @staticmethod
    def token():
        return '003'
    
    def _receive(self, event):
        pass

class ReplyMyInfo(Command):
    @staticmethod
    def token():
        return '004'
    
    def _receive(self, event):
        pass
    
class ReplyBounce(Command):
    @staticmethod
    def token():
        return '005'
    
    def _receive(self, event):
        pass

"""-----------------------------------------------------------------------------
Replies generated in the response to commands are found in the
range from 200 to 399.
-----------------------------------------------------------------------------"""
RPL_TRACELINK         = "200"
RPL_TRACECONNECTING   = "201"
RPL_TRACEHANDSHAKE    = "202"
RPL_TRACEUNKNOWN      = "203"
RPL_TRACEOPERATOR     = "204"
RPL_TRACEUSER         = "205"
RPL_TRACESERVER       = "206"
RPL_TRACESERVICE      = "207"
RPL_TRACENEWTYPE      = "208"
RPL_TRACECLASS        = "209"
RPL_TRACERECONNECT    = "210"
RPL_TRACELOG          = "261"
RPL_TRACEEND          = "262"
RPL_STATSLINKINFO     = "211"
RPL_STATSCOMMANDS     = "212"
RPL_ENDOFSTATS        = "219"
RPL_STATSUPTIME       = "242"
RPL_STATSOLINE        = "243"
RPL_UMODEIS           = "221"
RPL_SERVLIST          = "234"
RPL_SERVLISTEND       = "235"
RPL_LUSERCLIENT       = "251"
RPL_LUSEROP           = "252"
RPL_LUSERUNKNOWN      = "253"
RPL_LUSERCHANNELS     = "254"
RPL_LUSERME           = "255"
RPL_ADMINME           = "256"
RPL_ADMINLOC1         = "257"
RPL_ADMINLOC2         = "258"
RPL_ADMINEMAIL        = "259"
RPL_TRYAGAIN          = "263"
RPL_USERHOST          = "302"
RPL_ISON              = "303"
RPL_AWAY              = "301"
RPL_UNAWAY            = "305"
RPL_NOWAWAY           = "306"
RPL_WHOISUSER         = "311"
RPL_WHOISSERVER       = "312"
RPL_WHOISOPERATOR     = "313"
RPL_WHOISIDLE         = "317"
RPL_ENDOFWHOIS        = "318"
RPL_WHOISCHANNELS     = "319"
RPL_WHOWASUSER        = "314"
RPL_ENDOFWHOWAS       = "369"
RPL_LISTSTART         = "321"
RPL_LIST              = "322"
RPL_LISTEND           = "323"
RPL_UNIQOPIS          = "325"
RPL_CHANNELMODEIS     = "324"
RPL_NOTOPIC           = "331"
RPL_TOPIC             = "332"
RPL_INVITING          = "341"
RPL_SUMMONING         = "342"
RPL_INVITELIST        = "346"
RPL_ENDOFINVITELIST   = "347"
RPL_EXCEPTLIST        = "348"
RPL_ENDOFEXCEPTLIST   = "349"
RPL_VERSION           = "351"
RPL_WHOREPLY          = "352"
RPL_ENDOFWHO          = "315"
RPL_NAMREPLY          = "353"
RPL_ENDOFNAMES        = "366"
RPL_LINKS             = "364"
RPL_ENDOFLINKS        = "365"
RPL_BANLIST           = "367"
RPL_ENDOFBANLIST      = "368"
RPL_INFO              = "371"
RPL_ENDOFINFO         = "374"

class ReplyMotdStart(Command):
    @staticmethod
    def token():
        return '375'
    
    def _receive(self, event):
        pass

class ReplyMotd(Command):
    @staticmethod
    def token():
        return '372'
    
    def _receive(self, event):
        pass

class ReplyMotdEnd(Command):
    @staticmethod
    def token():
        return '376'
    
    def _receive(self, event):
        self._client.post_connect()

RPL_YOUREOPER         = "381"
RPL_REHASHING         = "382"
RPL_YOURESERVICE      = "383"
RPL_TIME              = "391"
RPL_USERSSTART        = "392"
RPL_USERS             = "393"
RPL_ENDOFUSERS        = "394"
RPL_NOUSERS           = "395"

"""-----------------------------------------------------------------------------
Error replies are found in the range from 400 to 599.
-----------------------------------------------------------------------------"""
ERR_NOSUCHNICK        = "401"
ERR_NOSUCHSERVER      = "402"
ERR_NOSUCHCHANNEL     = "403"
ERR_CANNOTSENDTOCHAN  = "404"
ERR_TOOMANYCHANNELS   = "405"
ERR_WASNOSUCHNICK     = "406"
ERR_TOOMANYTARGETS    = "407"
ERR_NOSUCHSERVICE     = "408"
ERR_NOORIGIN          = "409"
ERR_NORECIPIENT       = "411"
ERR_NOTEXTTOSEND      = "412"
ERR_NOTOPLEVEL        = "413"
ERR_WILDTOPLEVEL      = "414"
ERR_BADMASK           = "415"
ERR_UNKNOWNCOMMAND    = "421"
ERR_NOMOTD            = "422"
ERR_NOADMININFO       = "423"
ERR_FILEERROR         = "424"
ERR_NONICKNAMEGIVEN   = "431"
ERR_ERRONEUSNICKNAME  = "432"
ERR_NICKNAMEINUSE     = "433"
ERR_NICKCOLLISION     = "436"
ERR_UNAVAILRESOURCE   = "437"
ERR_USERNOTINCHANNEL  = "441"
ERR_NOTONCHANNEL      = "442"
ERR_USERONCHANNEL     = "443"
ERR_NOLOGIN           = "444"
ERR_SUMMONDISABLED    = "445"
ERR_USERSDISABLED     = "446"
ERR_NOTREGISTERED     = "451"
ERR_NEEDMOREPARAMS    = "461"
ERR_ALREADYREGISTRED  = "462"
ERR_NOPERMFORHOST     = "463"
ERR_PASSWDMISMATCH    = "464"
ERR_YOUREBANNEDCREEP  = "465"
ERR_YOUWILLBEBANNED   = "466"
ERR_KEYSET            = "467"
ERR_CHANNELISFULL     = "471"
ERR_UNKNOWNMODE       = "472"
ERR_INVITEONLYCHAN    = "473"
ERR_BANNEDFROMCHAN    = "474"
ERR_BADCHANNELKEY     = "475"
ERR_BADCHANMASK       = "476"
ERR_NOCHANMODES       = "477"
ERR_BANLISTFULL       = "478"
ERR_NOPRIVILEGES      = "481"
ERR_CHANOPRIVSNEEDED  = "482"
ERR_CANTKILLSERVER    = "483"
ERR_RESTRICTED        = "484"
ERR_UNIQOPPRIVSNEEDED = "485"
ERR_NOOPERHOST        = "491"
ERR_UMODEUNKNOWNFLAG  = "501"
ERR_USERSDONTMATCH    = "502"

