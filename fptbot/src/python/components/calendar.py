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

@since Mar 12, 2011
@author Mario Steinhoff
"""

__version__ = '$Rev$'

import random
import datetime

from core.config import Config
from core.component import Component, ComponentError
from objects.calendar import Calendar, Event

# ------------------------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------------------------
class CalendarComponentError(ComponentError): pass
class InvalidEventId(CalendarComponentError): pass

# ------------------------------------------------------------------------------
# Business Logic
# ------------------------------------------------------------------------------
class CalendarComponent(Component):
    def __init__(self, bot):
        self.bot = bot
        
        self.bot.register_config(CalenderComponentConfig)
        
        self.config = self.bot.get_config('components.calendar')
        self.logger = self.bot.get_logger('components.calendar')
        
        self.events = {
            232: Event(id=232, start=datetime.date(2011, 4, 29), end=datetime.date(2011, 4, 29), title='test1', location='phark'),
            238: Event(id=238, start=datetime.date(2011, 4, 30), end=datetime.date(2011, 4, 30), title='test2', location='phark'),
            231: Event(id=231, start=datetime.date(2011, 4, 27), end=datetime.date(2011, 4, 27), title='test3', location='phark')
        }
    
    def find_calendars(self):
        return [Calendar(id=1, name='test', type=Calendar.MANUAL)]
    
    def find_event_by_id(self, id):
        if id == None:
            return None
        
        try:
            return self.events[id]
        except KeyError:
            return None
    
    def find_events_by_date(self, date):
        result = []
        
        if date != None:
            for event in self.events.values():
                if event.start <= date <= event.end:
                    result.append(event)
        
        return result
    
    def insert_event(self, event):
        if event == None:
            return None
        
        event.id = random.randint(1, 10000)
        
        self.events[event.id] = event
        
        return event
        
    def update_event(self, event):
        if event == None:
            return None
        
        self.events[event.id] = event
        
        return event
        
    def delete_event(self, eventId):
        if eventId == None:
            return
        
        try:
            del(self.events[eventId])
        except KeyError:
            raise InvalidEventId
        
# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------
class CalenderComponentConfig(Config):
    identifier = 'components.calendar'
        
    def valid_keys(self):
        return [
            'gdata-username',
            'gdata-password'
            'gdata-token',
        ]
    
    def default_values(self):
        return {
            'gdata-username' : '',
            'gdata-password' : '',
            'gdata-token'    : ''
        }

