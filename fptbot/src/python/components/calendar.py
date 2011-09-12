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

import datetime

import sqlalchemy
import gdata.calendar.data
import atom.data

from core.component import Component, ComponentError
from objects.calendar import Calendar, Event, Contact, EventBackendMapping,\
    ContactBackendMapping, CalendarBackendMapping

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
        
        self.logger = self.bot.get_logger('components.calendar')
        
        self.datastore = None
    
    # --------------------------------------------------------------------------
    # Lifecycle
    # --------------------------------------------------------------------------
    def start(self):
        self.datastore = DataStore()
        
        # Setup primary backend
        sqlite = SqlAlchemyBackend(self.bot.get_persistence('local'))
        self.datastore.set_primary_backend(sqlite)
        
        # Setup secondary backend
        google = GoogleBackend(self.bot.get_persistence('google'))
        self.datastore.register_secondary_backend(google)
        
    def stop(self):
        self.datastore = None
    
    # --------------------------------------------------------------------------
    # Component methods
    # --------------------------------------------------------------------------
    def find_calendars(self):
        query = self.datastore.get_query('all_calendars')
        
        return self.datastore.find_objects(query)
    
    def find_event_by_id(self, id):
        if id == None:
            return None
        
        query = self.datastore.get_query('event_by_id')
        query.id = id
        
        return self.datastore.find_objects(query)
    
    def find_events_by_date(self, date):
        if date == None:
            return None
        
        query = self.datastore.get_query('events_at_date')
        query.date = date
        
        return self.datastore.find_objects(query)
    
    def insert_object(self, event):
        if event == None:
            return None
        
        if event.id != None:
            raise ValueError('event.id must be None')
        
        return self.datastore.insert_object(event)
        
    def update_object(self, event):
        if event == None:
            return None
        
        if event.id != None:
            raise ValueError('event.id must be given')
        
        try:
            return self.datastore.update_object(event)
        except KeyError:
            raise InvalidEventId
        
    def delete_event(self, eventId):
        if eventId == None:
            return
        
        try:
            event = self.find_event_by_id(eventId)
            
            self.datastore.delete_object(event)
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
    
    OPERATION_INSERT = 0x01
    OPERATION_UPDATE = 0x02
    OPERATION_DELETE = 0x03
    
    def __init__(self):
        self.primary_backend = None
        self.secondary_backends = []
    
    def set_primary_backend(self, backend):
        """
        Set a backend object as the primary backend.
        
        @param backend: The backend instance.
        
        @return Nothing
        """
        
        self.primary_backend = backend
    
    def notify_primary_backend(self, source, operation, object):
        """
        Notify the primary backend about a data change.
        
        When a change at one of the the secondary backends occurs, the
        primay backend is notified about the change.  It will first update
        itself with the changed data and then propagate the changed data to
        all other secondary backends except the initiating one.
        
        A change can be a insert, update or delete operation.
        
        @param source: The backend instance that initiated the change.
        @param operation: The change mode, can be insert, update or delete.
        @param object: The changed object.
        
        @return Nothing
        """
        
        self.primary_backend.handle_incoming_change(self, source, operation, object)
    
    def register_secondary_backend(self, backend):
        """
        Register a backend object as a secondary backend.
        
        @param backend: The backend instance.
        
        @return Nothing
        """
        
        self.secondary_backends.append(backend)
    
    def notify_secondary_backends(self, source, operation, object):
        """
        Notify all secondary backends about a data change.
        
        When a change at the primary backend occurs, the secondary backends
        are notified about the change. They can either ignore the change
        or fetch the changed object using the provided data type and id.
        
        A change can be a insert, update or delete operation.
        
        @param source: The backend instance that initiated the change.
        @param operation: The change mode, can be insert, update or delete.
        @param object: The changed object.
        
        @return Nothing
        """
        
        for backend in self.secondary_backends:
            # ignore source
            if backend.__class__.__name__ == source:
                continue
            
            backend.handle_incoming_change(self, source, operation, object)
    
    def get_query(self, name):
        """"
        Return a new query object with the given name.
        A query object is used to query the backends for specific objects.
        
        @param name: The name of the query.
        
        @return A new DataStoreQuery instance.
        """
        
        query_object = DataStoreQuery(name)
        
        return query_object
    
    def create_mapping(self, object, backend, identity):
        """
        Create a mapping between an object in the primary backend and an
        identity in a given secondary backend.
        
        @param object: The object in the primary backend.
        @param backend: The secondary backend.
        @param identity: The backend-specific identity.
        """
        
        self.primary_backend.create_mapping(self, object, backend, identity)
    
    def find_objects(self, query_object):
        """
        Find objects in the primary backend using a query object.
        
        @param query_object: The query_object with search criteria.
        
        @return A list with matching objects. The List will be empty if
        nothing was found.
        """
        
        return self.primary_backend.find_objects(self, query_object)
    
    def insert_object(self, object):
        """
        insert a new object in the primary backend.
        
        @param object: The object to insert.
        
        @return The given object with a populated id attribute.
        """
        
        return self.primary_backend.insert_object(self, object)
    
    def update_object(self, object):
        """
        Update an existing object in the primary backend.
        
        @param object: The object to update.
        """
        
        return self.primary_backend.update_object(self, object)
    
    def delete_object(self, object):
        """
        Delete an existing object in the primary backend.
        
        @param object: The object to delete.
        """
        
        return self.primary_backend.delete_object(self, object)

class DataStoreQuery():
    """
    An abstract data store query.
    
    This object only contains the general name of the specific query.
    Arbitrary query parameters can be added at runtime. When the query is run
    against the backends, the name is used to identify the concrete query
    objects provided by the backends.
    """
    
    def __init__(self, name):
        """
        Instantiate a new query object.
        
        @param name: The query name.
        """
        
        self.__query_name = name
        
    def get_name(self):
        """
        Return the query name.
        
        @return The query name.
        """
        
        return self.__query_name
    
    def get_parameters(self):
        """
        Return a dictionary with query parameters.
        
        @return A dictionary with query parameters.
        """
        
        # TODO filter private attributes
        return self.__dict__

class Backend():
    """
    A generic backend.
    """
        
    def handle_incoming_change(self, context, source, operation, object):
        """
        Respond to a data change.
        
        @param context: The datastore context.
        @param source: The backend where the change occured.
        @param operation: The change mode, can be insert, update or delete.
        @param object: The changed object.
        
        @return Nothing
        """
        
        raise NotImplementedError
    
    def create_mapping(self, context, object, backend, identity):
        """
        Create a mapping between an object in the primary backend and an
        identity in a given secondary backend.
        
        @param context: The datastore context.
        @param object: The object in the primary backend.
        @param backend: The secondary backend.
        @param identity: The backend-specific identity.
        """
        
        raise NotImplementedError
    
    def find_objects(self, context, query_object):
        """
        Find objects in the primary backend using a query object.
        
        @param context: The datastore context.
        @param query_object: The query_object with search criteria.
        
        @return A list with matching objects. The List will be empty if
        nothing was found.
        """
        
        raise NotImplementedError
    
    def insert_object(self, context, object):
        """
        insert a new data object.
        
        @param context: The datastore context.
        @param object: The object to insert.
        
        @return The given object with a populated id attribute.
        """
        
        raise NotImplementedError
    
    def update_object(self, context, object):
        """
        Update an existing object.
        
        @param context: The datastore context.
        @param object: The object to update.
        """
        
        raise NotImplementedError
    
    def delete_object(self, context, object):
        """
        Delete an existing object.
        
        @param context: The datastore context.
        @param object: The object to delete.
        """
        
        raise NotImplementedError

class SqlAlchemyBackend(Backend):
    """
    Backend implementation using the SQLAlchemy ORM layer.
    """
    
    def __init__(self, persistence):
        """
        Initialize the sqlalchemy backend.
        
        @param persistence: The bot persistence.
        """
        
        self.session = persistence.get_session()
    
    def create_mapping(self, context, object, backend, identity):
        """
        Create a mapping between an object in the primary backend and an
        identity in a given secondary backend.
        
        @param context: The datastore context.
        @param object: The object in the primary backend.
        @param backend: The secondary backend.
        @param identity: The backend-specific identity.
        """
        
        # TODO 
        pass
    
    def find_objects(self, context, query_object):
        """
        Find objects in the primary backend using a query object.
        
        @param context: The datastore context.
        @param query_object: The query_object with search criteria.
        
        @return A list with matching objects. The List will be empty if
        nothing was found.
        """
        
        def find_all_calendars():
            result = self.session.query(Calendar).all()
            
            return result
        
        def find_event_by_id():
            result = self.session.query(Event).filter(Event.id == query_object.id).all()
            
            return result
        
        def find_events_at_date():
            
            result = self.session \
                   .query(Event) \
                   .filter(sqlalchemy.func.strftime('%Y-%m-%d', Event.start) <= query_object.date) \
                   .filter(sqlalchemy.func.strftime('%Y-%m-%d', Event.end) >= query_object.date) \
                   .all()
            
            return result
        
        dispatcher = {
           'all_calendars': find_all_calendars,
           'event_by_id': find_event_by_id,
           'events_at_date': find_events_at_date
        }
        
        request = query_object.get_name()
        
        result = dispatcher[request]()
        
        return result
        
    
    def insert_object(self, context, object):
        """
        insert a new data object.
        
        @param context: The datastore context.
        @param object: The object to insert.
        
        @return The given object with a populated id attribute.
        """
        
        self.session.add(object)
        self.session.commit()
        
        context.notify_secondary_backends(self.__class__.__name__, DataStore.OPERATION_INSERT, object)
        
        return object
    
    def update_object(self, context, object):
        """
        Update an existing object.
        
        @param context: The datastore context.
        @param object: The object to update.
        """
        
        self.session.commit()
        
        context.notify_secondary_backends(self.__class__.__name__, DataStore.OPERATION_UPDATE, object)
        
        return object
    
    def delete_object(self, context, object):
        """
        Delete an existing object.
        
        @param context: The datastore context.
        @param object: The object to delete.
        """
        
        self.session.delete(object)
        
        context.notify_secondary_backends(self.__class__.__name__, DataStore.OPERATION_DELETE, object)
        
        return None

class GoogleBackend(Backend):
    """
    Backend implementation using Google's GData API.
    """
    
    date_format_time = '%Y-%m-%dT%H:%M:%S.000Z'
    date_format_allday = '%Y-%m-%d'
    
    def __init__(self, service):
        """
        Initialize the backend implementation.
        
        @param service: An Google API service object which handles authentication
        """
        
        self.service = service
    
    def handle_incoming_change(self, context, source, operation, object):
        """
        Respond to a data change.
        
        @param context: The datastore context.
        @param source: The backend where the change occured.
        @param operation: The change mode, can be insert, update or delete.
        @param object: The changed object.
        
        @return Nothing
        """
        
        if self.__class__.__name__ == source:
            return
        
        dispatcher = { 
          DataStore.OPERATION_INSERT : self.insert_object,
          DataStore.OPERATION_UPDATE : self.update_object,
          DataStore.OPERATION_DELETE : self.delete_object
        }
        
        result = dispatcher[operation](context, object)
        
        return result
    
    def find_objects(self, context, query_object):
        """
        Find objects in the primary backend using a query object.
        
        @param context: The datastore context.
        @param query_object: The query_object with search criteria.
        
        @return A list with matching objects. The List will be empty if
        nothing was found.
        """
        
        raise NotImplementedError
    
    def insert_object(self, context, object):
        """
        insert a new data object.
        
        @param context: The datastore context.
        @param object: The object to insert.
        
        @return The given object with a populated id attribute.
        """
        
        def hastime(object):
            return (object.hour != 0 or object.minute != 0 or object.second != 0)
        
        def event():
            entry = gdata.calendar.data.CalendarEventEntry()
            
            entry.title = atom.data.Title(text=object.title)
                
            if object.description:
                entry.content = atom.data.Content(text=object.description)
                
            if object.location:
                entry.where.append(gdata.calendar.data.CalendarWhere(value=object.location))
            
            if hastime(object.start) and hastime(object.end):
                date_format = self.date_format_time
            elif not hastime(object.start) and not hastime(object.end):
                date_format = self.date_format_allday
            else:
                raise ValueError('start/end date: mixing of datetime and date is not allowed. start=%s, end=%s'.format(object.start, object.end))
            
            start = object.start
            
            # Google API workaround
            # when creating an event with start = x and end = y, 
            # the created event ends at y-1
            if object.start == object.end:
                end = object.end
            else:
                delta = datetime.timedelta(1)
                end = object.end + delta
            
            start_time = start.strftime(date_format)
            end_time = end.strftime(date_format)
            
            entry.when.append(gdata.calendar.data.When(start=start_time, end=end_time))
        
            """ TODO catch error """
            new_entry = self.service.calendar_client.InsertEvent(entry)
            
            new_entry.id.text
            
            
            

        
        def contact():
            pass
        
        dispatcher = {
            Event : event,
            Contact : contact
        }
        
        dispatcher[object.__class__]()

    
    def update_object(self, context, object):
        """
        Update an existing object.
        
        @param context: The datastore context.
        @param object: The object to update.
        """
        
        print "update object"
        print object
    
    def delete_object(self, context, object):
        """
        Delete an existing object.
        
        @param context: The datastore context.
        @param object: The object to delete.
        """
        
        print "delete object"
        print object
    

class FacebookBackend(Backend):
    """
    Backend implementation using the Facebook API.
    """
    
    pass

