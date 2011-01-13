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

@since 06.01.2010
@author Mario Steinhoff
"""

from string   import split, join
from socket   import AF_INET, SOCK_STREAM
from asyncore import loop
from asynchat import async_chat

from core.messages              import message
from core.config                import Config
from interaction.interaction    import Interaction
from interaction.irc.user       import Userlist, User

SPACE      = "\x20"
CRLF       = "\x0D\x0A"
MIRC_COLOR = "\x03"

class Client(Interaction, async_chat):
    """
    Provide a RFC 2812 compilant IRC client implementation using asyncore.
    """
    
    class ClientConfig(Config):
        def __init__(self, persistence):
            Config.__init__(self, "irc-client", persistence);
            
        def valid(self):
            return [
                "nickname",
                "anickname",
                "realname",
                "ident",
                "address",
                "port"
            ]
        
        def defaults(self):
            return {
                "nickname"  : "bot-test",
                "anickname" : "bot-test-",
                "realname"  : "bot",
                "ident"     : "bot",
                "address"   : "de.quakenet.org",
                "port"      : 6667
            }

    def __init__(self, bot):
        """
        Initialize the IRC client.
        
        @param bot: The bot instance that this client should use.
        """
        
        Interaction.__init__(self, bot)
        async_chat.__init__(self)
        
        self._logger = self._bot.getLogger("interaction.irc")
        self._config = self.ClientConfig(bot.getPersistence())
        self._userlist = Userlist()
        self._modules = {}
        
        self._isConnected = False
        
        self.set_terminator(CRLF)

    def register_module(self, name):
        """
        Load a module that extends the client's functionality.
        
        @param name: The name of the module that should be registered
        """
        
        moduleName = "modules.%s" % name
        
        module = __import__(moduleName, globals(), locals(), [], -1)
        
        clazz = getattr(module, module.moduleName)
        
        self._modules[name] = clazz()
        
    def get_module(self, name):
        """
        Return a given module instance.
        
        @param name: The name of the module that should be returned.
        @return The module instance, a subclass of Module.
        @raise KeyError if there is no such module 
        """
        
        return self._modules[name]
    
    """-------------------------------------------------------------------------
    Connection handling
    -------------------------------------------------------------------------"""
    def start(self):
        """
        Connect to the IRC server.
        """
        
        self._logger.info(message[20001], {
            'address' : self._config.get('address'),
            'port'    : self._config.get('port')
        })
        
        try:
            self.create_socket(AF_INET, SOCK_STREAM)
            self.connect((self._config.get('address'), self._config.get('port')))
            
            self._buffer = []
            
            loop()
        except:
            #TODO: check which exceptions are caught here
            self._logger.info.error(message[20002])

    def stop(self):
        """
        Disconnect from the IRC server.
        """
        
        self._logger.info(message[20003])
        self.close_when_done()

    """-------------------------------------------------------------------------
    Communication interface
    
    TODO: Create consistent API to send/compose and receive/parse IRC messages.
    -------------------------------------------------------------------------"""
    def receive_irc(self, data):
        """
        Handle all interaction when there is protocol data received.
        
        Strip IRC protocol control characters.
        
        @param data: The data which was received.
        """
        
        data = [line.strip(CRLF) for line in data]
        
        source, command, params = self.parse_message(data)
        
        self._logger.info("Received: <%s> %s: %s (Raw: %s)" % (source, command, params, data))
        
        if command == 'PING':
            self.send_irc(["PONG", params[0]])
            
        if command == '001':
            self.send_irc(["JOIN", "#botbot.test"])

    def send_irc(self, data):
        """
        Handle all interaction when there is protocol data to send.
        
        Add IRC protocol control characters.
        
        @param data: The data to send.
        """
        
        self._logger.info("Sent:     %s" % join(data))
        self.push("%s%s" % (join(data), CRLF))

    """-------------------------------------------------------------------------
    Message handling
    -------------------------------------------------------------------------"""
    def parse_message(self, message):
        """
        Parse an incoming IRC message.
        
        The message is parsed into the following components:
        - source, a string with the format e.g. nickname!ident@host, or None  
        - command, the IRC command or reply
        - params, all parameters, parsed according to RFC section 2.3.1
        
        Currently, the implementation is not a real parser, but works
        in most conditions.
        
        TODO: write a proper parser with full RFC support. 
        
        @param message: The raw message
        
        @return a tupel (source, command, params)
        """
        
        """---------------------------------------------------------------------
        Handle the source of the message, if existent
        ---------------------------------------------------------------------"""
        if message[0] == ':':
            source, message = split(message[1:], ' ', 1)
        else:
            source = None

        """---------------------------------------------------------------------
        Parse the message components
        
        The command and its parameters are separated by the follwing rules:
        
        - The command can be any string with at least 1 letter or a 3 digit number.
        - A command can only have 14 parameters.
        - Every parameter must start with a space.
        - After the space, there must be at least one character except NUL, CR, LF, space, or colon.
        - After the first character, there can be further characters or colons.
        - If the parameter itself contains a space, it has to be separated by a space and a colon, " :"
        [...]
        ---------------------------------------------------------------------"""
        try:
            message = split(message, ' :')
            
            command = message[0]
            params = message[1:]
        
        except ValueError:
            command = message
            params = ''
        
        return source, command, params

    """-------------------------------------------------------------------------
    Implementation of asyncore methods 
    -------------------------------------------------------------------------"""
    def handle_connect(self):
        """
        Implement IRC protocol for connecting and set internal state.
        """
        
        self.send_irc(["NICK", self._config.get('nickname')])
        self.send_irc(["USER", self._config.get('ident'), "0", "*", ":%s" % self._config.get('realname')])
        
        self._isConnected = True
    
    def handle_close(self):
        """
        Implement IRC protocol for disconnecting and set internal state.
        """
        
        self.send_irc(["QUIT", "i did it for the lulz mkay"])
        
        self._isConnected = False

    """-------------------------------------------------------------------------
    Implementation of asynchat methods 
    -------------------------------------------------------------------------"""
    def collect_incoming_data(self, data):
        """
        Add any received data to the internal buffer.
        """
        
        self._buffer.append(data)

    def found_terminator(self):
        """
        Send event when a command terminator was found.
        """
        
        data = self._buffer
        self._buffer = []
        
        self.receive_irc(data)
