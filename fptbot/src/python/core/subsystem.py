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

@since Sep 22, 2011
@author Mario Steinhoff
"""

__version__ = '$Rev$'

from core import runlevel
from core.bot import BotError

# ------------------------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------------------------
class SubsystemError(BotError): pass
class SubsystemStateError(SubsystemError): pass

# ------------------------------------------------------------------------------
# Business Logic
# ------------------------------------------------------------------------------
class Subsystem(object):
    """
    Define a management interface for arbitrary subsystems.
    """
    
    def __init__(self, bot):
        """
        Initialize the subsystem with a reference to the bot instance.
        """
        
        self.__state = runlevel.STATE_HALTED
        
        self.bot = bot
    
    def start(self):
        """
        Start the subsystem and any background services.
        """
        
        if self.__state != runlevel.STATE_HALTED:
            raise SubsystemStateError('can not start subsystem %s: subsystem is not halted.'.format(self.__class__.__name__))
        
        try:
            self._start()
        
        except Exception:
            logger = self.bot.get_logger()
            logger.exception('Failed to start subsystem %s', self.__class__.__name__)
    
    def stop(self):
        """
        Stop the subsystem and any background services.
        """
        
        if self.__state != runlevel.STATE_RUNNING:
            raise SubsystemStateError('can not stop subsystem %s: subsystem is not running.'.format(self.__class__.__name__))
        
        try:
            self._stop()
        
        except Exception:
            logger = self.bot.get_logger()
            logger.exception('Failed to stop subsystem %s', self.__class__.__name__)
    
    def _starting(self):
        """
        Subsystem-internal method to indicate that the system is starting.
        """
        
        self.__state = runlevel.STATE_STARTING
    
    def _running(self):
        """
        Subsystem-internal method to indicate that the system is running.
        """
        
        self.__state = runlevel.STATE_RUNNING
    
    def _stopping(self):
        """
        Subsystem-internal method to indicate that the system is stopping.
        """
        
        self.__state = runlevel.STATE_STOPPING
    
    def _halted(self):
        """
        Subsystem-internal method to indicate that the system is stopped.
        """
        self.__state = runlevel.STATE_HALTED
    
    def get_state(self):
        """
        Returns the current running state of the subsystem.
        
        @see: core.runlevel for details on available running states.
        """
        
        return self.__state
    
