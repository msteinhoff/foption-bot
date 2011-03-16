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

@since Jan 06, 2011
@author Mario Steinhoff
"""

__version__ = '$Rev$'

from logging         import basicConfig, getLogger, DEBUG
from multiprocessing import Process

from core.constants          import DB_BOT
from core.exceptions         import ConfigRegisteredError, InteractionRegisteredError
from core.config             import Config
from core.persistence        import Persistence
from interaction.interaction import Interaction
from interaction.irc.client  import Client

class Bot(object):
    """
    Provide general functionality and start all subsystems.
    """
    
    def __init__(self):
        """
        Initialize the bot.
        """
        
        basicConfig(level=DEBUG)
        
        self._persistence = Persistence(DB_BOT)
        
        self._config = {}
        self._interaction = {}
        self._processes = {}
        
        self.register_config(BotConfig)
        self.register_interaction('irc', Client)
        
        
    def get_persistence(self):
        """
        Return the persistence instance.
        """
        
        return self._persistence
    
    def get_logger(self, name=None):
        """
        Return a logger instance.
        
        @param name: The intended name. If no name is given, a default
        of 'core.bot' is used.
        """
        
        if name == None:
            name = 'core.bot'
            
        return getLogger(name)
    
    def register_interaction(self, name, clazz):
        if name in self._interaction:
            raise InteractionRegisteredError
        
        self._interaction[name] = clazz(self)
        
    def register_config(self, clazz):
        if clazz.name in self._config:
            raise ConfigRegisteredError
        
        self._config[clazz.identifier] = clazz(self)
        
    def get_config(self, identifier):
        return self._config[identifier]
    
    def get_configs(self):
        return self._config
    
    def run(self):
        """
        Start the system.
        
        Initialize all interaction components in their own thread
        and call their start() method.
        """
        
        self.getLogger().info('starting the system')
        
        for name, object in self._interaction.items():
            #self._processes[name] = Process(target=Interaction.startInteraction, args=(self, object))
            #self._processes[name].start()
            
            self._processes[name] = object(self)
            self._processes[name].start()
        
        self.getLogger().info('startup completed')
        
        

class BotConfig(Config):
    identifier = 'core.bot'
        
    def valid_keys(self):
        return []
    
    def default_values(self):
        return {}
