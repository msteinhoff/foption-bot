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
import time
import json

import sqlalchemy.orm.exc
import atom.data
import gdata.calendar.data
import gdata.contacts.data

from core import runlevel
from core.config import Config
from core.component import Component, ComponentError
from objects.calendar import Calendar, Event, Contact, Backend,\
    CalendarPeerIdentity, EventPeerIdentity, ContactPeerIdentity

# ------------------------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------------------------
class CalendarComponentError(ComponentError): pass
class InvalidObjectId(CalendarComponentError): pass

# ------------------------------------------------------------------------------
# Business Logic
# ------------------------------------------------------------------------------
class CalendarComponent(Component):
    RUNLEVEL = runlevel.Runlevel(
        autoboot=True,
        minimum_start=runlevel.LOCAL_COMPONENT
    )
    
    def __init__(self, bot):
        Component.__init__(self, bot)
        
        self.bot.register_config(CalendarComponentConfig)
        
        self.logger = self.bot.get_logger('components.calendar')
        self.config = self.bot.get_config('components.calendar')
        
        self.datastore = None
    
    # --------------------------------------------------------------------------
    # Lifecycle
    # --------------------------------------------------------------------------
    def _start(self):
        """
        Startup the component and background services (DataStore, Backends).
        
        Implementation of Subsystem.start()
        """
        
        datastore = DataStore(DataStoreOneWaySync)
        
        # Setup primary backend
        sqlite = SqlAlchemyBackend(datastore, self.bot.get_subsystem('local-persistence'))
        datastore.set_primary_backend(sqlite)
        
        # Setup secondary backend
        google = GoogleBackend(datastore, self.bot.get_subsystem('google-api-service'))
        datastore.register_secondary_backend(google)
        
        datastore.register_authority(SystemAllowAuthority(), default=True)
        datastore.register_authority(SystemDenyAuthority())
        datastore.register_authority(LocalUserAuthority())
        datastore.register_authority(LocalBirthdayAuthority())
        
        self.datastore = datastore
        
        self._running()
        
    def _stop(self):
        """
        Shutdown the component and background services (DataStore, Backends).
        
        Implementation of Subsystem.stop()
        """
        
        self.datastore = None
        
        self._halted()
    
    # --------------------------------------------------------------------------
    # Component methods: global
    # --------------------------------------------------------------------------
    def insert_object(self, object):
        if object is None:
            raise ValueError('object must be given')
        
        if object.id is not None:
            raise ValueError('object.id must be None')
        
        result = self.datastore.insert_object(
            self.__class__.__name__,
            object
        )
        
        return result
        
    def update_object(self, object):
        if object is None:
            raise ValueError('object must be given')
        
        if object.id is None:
            raise ValueError('object.id must be given')
        
        self.datastore.update_object(
            self.__class__.__name__,
            object
        )
        
    def delete_object(self, object):
        if object is None:
            raise ValueError('object must be given')
        
        if object.id is None:
            raise ValueError('object.id must be given')
        
        self.datastore.delete_object(
            self.__class__.__name__,
            object
        )
    
    # --------------------------------------------------------------------------
    # Component methods: calendars
    # --------------------------------------------------------------------------
    def find_all_calendars(self):
        query = self.datastore.get_query('all_calendars')
        
        return self.datastore.find_objects(query)
    
    def find_calendar_by_id(self, id):
        if id is None:
            return None
        
        query = self.datastore.get_query('calendar_by_id')
        query.id = id
        
        return self.datastore.find_objects(query)
    
    def find_calendars_by_string(self, string):
        if string is None:
            return None
        
        query = self.datastore.get_query('calendars_by_string')
        query.string = string
        
        return self.datastore.find_objects(query)
    
    # --------------------------------------------------------------------------
    # Component methods: events
    # --------------------------------------------------------------------------
    def find_all_events(self):
        query = self.datastore.get_query('all_events')
        
        return self.datastore.find_objects(query)
    
    def find_event_by_id(self, id):
        if id is None:
            return None
        
        query = self.datastore.get_query('event_by_id')
        query.id = id
        
        return self.datastore.find_objects(query)
    
    def find_events_by_string(self, string):
        if string is None:
            return None
        
        query = self.datastore.get_query('events_by_string')
        query.string = string
        
        return self.datastore.find_objects(query)
    
    def find_events_at_date(self, date):
        if date is None:
            return None
        
        query = self.datastore.get_query('events_at_date')
        query.date = date
        
        return self.datastore.find_objects(query)
    
    # --------------------------------------------------------------------------
    # Component methods: contacts
    # --------------------------------------------------------------------------
    def find_all_contacts(self):
        query = self.datastore.get_query('all_contacts')
        
        return self.datastore.find_objects(query)
    
    def find_contact_by_id(self, id):
        if id is None:
            return None
        
        query = self.datastore.get_query('contacts_by_id')
        query.id = id
        
        return self.datastore.find_objects(query)
    
    def find_contacts_by_string(self, string):
        if string is None:
            return None
        
        query = self.datastore.get_query('contacts_by_string')
        query.string = string
        
        return self.datastore.find_objects(query)

class CalendarComponentConfig(Config):
    identifier = 'components.calendar'
        
    def valid_keys(self):
        return [
            'defaultCalendarId'
        ]
    
    def default_values(self):
        return {
            'defaultCalendarId' : None
        }


# ------------------------------------------------------------------------------
# Data management
# ------------------------------------------------------------------------------
class DataStoreError(CalendarComponentError): pass
class InvalidQueryName(DataStoreError): pass

class DataStore():
    """
    The calendar data store.
    
    The data store manages all backend systems and data synchronization
    between the primary and secondary backends.
    """
    
    def __init__(self, strategy):
        """
        Initialize the datastore.
        
        @param: Class pointer to the sync strategy implementation to use.
        """
        
        self.primary_backend = None
        self.authorities = {}
        self.defaulf_authority = None
        self.secondary_backends = []
        self.strategy = strategy(self)
    
    def set_primary_backend(self, backend):
        """
        Set a backend object as the primary backend.
        
        @param backend: The backend instance.
        
        @return None
        """
        
        self.primary_backend = backend
    
    def register_secondary_backend(self, backend):
        """
        Register a backend object as a secondary backend.
        
        @param backend: The backend instance.
        
        @return None
        """
        
        self.secondary_backends.append(backend)
        
        
    def register_authority(self, authority, default=False):
        """
        Register a new object authority.
        
        @param authority: The authority instance.
        @param authority: If the instance should be the default authority.
        
        @return None
        """
        
        name = authority.NAME
        self.authorities[name] = authority
        
        if default:
            self.defaulf_authority = name
        
    def get_authority(self, name=None):
        """
        Return a authority by name.
        
        @param name: The name of the authority.
        
        @return The authority instance.
        """
        
        if not name:
            name = self.defaulf_authority
        
        return self.authorities[name]
    
    def get_query(self, name):
        """"
        Return a new query object with the given name.
        A query object is used to query the backends for specific objects.
        
        @param name: The name of the query.
        
        @return A new DataStoreQuery instance.
        """
        
        query_object = DataStoreQuery(name)
        
        return query_object
    
    def find_objects(self, query):
        """
        Find objects in the primary backend using a query object.
        
        @param query: A DataStoreQuery instance with search criteria.
        
        @return A list with matching objects. The List will be empty if
        nothing was found.
        """
        
        return self.primary_backend.find_objects(self, query)
    
    def find_identities(self, object):
        """
        Find a identity for a specific object in the primary query.
        
        @param object: The object to use.
        """
        
        return self.primary_backend.find_datastore_identities(object)
    
    def insert_object(self, source, object):
        """
        insert a new object into the datastore.
        
        @param source: The source of this action.
        @param object: The object to insert.
        
        @return The given object with a populated id attribute.
        """
        
        return self.strategy.insert(source, object)
    
    def update_object(self, source, object):
        """
        Update an existing object in the datastore.
        
        @param source: The source of this action.
        @param object: The object to update.
        
        @return The updated object.
        """
        
        self.strategy.update(source, object)
    
    def delete_object(self, source, object):
        """
        Delete an existing object from the datastore.
        
        @param source: The source of this action.
        @param object: The object to delete.
        """
        
        self.strategy.delete(source, object)

class DataStoreSyncStrategy(object):
    """
    Abstract implementation for backend all synchronization strategies.
    """
    
    def __init__(self, datastore):
        """
        Initialize the strategy.
        """
        self.datastore = datastore
        
    def insert(self, source, object):
        """
        Handle insert algorithm.
        
        @param source: Classname where the object comes from.
        @param object: The object to be inserted.
        """
        raise NotImplementedError
    
    def update(self, source, object):
        """
        Handle update algorithm.
        
        @param source: Classname where the object comes from.
        @param object: The object to be updated.
        """
        raise NotImplementedError
    
    def delete(self, source, object):
        """
        Handle delete algorithm.
        
        @param source: Classname where the object comes frome.
        @param object: The object to be deleted.
        """
        raise NotImplementedError

class DataStoreOneWaySync(DataStoreSyncStrategy):
    """
    Implementation for a one-way synchronization mechanism.
    
    Data is exclusively entered locally into the primary backend and
    replicated to all secondary backends. The secondary entities are mapped
    to the primary entites by id.
    """
    
    def insert(self, source, object):
        """
        Insert a new object.
        
        @param source: The object source' classname.
        @param source: The local object.
        
        @return The local object with populated id and mappings.
        """
        
        primary = self.datastore.primary_backend
        secondaries = self.datastore.secondary_backends
        
        try:
            stored_object = primary.insert_object(object)
            
            try:
                authority = self.datastore.get_authority(object.get_authority_name())
            except AttributeError:
                authority = self.datastore.get_authority()
            
            for secondary in secondaries:
                if not authority.may_replicate(object, primary, secondary):
                    continue
                
                datastore_identity = secondary.insert_object(object)
                
                primary.create_backend_identity(
                    stored_object,
                    datastore_identity
                )
            
            primary.commit_transaction()
        
        except:
            primary.rollback_transaction()
            raise
        
        return stored_object
        
    def update(self, source, object):
        """
        Update an existing object.
        
        @param source: The object source' classname.
        @param source: The local object.
        """
        
        primary = self.datastore.primary_backend
        secondaries = self.datastore.secondary_backends
        
        try:
            primary.update_object(object)
            
            datastore_ids = {}
            
            for identity in object.identities:
                datastore_id = DataStorePeerIdentity(
                    backend=identity.backend.typename,
                    type=identity.typename,
                    identity=identity.identity
                )
                
                datastore_ids[identity.backend.typename] = datastore_id
            
            for secondary in secondaries:
                secondary.update_object(
                    datastore_ids[secondary.__class__.__name__],
                    object
                )
            
            primary.commit_transaction()
        
        except:
            primary.rollback_transaction()
            raise
    
    def delete(self, source, object):
        """
        Delete an existing object.
        
        @param source: The object source' classname.
        @param source: The local object.
        """
        
        primary = self.datastore.primary_backend
        secondaries = self.datastore.secondary_backends
        
        try:
            datastore_ids = {}
            
            for identity in object.identities:
                datastore_id = DataStorePeerIdentity(
                    backend=identity.backend.name,
                    type=identity.typename,
                    identity=identity.identity
                )
                
                datastore_ids[identity.backend.typename] = datastore_id
            
            for secondary in secondaries:
                secondary.delete_object(
                    datastore_ids[secondary.__class__.__name__]
                )
        
            primary.delete_object(object)
            
            primary.commit_transaction()
        
        except:
            primary.rollback_transaction()
            raise

class DataStoreTwoWaySync(DataStoreSyncStrategy):
    """
    Implementation for a two-way synchronization mechanism.
    
    Data can be copied/synchronized from the primary backend to all
    secondary backends. Additionally, all secondary backends can
    request a data update in the primary backend which if successful
    will be populated to all other secondary backends. The data update
    request must be initiated from outside of this class.
    """
    
    def insert(self, source, object):
        """
        Insert a new object.
        
        @param source: The object source' classname.
        @param source: The local object.
        
        @return The local object with populated id and mappings.
        """
        
        return object
    
    def update(self, source, object):
        """
        Update an existing object.
        
        @param source: The object source' classname.
        @param source: The local object.
        """
        
        pass
    
    def delete(self, source, object):
        """
        Delete an existing object.
        
        @param source: The object source' classname.
        @param source: The local object.
        """
        
        pass
    
class DataStoreQuery(object):
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

class DataStorePeerIdentity(object):
    """
    A storage-idenpendent, backend-specific identity for a given entity.
    """
    
    def __init__(self, backend=None, type=None, identity=None):
        """
        @param backend: The classname of the backend.
        @param type: The classname of the entity type.
        @param identity: The entity identity.
        """
        self.backend = backend
        self.type = type
        self.identity = identity

class DataStoreAuthority(object):
    """
    An abstract data store object authority.
    
    A object authority decides whether a specific object is allowed to be
    replicated between two backends.
    """
    
    def may_replicate(self, object, source, destination):
        """
        Decide wether the given object may be replicated from src to dst.
        
        @param object: The object to check.
        @param source: The source backend.
        @param destination: The destination backend.
        """
        
        return NotImplementedError

class SystemAllowAuthority(DataStoreAuthority):
    """
    A default authority.
    
    All objects may replicate.
    """
    
    NAME = '/system/allow'
    
    def may_replicate(self, object, source, destination):
        return True

class SystemDenyAuthority(DataStoreAuthority):
    """
    A system authority.
    
    No objects may replicate.
    """
    
    NAME = '/system/deny'
    
    def may_replicate(self, object, source, destination):
        return False

class LocalUserAuthority(DataStoreAuthority):
    """
    An authority for objects created by local users.
    
    All objects may replicate.
    """
    
    NAME = '/local/user'
    
    def may_replicate(self, object, source, destination):
        return True

class LocalBirthdayAuthority(DataStoreAuthority):
    """
    An authority for objects created by local users.
    
    Keep all authority-based objects local.
    """
    
    NAME = '/local/birthday'
    
    def may_replicate(self, object, source, destination):
        return False

class DataStoreBackend(object):
    """
    An abstract datastore backend implementation.
    """
    
    class Query(object):
        """
        An abstract Query implementation.
        Queries are used for data retrieval.
        """
        
        def execute(self, endpoint, query):
            """
            Execute the requested query against the concrete service
            endpoint.
            
            The query is executed using a query handler, which can be
            any class method.
            
            @param endpoint: The service endpoint.
            @param query: The DataStoreQuery instance.
            
            @return The result of the query.
            
            @raise InvalidQueryName if no query handler was found.
            """
            
            name = query.get_name()
            
            try:
                handler = getattr(self, name)
                
                result = handler(endpoint, query)
                
            except AttributeError:
                raise InvalidQueryName
            
            return result
        
    class Adapter(object):
        """
        An abstract Adapter implementation.
        Adapters are used for data manipulation.
        """
        
        pass

class SqlAlchemyBackend(DataStoreBackend):
    """
    Backend implementation using the SQLAlchemy ORM layer.
    """
    
    class Query(DataStoreBackend.Query):
        def __with_deleted(self, query):
            """
            Return if the result should contain entries marked as deleted.
            
            @param query: The DataStoreQuery to check.
            
            @return True if deleted entries are requested, otherwise False.
            """
            return (hasattr(query, 'with_deleted') and query.with_deleted)
        
        def all_calendars(self, session, query):
            """
            @return All calendar objects.
            """
            
            result = session \
                   .query(Calendar) \
                   .filter(Calendar.isDeleted == self.__with_deleted(query)) \
                   .all()
            
            return result
        
        def calendar_by_id(self, session, query):
            """
            @return A single calendar object with the id of query.id.
            """
            
            try:
                result = session \
                       .query(Calendar) \
                       .filter(Calendar.id == query.id) \
                       .filter(Calendar.isDeleted == self.__with_deleted(query)) \
                       .one()
                
            except sqlalchemy.orm.exc.NoResultFound:
                result = []
            
            return result
        
        def calendars_by_string(self, session, query):
            """
            @return Calendar objects where the name contains the query.string.
            """
            
            result = session \
                   .query(Calendar) \
                   .filter(Calendar.title.contains(query.string)) \
                   .filter(Event.isDeleted == self.__with_deleted(query)) \
                   .all()
                   
            return result
        
        def all_events(self, session, query):
            """
            @return All event objects.
            """
            
            result = session \
                   .query(Event) \
                   .filter(Event.isDeleted == self.__with_deleted(query)) \
                   .all()
            
            return result
        
        def event_by_id(self, session, query):
            """
            @return A single event object with the id of query.id
            """
            
            try:
                result = session \
                       .query(Event) \
                       .filter(Event.id == query.id) \
                       .filter(Event.isDeleted == self.__with_deleted(query)) \
                       .one()
                
            except sqlalchemy.orm.exc.NoResultFound:
                result = []
            
            return result
        
        def events_by_string(self, session, query):
            """
            @return Event objects where the title, description or 
                    location contain the query.string.
            """
            
            result = session \
                   .query(Event) \
                   .filter(sqlalchemy.or_( \
                        Event.title.contains(query.string), \
                        Event.description.contains(query.string), \
                        Event.location.contains(query.string) \
                    )) \
                   .filter(Event.isDeleted == self.__with_deleted(query)) \
                   .all()
                   
            return result
        
        def events_at_date(self, session, query):
            """
            @return Event objects that lie between query.start and query.end.
            """
            
            result = session \
                   .query(Event) \
                   .filter(sqlalchemy.func.strftime('%Y-%m-%d', Event.start) <= query.date) \
                   .filter(sqlalchemy.func.strftime('%Y-%m-%d', Event.end) >= query.date) \
                   .filter(Event.isDeleted == self.__with_deleted(query)) \
                   .all()
            
            return result
        
        def all_contacts(self, session, query):
            """
            @return All contact objects.
            """
            
            result = session.query(Contact).filter(Contact.isDeleted == self.__with_deleted(query)).all()
            
            return result
        
        def contact_by_id(self, session, query):
            """
            @return A single contact object with the id of query.id.
            """
            
            try:
                result = session \
                       .query(Contact) \
                       .filter(Contact.id == query.id) \
                       .filter(Contact.isDeleted == self.__with_deleted(query)) \
                       .one()
                
            except sqlalchemy.orm.exc.NoResultFound:
                result = []
            
            return result
        
        def contacts_by_string(self, session, query):
            """
            @return Contact objects where the firstname, lastname or
                    nickname contain the query.string.
            """
            
            result = session \
                   .query(Contact) \
                   .filter(sqlalchemy.or_( \
                        Contact.firstname.contains(query.string), \
                        Contact.lastname.contains(query.string), \
                        Contact.nickname.contains(query.string) \
                    )) \
                   .filter(Event.isDeleted == self.__with_deleted(query)) \
                   .all()
                   
            return result
    
    def __init__(self, datastore, persistence):
        """
        Initialize the sqlalchemy backend.
        
        @param datastore: The datastore.
        @param persistence: The bot persistence.
        """
        
        self.datastore = datastore
        self.session = persistence.get_session()
        self.query = self.Query()
    
    def begin_transaction(self):
        """
        Begin a new transaction.
        """
        
        self.session.begin()
    
    def commit_transaction(self):
        """
        Commit the session's transaction.
        """
        
        self.session.commit()
    
    def rollback_transaction(self):
        """
        Rollback the session's transaction.
        """
        
        self.session.rollback()
    
    def request_backend(self, typename):
        """
        Request a backend object from the database.
        When the object was not found, a new object will be created.
        
        @param typename: The typename of the backend.
        
        @return A Backend instance.
        """
        
        try:
            backend = self.session \
                    .query(Backend) \
                    .filter(Backend.typename == typename) \
                    .one()
                    
        except sqlalchemy.orm.exc.NoResultFound:
            backend = Backend(typename=typename)
            
            self.session.add(backend)
        
        return backend
    
    def create_backend_identity(self, object, datastore_identity):
        """
        Create a mapping between a local object and an remote peer identity.
        
        @param object: The local object.
        @param identity: The DataStorePeerIdentity object.
        """
        
        def calendar():
            identity = CalendarPeerIdentity()
            identity.calendar = object
            
            return identity
        
        def event():
            identity = EventPeerIdentity()
            identity.event = object
            
            return identity
        
        def contact():
            identity = ContactPeerIdentity()
            identity.contact = object
            
            return identity
        
        dispatcher = {
            'Calendar': calendar,
            'Event': event,
            'Contact': contact
        }
        
        identity = dispatcher[datastore_identity.type]()
        
        identity.backend = self.request_backend(datastore_identity.backend)
        identity.identity = datastore_identity.identity
        
        self.session.add(identity)
    
    def find_datastore_identities(self, object):
        """
        Returns a DataStorePeerIdentity for a given local object.
        
        @param object: The local object.
        
        @return A DataStorePeerIdentity instance.
        """
        
        result = []
        
        for identity in object.identities:
            datastore_identity = DataStorePeerIdentity()
            datastore_identity.backend = identity.backend.typename
            datastore_identity.type = identity.typename
            datastore_identity.identity = identity.identity
            
            result.append(datastore_identity)
            
        return result
    
    def find_objects(self, query):
        """
        Find objects in the primary backend using a query object.
        
        See SqlAlchemyBackend.Query for supported queries.
        
        @param query_object: The query_object with search criteria.
        
        @return A list with matching objects. The List will be empty if
        nothing was found.
        """
        
        result = self.query.execute(self.session, query)
        
        return result
        
    
    def insert_object(self, object):
        """
        insert a new data object.
        
        @param object: The object to insert.
        
        @return The given object with a populated id attribute.
        """
        
        self.session.add(object)
        
        return object
    
    def should_replicate(self, object):
        """
        Check whether the given object should be replicated to secondary
        backends.
        
        @param object: The object to check.
        
        @return True if it is ok to replicate the object, otherwise False.
        """
        
        check = {
            'Calendar' : lambda: (object.type == Calendar.BASIC), 
            'Event': lambda: (object.calendar.type == Calendar.BASIC), 
            'Contact': True
        }
        
        return check[object.__class__.__name__]()
    
    def update_object(self, object):
        """
        Update an existing object.
        
        This method actually does nothing as SqlAlchemy maintains
        attribute state and marks objects as dirty as soon as attributes
        change.
        The actual database update will be executed when committing the
        current transaction.
        
        @param object: The object to update.
        """
        
        # legacy code
        #self.session.save(object)
        pass
    
    def delete_object(self, object):
        """
        Delete an existing object.
        
        @param object: The object to delete.
        """
        
        object.isDeleted = True

class GoogleBackend(DataStoreBackend):
    """
    Backend implementation using Google's GData API.
    """
    
    LINK_EDIT = 'edit'
    LINK_EVENTFEED = 'http://schemas.google.com/gCal/2005#eventFeed'
    
    class Query(DataStoreBackend.Query):
        def all_calendars_feed(self, service, query):
            """
            @return An atom feed with all calendar objects.
            """
            
            return service.calendar_client.GetOwnCalendarsFeed()
        
        def calendar_by_id(self, service, query):
            """
            @return A single calendar object with the id of query.id.
            """
            
            return service.calendar_client.get_calendar_entry(uri=query.id)
        
        def event_by_id(self, service, query):
            """
            @return A single event object with the id of query.id.
            """
            
            return service.calendar_client.get_event_entry(uri=query.id)
        
        def contact_by_id(self, service, query):
            """
            @return A single contact object with the id of query.id.
            """
            
            return service.contacts_client.get_contact(uri=query.id)
    
    class Adapter(DataStoreBackend.Adapter):
        """
        Abstract implementation for manipulation of GData entries.
        """
        
        date_format_time = '%Y-%m-%dT%H:%M:%S.000Z'
        date_format_allday = '%Y-%m-%d'
    
        def hastime(self, object):
            """
            Check if the given datetime object contains time.
            
            TODO: this implementation is not optimal as an intentional 
            TODO: date at 00:00:00 produces a false positive result.
            
            @param object: The datetime object.
            """
            
            if hasattr(object, 'hour') and hasattr(object, 'minute') and hasattr(object, 'second'):
                return (object.hour != 0 or object.minute != 0 or object.second != 0)
            
            return False
        
        def new_identity(self):
            """
            Create a new DataStorePeerIdentity object.
            
            @return A DataStorePeerIdentity instance from the GoogleBackend.
            """
            
            identity = DataStorePeerIdentity()
            identity.backend = 'GoogleBackend'
            
            return identity
        
        def json_links(self, gdata_object):
            """
            Convert data from a atom.Link list into a JSON string.
            
            @param gdata_object: The GData object containing the links.
            
            @return A link.rel=>link.href dict in JSON.
            """
            
            list  = {}
            
            for link in gdata_object.link:
                if link.rel is None or link.href is None:
                    continue
                
                list[link.rel] = link.href
                
            result = json.dumps(list)
            
            return result
            
    class CalendarEntryAdapter(Adapter):
        """
        Manipulate GData CalendarEntry objects.
        """
        
        def _local_to_gdata(self, local_object, gdata_object):
            """
            Update a GData instance with data from a local instance.
            
            @param local_object: An objects.Calendar instance.
            @param gdata_object: An gdata.contacts.data.CalendarEntry instance.
            
            @return The updated gdata_object.
            """
            
            #-------------------------------------------------------------------
            # Calendar: title
            #-------------------------------------------------------------------
            if local_object.title:
                if gdata_object.title:
                    gdata_object.title.text = local_object.title
                else:
                    gdata_object.title = atom.data.Title(text=local_object.title)
            
            #-------------------------------------------------------------------
            # Calendar: summary
            #-------------------------------------------------------------------
            if local_object.summary:
                if gdata_object.summary:
                    gdata_object.summary.text = local_object.summary
                else:
                    gdata_object.summary = atom.data.Summary(text=local_object.summary)
            
            #-------------------------------------------------------------------
            # Calendar: timezone
            #-------------------------------------------------------------------
            # TODO: default timezone configurable
            if gdata_object.timezone is None:
                gdata_object.timezone = gdata.calendar.data.TimeZoneProperty(value='Europe/Berlin')
            
            #-------------------------------------------------------------------
            # Calendar: where
            #-------------------------------------------------------------------
            # TODO: default location configurable
            if local_object.location:
                if len(gdata_object.where) > 0:
                    # TODO: bad implementation, unclear specification from google
                    # TODO: assume where always contains only one element with index 0
                    gdata_object.where[0].value = local_object.location
                    
                else:
                    where = gdata.calendar.data.CalendarWhere(
                        value=local_object.location
                    )
                    
                    gdata_object.where.append(where)
            
            else:
                if len(gdata_object.where) == 0:
                    where = gdata.calendar.data.CalendarWhere(
                        value='Duesseldorf, Germany'
                    )
                    
                    gdata_object.where.append(where)
            
            #-------------------------------------------------------------------
            # Calendar: color
            #-------------------------------------------------------------------
            if local_object.color:
                color = '#{0}'.format(local_object.color)
                
                if gdata_object.color:
                    gdata_object.color.value = color
                else:
                    gdata_object.color = gdata.calendar.data.ColorProperty(value=color)
            
            else:
                # TODO: default color configurable
                color = '#000000'
                
                if gdata_object.color is None:
                    gdata_object.color = gdata.calendar.data.ColorProperty(value=color)
            
            return gdata_object
        
        def _gdata_to_local(self, local_object, gdata_object):
            """
            Update a local instance with data from a GData instance.
            
            @param local_object: An objects.Calendar instance.
            @param gdata_object: An gdata.contacts.data.CalendarEntry instance.
            
            @return The updated local_object.
            """
            
            #-------------------------------------------------------------------
            # Calendar: title
            #-------------------------------------------------------------------
            if gdata_object.title:
                local_object.title = gdata_object.title.text 
            
            #-------------------------------------------------------------------
            # Calendar: summary
            #-------------------------------------------------------------------
            if gdata_object.summary:
                local_object.summary = gdata_object.summary.text 
            
            #-------------------------------------------------------------------
            # Calendar: where
            #-------------------------------------------------------------------
            if gdata_object.location and len(gdata_object.where) > 0:
                local_object.location = gdata_object.where[0].value 
            
            #-------------------------------------------------------------------
            # Calendar: color
            #-------------------------------------------------------------------
            if gdata_object.color.value:
                local_object.color = '#{0}'.format(gdata_object.color.value)
            
            #-------------------------------------------------------------------
            # Calendar: type (internal attribute)
            #-------------------------------------------------------------------
            if len(gdata_object.extended_property) > 0:
                for property in gdata_object.extended_property:
                    if property.name == self.properties['type']:
                        local_object.type = property.value
            
            return gdata_object
        
        def insert(self, backend, local_object):
            """
            Insert a local object into the Google Service.
            
            @param backend: The Google Backend.
            @param local_object: An objects.Calendar instance.
            
            @return a DataStorePeerIdentity with information about the 
                    new Google Entry. 
            """
            
            entry = gdata.calendar.data.CalendarEntry()
            
            entry = self._local_to_gdata(local_object, entry)
            
            new_entry = backend.service.calendar_client.InsertCalendar(entry)
            
            identity = self.new_identity()
            identity.type = 'Calendar'
            identity.identity = self.json_links(new_entry)
            
            return identity
        
        def update(self, backend, gdata_object, local_object):
            """
            Update an existing object in Google with data from a local object.
            
            @param backend: The Google Backend.
            @param gdata_object: The existing gdata.contacts.data.CalendarEntry. 
            @param local_object: An objects.Calendar instance.
            """
            
            updated_entry = self._local_to_gdata(local_object, gdata_object)
            
            backend.service.calendar_client.Update(updated_entry)
        
        def delete(self, backend, gdata_object):
            """
            Delete an existing object from the Google Services.
            
            @param backend: The Google Backend.
            @param gdata_object: The existing gdata.contacts.data.CalendarEntry.
            """
            
            backend.calendar_client.Delete(gdata_object)
    
    class CalendarEventEntryAdapter(Adapter):
        def _local_to_gdata(self, local_object, gdata_object):
            """
            Update a GData instance with data from a local instance.
            
            @param local_object: An objects.Event instance.
            @param gdata_object: An gdata.contacts.data.CalendarEventEntry instance.
            
            @return The updated gdata_object.
            """
            
            #-----------------------------------------------------------------------
            # Event: title
            #-----------------------------------------------------------------------
            if local_object.title:
                if gdata_object.title:
                    gdata_object.title.text = local_object.title
                else:
                    gdata_object.title = atom.data.Title(text=local_object.title)
            
            #-----------------------------------------------------------------------
            # Event: title
            #-----------------------------------------------------------------------
            if local_object.description:
                if gdata_object.content:
                    gdata_object.content.text = local_object.description
                else:
                    gdata_object.content = atom.data.Content(text=local_object.description)
            
            #-----------------------------------------------------------------------
            # Event: where
            #-----------------------------------------------------------------------
            if len(gdata_object.where) > 0:
                # TODO: bad implementation, unclear specification from google
                # TODO: assume where always contains only one element with index 0
                gdata_object.where[0].value = local_object.location
                
            else:
                where = gdata.calendar.data.CalendarWhere(
                    value=local_object.location
                )
                
                gdata_object.where.append(where)
            
            #-----------------------------------------------------------------------
            # Event: when
            #-----------------------------------------------------------------------
            if self.hastime(local_object.start) and self.hastime(local_object.end):
                date_format = self.date_format_time
            elif not self.hastime(local_object.start) and not self.hastime(local_object.end):
                date_format = self.date_format_allday
            else:
                raise ValueError('start/end date: mixing of datetime and date is not allowed. start={0}, end={1}'.format(local_object.start, local_object.end))
            
            start = local_object.start
            
            # Google API workaround
            # when creating an event with start = x and end = y, 
            # the created event ends at y-1
            if local_object.start == local_object.end:
                end = local_object.end
            else:
                delta = datetime.timedelta(1)
                end = local_object.end + delta
            
            start_time = start.strftime(date_format)
            end_time = end.strftime(date_format)
            
            if len(gdata_object.when) > 0:
                # TODO: bad implementation, missing docs from google
                # TODO: assume when always contains only one element with index 0
                when = gdata_object.when[0]
                
                when.start = start_time
                when.end = end_time
            else:
                when = gdata.calendar.data.When(
                    start=start_time, 
                    end=end_time
                )
                
                gdata_object.when.append(when)
            
            return gdata_object
        
        def _gdata_to_local(self, local_object, gdata_object):
            """
            Update a local instance with data from a GData instance.
            
            @param local_object: An objects.Contact instance.
            @param gdata_object: An gdata.contacts.data.CalendarEventEntry instance.
            
            @return The updated local_object.
            """
            
            #-------------------------------------------------------------------
            # Event: title
            #-------------------------------------------------------------------
            if gdata_object.title:
                local_object.title = gdata_object.title.text
            
            #-------------------------------------------------------------------
            # Event: description
            #-------------------------------------------------------------------
            if gdata_object.content:
                local_object.description = gdata_object.content.text
            
            #-------------------------------------------------------------------
            # Event: where
            #-------------------------------------------------------------------
            if len(gdata_object.where) > 0:
                local_object.location = gdata_object.where[0].value
            
            #-----------------------------------------------------------------------
            # Event: when
            #-----------------------------------------------------------------------
            if len(gdata_object.when) > 0:
                when = gdata_object.when[0]
                
                try:
                    start = time.strptime(when.start, self.date_format_time)
                    end = time.strptime(when.end, self.date_format_time)
                except ValueError:
                    try:
                        start = time.strptime(when.start, self.date_format_allday)
                        end = time.strptime(when.end, self.date_format_allday)
                    except ValueError:
                        start = None
                        end = None
                
                if start and end:
                    if start != end:
                        delta = datetime.timedelta(-1)
                        end -= delta
                    
                    local_object.start = start
                    local_object.end = end
            
            return local_object
        
        def insert(self, backend, local_object):
            """
            Insert a local object into the Google Service.
            
            @param backend: The Google Backend.
            @param local_object: An objects.Event instance.
            
            @return a DataStorePeerIdentity with information about the 
                    new Google Entry. 
            """
            
            entry = gdata.calendar.data.CalendarEventEntry()
            
            entry = self._local_to_gdata(local_object, entry)
            
            if local_object.calendar:
                calendar_identities = backend.datastore.find_identities(local_object.calendar)
            
                try:
                    google_identity = [identity for identity in calendar_identities if identity.backend == 'GoogleBackend'][0]
                    
                    links = json.loads(google_identity.identity)
                    
                    calendar_uri = backend.find_eventfeed_link(links)
                    
                except KeyError:
                    calendar_uri = None
            
            else:
                calendar_uri = None
            
            new_entry = backend.service.calendar_client.InsertEvent(entry, calendar_uri)
            
            identity = self.new_identity()
            identity.type = 'Event'
            identity.identity = self.json_links(new_entry)
            
            return identity
        
        def update(self, backend, gdata_object, local_object):
            """
            Update an existing object in Google with data from a local object.
            
            @param service: The Google API service.
            @param gdata_object: The existing gdata.contacts.data.CalendarEventEntry. 
            @param local_object: An objects.Contact instance.
            """
            
            updated_entry = self._local_to_gdata(local_object, gdata_object)
            
            backend.service.calendar_client.Update(updated_entry)
        
        def delete(self, backend, gdata_object):
            """
            Delete an existing object from the Google Services.
            
            @param backend: The Google Backend.
            @param gdata_object: The existing gdata.contacts.data.CalendarEventEntry.
            """
            
            backend.service.calendar_client.Delete(gdata_object)
    
    class ContactEntryAdapter(Adapter):
        def _local_to_gdata(self, local_object, gdata_object):
            """
            Update a GData instance with data from a local instance.
            
            @param local_object: An objects.Contact instance.
            @param gdata_object: An gdata.contacts.data.ContactEntry instance.
            
            @return The updated gdata_object.
            """
            
            if local_object.firstname:
                local = local_object.firstname
                remote = gdata_object.name
                
                if remote:
                    remote.given_name = local
                else:
                    remote = gdata.data.Name(
                        given_name=gdata.data.GivenName(text=local)
                    )
            
            if local_object.lastname:
                local = local_object.lastname
                remote = gdata_object.name
                
                if  remote:
                    remote.family_name = local
                else:
                    remote = gdata.data.Name(
                        family_name=gdata.data.FamilyName(text=local)
                    )
            
            if local_object.nickname:
                local = local_object.nickname
                remote = gdata_object.nickname
                
                if remote:
                    remote.text = local
                else:
                    remote = gdata.contacts.data.NickName(text=local)
            
            if local_object.birthday:
                local = local_object.birthday.strftime(self.date_format_allday)
                remote = gdata_object.birthday
                
                if remote:
                    remote.when = local
                else:
                    remote = gdata.contacts.data.Birthday(when=local)
            
            return gdata_object
        
        def _gdata_to_local(self, local_object, gdata_object):
            """
            Update a local instance with data from a GData instance.
            
            @param local_object: An objects.Contact instance.
            @param gdata_object: An gdata.contacts.data.ContactEntry instance.
            
            @return The updated local_object.
            """
            
            if gdata_object.name and gdata_object.name.given_name:
                local_object.firstname = gdata_object.name.given_name
            
            if gdata_object.name and gdata_object.name.family_name:
                local_object.lastname = gdata_object.name.family_name
            
            if gdata_object.nickname:
                local_object.nickname = gdata_object.nickname.text
            
            if gdata_object.birthday:
                local_object.birthday = time.strptime(
                    gdata_object.birthday.when,
                    self.date_format_allday
                )
            
            return gdata_object
        
        def insert(self, backend, local_object):
            """
            Insert a local object into the Google Service.
            
            @param backend: The Google Backend.
            @param local_object: An objects.Contact instance.
            
            @return a DataStorePeerIdentity with information about the 
                    new Google Entry. 
            """
            
            entry = gdata.contacts.data.ContactEntry()
            
            entry = self._local_to_gdata(local_object, entry)
            
            new_entry = backend.service.contacts_client.CreateContact(entry)
            
            identity = self.new_identity()
            identity.type = 'Contact'
            identity.identity = self.json_links(new_entry)
            
            return identity
        
        def update(self, backend, gdata_object, local_object):
            """
            Update an existing object in Google with data from a local object.
            
            @param backend: The Google Backend.
            @param gdata_object: The existing gdata.contacts.data.ContactEntry. 
            @param local_object: An objects.Contact instance.
            """
            
            updated_entry = self._local_to_gdata(local_object, gdata_object)
            
            backend.service.contacts_client.Update(updated_entry)
        
        def delete(self, backend, gdata_object):
            """
            Delete an existing object from the Google Services.
            
            @param backend: The Google Backend.
            @param gdata_object: The existing gdata.contacts.data.ContactEntry.
            """
            
            backend.service.contacts_client.Delete(gdata_object)
    
    def __init__(self, datastore, service):
        """
        Initialize the backend implementation.
        
        @param datastore: The datastore.
        @param service: An Google API service object which handles authentication
        """
        
        self.datastore = datastore
        self.service = service
        self.query = self.Query()
        self.adapters = {
            'Calendar' : self.CalendarEntryAdapter(),
            'Event' : self.CalendarEventEntryAdapter(),
            'Contact' : self.ContactEntryAdapter(),
        }
    
    def find_objects(self, query):
        """
        Find objects in the google backend using a query object.
        
        @param query_object: The query_object with search criteria.
        
        @return A list with matching objects. The List will be empty if
        nothing was found.
        """
        
        
        result = self.query.execute(self.service, query)
        
        return result
    
    def find_edit_link(self, links):
        """
        Returns the Google edit link from a CalendarEventEntry link list.
        """
        
        return links[self.LINK_EDIT]
    
    def find_eventfeed_link(self, links):
        """
        Returns the Google eventFeed link from a CalendarEventEntry link list.
        """
        
        return links[self.LINK_EVENTFEED]
    
    def insert_object(self, object):
        """
        insert a new data object.
        
        @param object: The object to insert.
        
        @return The identity of the remote object.
        """
        
        adapter = self.adapters[object.__class__.__name__]
        identity = adapter.insert(self, object)
        
        return identity
    
    def update_object(self, identity, object):
        """
        Update an existing object.
        
        @param identity: The object's peer identity.
        @param object: The new object data.
        """
        
        links = json.loads(identity.identity)
        
        query = self.datastore.get_query('event_by_id')
        query.id = self.find_edit_link(links)
        
        current_entry = self.find_objects(query)
        
        adapter = self.adapters[identity.type]
        adapter.update(self, current_entry, object)
   
    def delete_object(self, identity):
        """
        Delete an existing object.
        
        @param identity: The object's peer identity.
        """
        
        links = json.loads(identity.identity)
        
        query = self.datastore.get_query('event_by_id')
        query.id = self.find_edit_link(links)
        
        current_entry = self.find_objects(query)
        
        adapter = self.adapters[identity.type]
        adapter.delete(self, current_entry)
