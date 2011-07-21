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
# Data management
# ------------------------------------------------------------------------------
class DataStore():
    """
    The calendar data store.
    
    The data store manages all backend systems and data synchronization
    between the primary and secondary backends.
    """

    def set_primary_backend(self, backend):
        """
        Set a backend object as the primary backend.
        
        @param backend: The backend instance.
        
        @return Nothing
        """
        
        raise NotImplementedError
    
    def notify_primary_backend(self, source, operation, type, id):
        """
        Notify the primary backend about a data change.
        
        When a change at one of the the secondary backends occurs, the
        primay backend is notified about the change.  It will first update
        itself with the changed data and then propagate the changed data to
        all other secondary backends except the initiating one.
        
        A change can be a insert, update or delete operation.
        
        @param source: The backend that initiated the change.
        @param operation: The change mode, can be insert, update or delete.
        @param type: The data type of the changed object.
        @param id: The id of the changed object.
        
        @return Nothing
        """
        
        raise NotImplementedError
    
    def register_secondary_backend(self, backend):
        """
        Register a backend object as a secondary backend.
        
        @param backend: The backend instance.
        
        @return Nothing
        """
        
        raise NotImplementedError
    
    def notify_secondary_backends(self, operation, type, id):
        """
        Notify all secondary backends about a data change.
        
        When a change at the primary backend occurs, the secondary backends
        are notified about the change. They can either ignore the change
        or fetch the changed object using the provided data type and id.
        
        A change can be a insert, update or delete operation.
        
        @param operation: The change mode, can be insert, update or delete.
        @param type: The data type of the changed object.
        @param id: The id of the changed object.
        
        @return Nothing
        """
        
        raise NotImplementedError
    
    def find_objects(self, object):
        """
        Find objects with the given search criteria in the primary backend.
        Wildcards can be used.
        
        TODO: advanced find using sql queries.
        
        @param object: The object with search criteria.
        
        @return A list with matches. List will be empty if nothing was found.
        """
        
        raise NotImplementedError
    
    def create_object(self, object):
        """
        Create a new object in the registered primary/secondary backends.
        
        @param object: The object to create.
        
        @return The given object with a populated id attribute.
        """
        
        raise NotImplementedError
    
    def update_object(self, object):
        """
        Update an existing object in the registered primary/secondary backends.
        
        @param object: The object to update.
        """
        
        raise NotImplementedError
    
    def remove_object(self, type, id):
        """
        Delete an existing object in the registered primary/secondary backends.
        
        @param type: The data type of the object to delete.
        @param id: The id of the object to delete.
        """
        
        raise NotImplementedError

class Backend():
    """
    A generic backend.
    """
    def __init__(self):
        """
        Instantiate the backend.
        """
        
        self.datastore = None
        
    def set_datastore(self, datastore):
        """
        Set the current datastore to work with.
        
        @param datastore: The datastore instance.
        """
        
        self.datastore = datastore
    
    def handle_incoming_change(self, source, operation, type, id):
        """
        Respond to a data change.
        
        @param source: The backend where the change occured.
        @param operation: The change mode, can be insert, update or delete.
        @param type: The data type of the changed object.
        @param id: The id of the changed object.
        
        @return Nothing
        """
        
        raise NotImplementedError
    
    def create_object(self, object):
        """
        Create a new data object.
        
        @param object: The object to create.
        
        @return The given object with a populated id attribute.
        """
        
        raise NotImplementedError
    
    def update_object(self, object):
        """
        Update an existing object.
        
        @param object: The object to update.
        """
        
        raise NotImplementedError
    
    def remove_object(self, type, id):
        """
        Delete an existing object.
        
        @param type: The data type of the object to delete.
        @param id: The id of the object to delete.
        """
        
        raise NotImplementedError



class SqliteBackend(Backend):
    def set_cursor(self):
        pass

class GoogleBackend(Backend):
    pass

class FacebookBackend(Backend):
    pass

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
