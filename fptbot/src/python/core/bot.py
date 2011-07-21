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

import logging
import multiprocessing

from core.timer import timer_map
from core.config import Config
from core.persistence import Persistence
from interaction.interaction import Interaction

# ------------------------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------------------------
class BotError(Exception): pass
class ConfigRegisteredError(BotError): pass
class InteractionRegisteredError(BotError): pass
class ComponentRegisteredError(BotError): pass
class TimerRegisteredError(BotError): pass

# ------------------------------------------------------------------------------
# Business Logic
# ------------------------------------------------------------------------------
class Bot(object):
    """
    Provide general functionality and start all subsystems.
    """
    
    def __init__(self):
        """
        Initialize the bot.
        """
        
        logging.basicConfig(level=logging.DEBUG)
        
        self.logger = self.get_logger()
        
        self._config = {}
        self.register_config(BotConfig)
        
        self._persistence = Persistence(self.get_config('core.bot').get('database-file'))
        self.register_persistence()
        
        self._components = {}
        self.register_component('principal', 'components.principal.PrincipalComponent')
        self.register_component('calendar', 'components.calendar.CalendarComponent')
        self.register_component('facts', 'components.facts.FactsComponent')
        
        self._interaction = {}
        self.register_interaction('irc', 'interaction.irc.client.Client')
        
        self._timer = {}
        
        self._processes = {}
    
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
    
    #---------------------------------------------------------------------------
    # logging
    #---------------------------------------------------------------------------
    def get_logger(self, identifier=None):
        """
        Return a logger instance.
        
        @param identifier: The intended name. If no name is given, a default
        of 'core.bot' is used.
        """
        
        if identifier == None:
            identifier = 'core.bot'
            
        return logging.getLogger(identifier)
    
    #---------------------------------------------------------------------------
    # persistence
    #---------------------------------------------------------------------------
    def get_persistence(self):
        """
        Return the persistence instance.
        """
        
        return self._persistence
    
    #---------------------------------------------------------------------------
    # configuration
    #---------------------------------------------------------------------------
    def register_config(self, clazz):
        """
        @param clazz: 
        """
        
        if clazz.identifier in self._config:
            raise ConfigRegisteredError
        
        self._config[clazz.identifier] = clazz()
        
    def get_config(self, identifier):
        """
        @param identifier: 
        """
        
        return self._config[identifier]
    
    def get_configs(self):
        """
        """
        
        return self._config
    
    #---------------------------------------------------------------------------
    # interaction
    #---------------------------------------------------------------------------
    def register_interaction(self, identifier, classname):
        """
        @param identifier: 
        @param clazz: 
        """
    
        if identifier in self._interaction:
            raise InteractionRegisteredError
        
        clazz = self.get_object(classname)
        
        self._interaction[identifier] = clazz(self)
        
    #---------------------------------------------------------------------------
    # components
    #---------------------------------------------------------------------------
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
    
    #---------------------------------------------------------------------------
    # timer
    #---------------------------------------------------------------------------
    def register_timer(self, identifier, type, interval, callback):
        if identifier in self._timer:
            raise TimerRegisteredError(identifier)
        
        self._timer[identifier] = timer_map[type](interval, callback)
        
    def get_timer(self, identifier):
        """
        @param identifier: 
        """
        
        return self._timer[identifier]
    
    #---------------------------------------------------------------------------
    # system
    #---------------------------------------------------------------------------
    def run(self):
        """
        Start the system.
        
        Initialize all interaction components in their own thread
        and call their start() method.
        """
        
        for name, component in self._components.items():
            self.logger.info('starting component %s', name)
            component.start()
        
        for name, object in self._interaction.items():
            #self._processes[name] = multiprocessing.Process(target=Interaction.startInteraction, args=(self, object))
            #self._processes[name].start()
            
            self.logger.info('starting process %s', name)
            self._processes[name] = object
            self._processes[name].start()
        
        # temporary solution because the system currently uses only one thread. 
        self.halt()
        
    def halt(self):
        """
        Shutdown the system.
        """
        
        for name, object in self._processes.items():
            self.logger.info('stopping process %s', name)
            object.stop()
        
        for name, component in self._components.items():
            self.logger.info('stopping component %s', name)
            component.stop()


class BotConfig(Config):
    identifier = 'core.bot'
        
    def valid_keys(self):
        return [
            'configuration-directory',
            'logging-directory',
            'database-file'
        ]
    
    def default_values(self):
        return {
            'logging-directory'      : '',
            'database-file'          : ''
        }
