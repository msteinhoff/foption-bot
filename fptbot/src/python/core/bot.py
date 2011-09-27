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
import collections

from core import runlevel
from core.timer import timer_map
from core.config import Config

# ------------------------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------------------------
class BotError(Exception): pass
class ConfigRegisteredError(BotError): pass
class TimerRegisteredError(BotError): pass
class SubsystemRegisteredError(BotError): pass

# ------------------------------------------------------------------------------
# Business Logic
# ------------------------------------------------------------------------------
class Bot(object):
    """
    Provide general functionality and start all subsystems.
    """
    
    def __init__(self, level=logging.DEBUG):
        """
        Initialize the bot.
        """
        
        logging.basicConfig(level=level)
        
        self.logger = self.get_logger()
        
        self.__runlevel = runlevel.HALT
        self.__runlevel_map = collections.defaultdict(list)
        
        self._config = {}
        self._timer = {}
        self._subsystems = {}
        self._processes = {}
        
        self.register_config(BotConfig)
        self.apply_logger_config()
        
        self.register_subsystem('local-persistence', 'core.persistence.SqlAlchemyPersistence', connect_string='config:core.bot.database-connectstring')
        self.register_subsystem('google-api-service', 'core.persistence.GoogleApiService')
        self.register_subsystem('principal-component', 'components.principal.PrincipalComponent')
        self.register_subsystem('calendar-component', 'components.calendar.CalendarComponent')
        self.register_subsystem('facts-component', 'components.facts.FactsComponent')
        self.register_subsystem('irc-client', 'interaction.irc.client.Client')
        
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
        
        if identifier is None:
            identifier = 'core.bot'
            
        return logging.getLogger(identifier)
    
    def apply_logger_config(self):
        pass
    
    #---------------------------------------------------------------------------
    # configuration
    #---------------------------------------------------------------------------
    def register_config(self, clazz):
        """
        @param clazz: 
        """
        
        if clazz.identifier in self._config:
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
    
    #---------------------------------------------------------------------------
    # timer
    #---------------------------------------------------------------------------
    def register_timer(self, identifier, type, interval, callback):
        """
        Register a new timer with the bot.
        
        @param identifier: The identifier of the timer.
        @param type: The requested type.
        @param interval: The type-specific interval.
        @param callback: The callback to execute when the timer is fired.
        """
        
        if identifier in self._timer:
            raise TimerRegisteredError(identifier)
        
        self._timer[identifier] = timer_map[type](interval, callback)
        
    def get_timer(self, identifier):
        """
        @param identifier: The identifier of the timer.
        
        @Return The timer instance.
        """
        
        return self._timer[identifier]
    
    #---------------------------------------------------------------------------
    # subsystems
    #---------------------------------------------------------------------------
    def register_subsystem(self, identifier, classname, **kwargs):
        """
        Register a new subsystem.
        
        @param identifier: The identifier for the instanciated subsystem.
        @param classname: The fully qualified classname of the subsystem.
        @param **kwargs: Any additional constructor arguments.
        """
    
        if identifier in self._subsystems:
            raise SubsystemRegisteredError
        
        clazz = self.get_object(classname)
        
        self._subsystems[identifier] = clazz(self, **kwargs)
        
        # using defaultdict here
        self.__runlevel_map[clazz.RUNLEVEL.level].append(identifier)
    
    def get_subsystem(self, identifier):
        """
        Return the subsystem instance.
        
        @identifier: The identifier of the subsystem.
        
        @return The subsystem instance.
        """
        
        return self._subsystems[identifier]
    
    #---------------------------------------------------------------------------
    # bootstrapping
    #---------------------------------------------------------------------------
    def init(self, requested):
        """
        Execute a runlevel switch.
        
        @param requested: The requested runlevel.
        """
        
        if self.__runlevel == requested:
            return
        
        direction = runlevel.calculate_direction(self.__runlevel, requested)
        distance = runlevel.calculate_distance(self.__runlevel, requested)
        
        self.logger.info('switching runlevel: %s to %s', self.__runlevel, requested)
        
        for next in distance:#
            self.__runlevel = next
            
            if direction == runlevel.DIRECTION_UP:
                self.logger.info('entering runlevel %s', next)
                self._start_subsystems(next)
                
            if direction == runlevel.DIRECTION_DOWN:
                self.logger.info('leaving runlevel %s', next)
                self._stop_subsystems(next)
            
        self.__runlevel = requested
        
        self.logger.info('runlevel switched: %s', self.__runlevel)
        
        # temporary solution because the system currently uses only one thread.
        #self.init(runlevel.HALT)
    
    def get_runlevel(self):
        """
        Return the current runlevel of the system.
        """
        
        return self.__runlevel
    
    def _start_subsystems(self, requested):
        """
        Start all subsystems for the requested runlevel.
        
        TODO multithreaded or singlethreaded, event-based architecture
        for name, object in self._interaction.items():
            #self._processes[name] = multiprocessing.Process(target=Interaction.startInteraction, args=(self, object))
            #self._processes[name].start()
            
            self.logger.info('starting process %s', name)
            self._processes[name] = object
            self._processes[name].start()

        @param requested: The requested runlevel.
        """
        
        for identifier in self.__runlevel_map[requested]:
            if self._subsystems[identifier].get_state() != runlevel.STATE_HALTED:
                self.logger.info('subsystem %s: skipped (not halted)', identifier)
                continue
            
            try:
                self.logger.info('subsystem %s: starting', identifier)
                self._subsystems[identifier].start()
                self.logger.info('subsystem %s: started', identifier)
            except:
                self.logger.exception('subsystem %s: start failed', identifier)

        
    def _stop_subsystems(self, requested):
        """
        Stop all subsystems for the requested runlevel.
        
        @param requested: The requested runlevel.
        """
        
        for identifier in self.__runlevel_map[requested]:
            if self._subsystems[identifier].get_state() != runlevel.STATE_RUNNING:
                self.logger.info('subsystem %s: skipped (not running)', identifier)
                continue
            
            try:
                self.logger.info('subsystem %s: starting', identifier)
                self._subsystems[identifier].stop()
                self.logger.info('subsystem %s: started', identifier)
            except:
                self.logger.exception('subsystem %s: start failed', identifier)

    
class BotConfig(Config):
    identifier = 'core.bot'
        
    def valid_keys(self):
        return [
            'logging-directory',
            'database-file',
            'database-connectstring',
        ]
    
    def default_values(self):
        return {
            'logging-directory'      : '',
            'database-file'          : '',
            'database-connectstring' : ''
        }
