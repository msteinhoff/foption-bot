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
from core.config             import Config
from core.persistence        import Persistence
from interaction.interaction import Interaction

"""-----------------------------------------------------------------------------
Exceptions
-----------------------------------------------------------------------------"""
class BotError(Exception): pass
class ConfigRegisteredError(BotError): pass
class InteractionRegisteredError(BotError): pass
class ComponentRegisteredError(BotError): pass

"""-----------------------------------------------------------------------------
Business Logic
-----------------------------------------------------------------------------"""
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
        self._components = {}
        self._processes = {}
        
        self.register_config(BotConfig)
        self.register_component('calendar', 'components.calendar.CalendarComponent')
        self.register_interaction('irc', 'interaction.irc.client.Client')
    
    def get_object( self, name ):
        """
        Returns a reference to the given object.
        
        The containing module is imported and a reference to the
        given object is returned.
        
        Taken from http://stackoverflow.com/questions/452969/does-python-have-
        an-equivalent-to-java-class-forname
        
        @param classname: The fully qualified classname to load
        
        @return: A reference to the class object
        """
        
        module_name, _, object_name = name.rpartition('.')
        
        m = __import__(module_name, globals(), locals(), [object_name], -1)
        
        obj = getattr(m, object_name)
        
        return obj
    
    """-------------------------------------------------------------------------
    Logging
    -------------------------------------------------------------------------"""
    def get_logger(self, identifier=None):
        """
        Return a logger instance.
        
        @param identifier: The intended name. If no name is given, a default
        of 'core.bot' is used.
        """
        
        if identifier == None:
            identifier = 'core.bot'
            
        return getLogger(identifier)
    
    """-------------------------------------------------------------------------
    Persistence
    -------------------------------------------------------------------------"""
    def get_persistence(self):
        """
        Return the persistence instance.
        """
        
        return self._persistence
    
    """-------------------------------------------------------------------------
    Configuration
    -------------------------------------------------------------------------"""
    def register_config(self, clazz):
        """
        @param clazz: 
        """
        
        if clazz.name in self._config:
            raise ConfigRegisteredError
        
        self._config[clazz.identifier] = clazz(self)
        
    def get_config(self, identifier):
        """
        @param identifier: 
        """
        
        return self._config[identifier]
    
    def get_configs(self):
        """
        """
        
        return self._config
    
    """-------------------------------------------------------------------------
    Interaction
    -------------------------------------------------------------------------"""
    def register_interaction(self, identifier, classname):
        """
        @param identifier: 
        @param clazz: 
        """
    
        if identifier in self._interaction:
            raise InteractionRegisteredError
        
        clazz = self.get_object(classname)
        
        self._interaction[identifier] = clazz(self)
        
    """-------------------------------------------------------------------------
    Components
    -------------------------------------------------------------------------"""
    def register_component(self, identifier, classname):
        """
        @param identifier: 
        @param clazz: 
        """
        
        if identifier in self._components:
            raise ComponentRegisteredError
        
        clazz = self.get_object(classname)
        
        self._components[identifier] = clazz(self)
        
    def get_component(self, identifier):
        """
        @param identifier: 
        """
        
        return self._components[identifier]
    
    """-------------------------------------------------------------------------
    System
    -------------------------------------------------------------------------"""
    def run(self):
        """
        Start the system.
        
        Initialize all interaction components in their own thread
        and call their start() method.
        """
        
        self.get_logger().info('starting the system')
        
        for name, object in self._interaction.items():
            #self._processes[name] = Process(target=Interaction.startInteraction, args=(self, object))
            #self._processes[name].start()
            
            self._processes[name] = object
            self._processes[name].start()
        
        self.get_logger().info('startup completed')

class BotConfig(Config):
    identifier = 'core.bot'
        
    def valid_keys(self):
        return []
    
    def default_values(self):
        return {}
