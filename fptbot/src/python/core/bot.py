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

from multiprocessing import Process

from core.config            import Config
from core.logger            import Logger
from persistence.file       import File
from interaction.irc.client import Client

class BotConfig(Config):
    """
    the general bot configuration
    """
    
    def __init__(self, persistence):
        """
        initialize configuration structure
        """
        valid = {}
        defaults = {}
        
        Config.__init__("bot", persistence, valid, defaults);


class Bot(object):
    """
    The base class that manages all sub systems
    """
    
    def __init__(self):
        """
        initialize the system
        """
        self.persistence = File()
        
        self.config = BotConfig(self.persistence)
        self.logger = Logger() 
        
        self.interaction = {}
        self.interaction['irc'] = Client(user, server)

    def run(self):
        """
        start the system
        """
        
        logProcess = Process(target=Logger)
        logProcess.start()
        