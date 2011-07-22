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
from objects.calendar import Calendar, Event, Contact

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
        
        self.datastore = None
    
    # --------------------------------------------------------------------------
    # Lifecycle
    # --------------------------------------------------------------------------
    def start(self):
        self.datastore = DataStore()
        
        # Setup primary backend
        persistence = self.bot.get_persistence()
        sqlite = SqliteBackend(persistence.get_connection())
        self.datastore.set_primary_backend(sqlite)
        
        # Setup secondary backend
        google = GoogleBackend()
        self.datastore.register_secondary_backend(google)
        
    def shutdown(self):
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
    
    def insert_event(self, event):
        if event == None:
            return None
        
        if event.id != None:
            raise ValueError('event.id must be None')
        
        return self.datastore.insert_object(event)
        
    def update_event(self, event):
        if event == None:
            return None
        
        if event.id == None:
            raise ValueError('event.id must be given')
        
        try:
            return self.datastore.update_object(event)
        except KeyError:
            raise InvalidEventId
        
    def delete_event(self, eventId):
        if eventId == None:
            return
        
        try:
            self.datastore.delete_object(Event, eventId)
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
    
    def notify_primary_backend(self, source, operation, type, id):
        """
        Notify the primary backend about a data change.
        
        When a change at one of the the secondary backends occurs, the
        primay backend is notified about the change.  It will first update
        itself with the changed data and then propagate the changed data to
        all other secondary backends except the initiating one.
        
        A change can be a insert, update or delete operation.
        
        @param source: The backend instance that initiated the change.
        @param operation: The change mode, can be insert, update or delete.
        @param type: The data type of the changed object.
        @param id: The id of the changed object.
        
        @return Nothing
        """
        
        self.primary_backend.handle_incoming_change(self, source, operation, type, id)
    
    def register_secondary_backend(self, backend):
        """
        Register a backend object as a secondary backend.
        
        @param backend: The backend instance.
        
        @return Nothing
        """
        
        self.secondary_backends.append(backend)
    
    def notify_secondary_backends(self, source, operation, type, id):
        """
        Notify all secondary backends about a data change.
        
        When a change at the primary backend occurs, the secondary backends
        are notified about the change. They can either ignore the change
        or fetch the changed object using the provided data type and id.
        
        A change can be a insert, update or delete operation.
        
        @param source: The backend instance that initiated the change.
        @param operation: The change mode, can be insert, update or delete.
        @param type: The data type of the changed object.
        @param id: The id of the changed object.
        
        @return Nothing
        """
        
        for backend in self.secondary_backends:
            # ignore source
            if backend.__class__.__name__ == source:
                continue
            
            backend.handle_incoming_change(self, source, operation, type, id)
    
    def get_query(self, name):
        """"
        Return a new query object with the given name.
        A query object is used to query the backends for specific objects.
        
        @param name: The name of the query.
        
        @return A new DataStoreQuery instance.
        """
        
        query_object = DataStoreQuery(name)
        
        return query_object
    
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
    
    def delete_object(self, type, id):
        """
        Delete an existing object in the primary backend.
        
        @param type: The data type of the object to delete.
        @param id: The id of the object to delete.
        """
        
        return self.primary_backend.delete_object(self, type, id)

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
        
    def handle_incoming_change(self, context, source, operation, type, id):
        """
        Respond to a data change.
        
        @param context: The datastore context.
        @param source: The backend where the change occured.
        @param operation: The change mode, can be insert, update or delete.
        @param type: The data type of the changed object.
        @param id: The id of the changed object.
        
        @return Nothing
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
    
    def delete_object(self, context, type, id):
        """
        Delete an existing object.
        
        @param context: The datastore context.
        @param type: The data type of the object to delete.
        @param id: The id of the object to delete.
        """
        
        raise NotImplementedError

class SqliteBackend(Backend):
    """
    Backend implementation using a local sqlite database.
    
    TODO: implement object space.
    """
    
    class Query():
        """
        Implement a simple sqlite query.
        """
        
        def __init__(self, type, query):
            """
            Instantiate a new query.
            
            @param query: The SQL query that gets executed.
            """
            self.type = type
            self.query = query
            
        def get_type(self):
            """
            Return the data type of the query result.
            
            @return The data type of the query result.
            """
            
            return self.type
            
        def execute(self, connection, parameters={}):
            """
            Execute the query.
            
            @param connection: The sqlite connection to use.
            @param parameters: A optional list of named parameters.
            
            @return 
            """
            return connection.execute(self.query, parameters)
        
    def __init__(self, persistence):
        """
        Initialize the sqlite backend.
        
        @param persistence: The bot persistence.
        """
        
        self.connection = persistence.get_connection()
        
        self.query_list = {
            'last_calendar_id'     : self.Query(Calendar, 'SELECT last_insert_rowid() AS ID FROM CALENDARS'),
            'find_all_calendars'   : self.Query(Calendar, 'SELECT ID, NAME, TYPE FROM CALENDARS'),
            'find_calendar_by_ids' : self.Query(Calendar, 'SELECT ID, NAME, TYPE FROM CALENDARS WHERE ID IN (:ids)'),
            'insert_calendar'      : self.Query(Calendar, 'INSERT INTO CALENDARS (ID, NAME, TYPE) VALUES (NULL, :name, :type)'),
            'update_calendar'      : self.Query(Calendar, 'UPDATE CALENDARS SET NAME=:name, TYPE=:type WHERE ID=:id'),
            'delete_calendar'      : self.Query(Calendar, 'DELETE FROM CALENDARS WHERE ID=:id'),
            
            'last_event_id'        : self.Query(Event, 'SELECT last_insert_rowid() AS ID FROM EVENTS'),
            'find_event_by_id'     : self.Query(Event, 'SELECT ID, G_ETAG, DATE_FROM, DATE_TO, DATE_ALLDAY, TITLE, DESCRIPTION, LOCATION FROM EVENTS WHERE ID=:id'),
            'find_events_at_date'  : self.Query(Event, 'SELECT ID, G_ETAG, DATE_FROM, DATE_TO, DATE_ALLDAY, TITLE, DESCRIPTION, LOCATION FROM EVENTS WHERE DATE_FROM <= :date AND DATE_TO >= :date'),
            'insert_event'         : self.Query(Event, 'INSERT INTO EVENTS (ID, CALENDAR_ID, G_ETAG, DATE_FROM, DATE_TO, DATE_ALLDAY, TITLE, DESCRIPTION, LOCATION) VALUES (NULL, :calendar_id, :g_etag, :date_from, :date_to, date_allday, :title, :description, :location)'),
            'update_event'         : self.Query(Event, 'UPDATE EVENTS SET CALENDAR_ID=:calendar_id, G_ETAG=:g_etag, DATE_FROM=:date_from, DATE_TO=:date_to, DATE_ALLDAY=:date_allday, TITLE=:title, DESCRIPTION=:description, LOCATION WHERE ID=:id'),
            'delete_event'         : self.Query(Event, 'DELETE FROM EVENTS WHERE ID=:id'),
            
            'last_contact_id'      : self.Query(Contact, 'SELECT last_insert_rowid() AS ID FROM CONTACTS'),
            'insert_contact'       : self.Query(Contact, 'INSERT INTO CONTACTS (ID, FIRSTNAME, LASTNAME, NICKNAME, BIRTHDAY) VALUES (NULL, :firstname, :lastname, :birthday)'),
            'update_contact'       : self.Query(Contact, 'UPDATE CONTACTS SET FIRSTNAME=:firstname, LASTNAME=:lastname, NICKNAME=:nickname BIRTHDAY=:birthday WHERE ID=:id'),
            'delete_contact'       : self.Query(Contact, 'DELETE FROM CONTACTS WHERE ID=:id'),
        }
        
    def get_query(self, name):
        """
        Get a concrete sqlite query object.
        
        @param name: The name of the query.
        
        @return A Query instance.
        """
        
        return self.query_list[name]
    
    def handle_incoming_change(self, context, source, operation, type, id):
        """
        Respond to a data change.
        
        @param context: The datastore context.
        @param source: The backend where the change occured.
        @param operation: The change mode, can be insert, update or delete.
        @param type: The data type of the changed object.
        @param id: The id of the changed object.
        
        @return Nothing
        """
        
        raise NotImplementedError
    
    def find_objects(self, context, abstract_query):
        """
        Find objects in the primary backend using a query object.
        
        @param abstract_query: A query object with search criteria.
        
        @return A list with matching objects. The List will be empty if
        nothing was found.
        """
        
        sql_query = self.get_query(abstract_query.get_name())
        
        query_result = sql_query.execute(self.connection, abstract_query.get_parameters())
        
        result = []
        
        # ----------------------------------------------------------------------
        # Handle retrieval of Calendar objects
        # ----------------------------------------------------------------------
        if sql_query.get_type() == Calendar:
            for row in query_result:
                result.append(
                    Calendar(
                        id=row['id'],
                        name=row['name'],
                        type=row['type']
                    )
                )
        
        # ----------------------------------------------------------------------
        # Handle retrieval of Event objects
        # ----------------------------------------------------------------------
        if sql_query.get_type() == Event:
            calendar_fetch = []
            
            for row in query_result:
                if row['date_allday']:
                    allday = True
                else:
                    allday = False
                
                if row['calendar_id'] and row['calendar_id'] not in calendar_fetch:
                    calendar_fetch.append(row['calendar_id']) 
                
                result.append(
                    Event(
                        id=row['id'],
                        calendar=row['calendar_id'],
                        etag=row['g_etag'],
                        start=row['date_from'],
                        end=row['date_to'],
                        allday=allday,
                        title=row['title'],
                        description=row['description'],
                        location=row['location']
                    )
                )
                
            # resolve relation manually
            # TODO use some lightweight ORM framework
            if len(calendar_fetch) > 0:
                abstract_query = DataStoreQuery('find_calendar_by_ids')
                abstract_query.ids = ','.join(calendar_fetch)
                
                calendars = {}
                
                for calendar in self.find_objects(context, abstract_query):
                    calendars[calendar.id] = calendar
                    
                for event in result:
                    event.calendar = calendars[event.calendar]
        
        # ----------------------------------------------------------------------
        # Handle retrieval of Contact objects
        # ----------------------------------------------------------------------
        if sql_query.get_type() == Contact:
            for row in query_result:
                result.append(
                    Contact(
                        id=row['id'],
                        firstname=row['firstname'],
                        lastname=row['lastname'],
                        nickname=row['nickname'],
                        birthday=row['birthday']
                    )
                )
        
        return result
    
    def insert_object(self, context, object):
        """
        insert a new data object.
        
        @param context: The datastore context.
        @param object: The object to insert.
        
        @return The given object with a populated id attribute.
        """
        
        if not isinstance(object, Calendar) and not isinstance(object, Event) and not isinstance(object, Contact):
            raise ValueError('object type %s is not a calendar object instance'.format(object.__class__.__name__))
        
        # ----------------------------------------------------------------------
        # Handle insertion of Calendar objects
        # ----------------------------------------------------------------------
        if isinstance(object, Calendar):
            object_query = 'insert_calendar'
            id_query = 'last_calendar_id'
            
            object_data = {
                'name': object.name,
                'type': object.type
            }
            
        # ----------------------------------------------------------------------
        # Handle insertion of Event objects
        # ----------------------------------------------------------------------
        if isinstance(object, Event):
            object_query = 'insert_event'
            id_query = 'last_event_id'
            
            # object.calendar can either be a Calendar object or an integer 
            # with the corresponding calendar database id.
            if isinstance(object.calendar, Calendar):
                # When calendar object is not persistent (id is None), 
                # insert it before insertion of event object.
                if not object.calendar.id:
                    self.insert_object(context, object.calendar)
                
                calendar_id = object.calendar.id
                
            else:
                calendar_id = object.calendar
            
            object_data = {
                'calendar_id' : calendar_id,
                'g_etag'      : object.etag,
                'date_from'   : object.start,
                'date_to'     : object.end,
                'date_allday' : object.allday,
                'title'       : object.title,
                'description' : object.description,
                'location'    : object.location
            }
            
        # ----------------------------------------------------------------------
        # Handle insertion of Contact objects
        # ----------------------------------------------------------------------
        if isinstance(object, Contact):
            object_query = 'insert_contact'
            id_query = 'last_contact_id'
            
            object_data = {
                'firstname' : object.firstname,
                'lastname'  : object.lastname,
                'nickname'  : object.nickname,
                'birthday'  : object.birthday
            }
        
        with self.connection:
            self.get_query(object_query).execute(self.connection, object_data)
        
        id = self.get_query(id_query).execute(self.connection).fetchone()
        
        if id:
            object.id = id['id']
            
        return object
    
    def update_object(self, context, object):
        """
        Update an existing object.
        
        @param context: The datastore context.
        @param object: The object to update.
        """
        
        if isinstance(object, Calendar):
            pass
        
        if isinstance(object, Event):
            pass
        
        if isinstance(object, Contact):
            pass
    
    def delete_object(self, context, type, id):
        """
        Delete an existing object.
        
        @param context: The datastore context.
        @param type: The data type of the object to delete.
        @param id: The id of the object to delete.
        """
        
        if isinstance(object, Calendar):
            pass
        
        if isinstance(object, Event):
            pass
        
        if isinstance(object, Contact):
            pass

class GoogleBackend(Backend):
    """
    Backend implementation using Google's GData API.
    """
    
    pass

class FacebookBackend(Backend):
    """
    Backend implementation using the Facebook API.
    """
    
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
