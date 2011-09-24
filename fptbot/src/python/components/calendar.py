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

import sqlalchemy.orm.exc
import atom.data
import gdata.calendar.data

from core import runlevel
from core.component import Component, ComponentError
from objects.calendar import Calendar, Event, Backend,\
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
        minimum_start=runlevel.LOCAL_SERVICE
    )
    
    def __init__(self, bot):
        Component.__init__(self, bot)
        
        self.logger = self.bot.get_logger('components.calendar')
        
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
        if object == None:
            raise ValueError('object must be given')
        
        if object.id != None:
            raise ValueError('object.id must be None')
        
        result = self.datastore.insert_object(
            self.__class__.__name__,
            object
        )
        
        return result
        
    def update_object(self, object):
        if object == None:
            raise ValueError('object must be given')
        
        if object.id == None:
            raise ValueError('object.id must be given')
        
        try:
            self.datastore.update_object(
                self.__class__.__name__,
                object
            )
        
        except KeyError:
            raise InvalidObjectId
        
    def delete_object(self, object):
        if object == None:
            raise ValueError('object must be given')
        
        if object.id == None:
            raise ValueError('object.id must be given')
        
        try:
            self.datastore.delete_object(
                self.__class__.__name__,
                object
            )
        
        except KeyError:
            raise InvalidObjectId
    
    # --------------------------------------------------------------------------
    # Component methods: calendars
    # --------------------------------------------------------------------------
    def find_all_calendars(self):
        query = self.datastore.get_query('all_calendars')
        
        return self.datastore.find_objects(query)
    
    def find_calendar_by_id(self, id):
        if id == None:
            return None
        
        query = self.datastore.get_query('calendar_by_id')
        query.id = id
        
        return self.datastore.find_objects(query)
    
    def find_calendars_by_string(self, string):
        if string == None:
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
        if id == None:
            return None
        
        query = self.datastore.get_query('event_by_id')
        query.id = id
        
        return self.datastore.find_objects(query)
    
    def find_events_by_string(self, string):
        if string == None:
            return None
        
        query = self.datastore.get_query('events_by_string')
        query.string = string
        
        return self.datastore.find_objects(query)
    
    def find_events_at_date(self, date):
        if date == None:
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
        if id == None:
            return None
        
        query = self.datastore.get_query('contacts_by_id')
        query.id = id
        
        return self.datastore.find_objects(query)
    
    def find_contacts_by_string(self, string):
        if string == None:
            return None
        
        query = self.datastore.get_query('contacts_by_string')
        query.string = string
        
        return self.datastore.find_objects(query)

# ------------------------------------------------------------------------------
# Data management
# ------------------------------------------------------------------------------
class DataStoreError(CalendarComponentError): pass
class ObjectNotFound(DataStoreError): pass
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
        self.secondary_backends = []
        self.strategy = strategy(self)
    
    def set_primary_backend(self, backend):
        """
        Set a backend object as the primary backend.
        
        @param backend: The backend instance.
        
        @return Nothing
        """
        
        self.primary_backend = backend
    
    def register_secondary_backend(self, backend):
        """
        Register a backend object as a secondary backend.
        
        @param backend: The backend instance.
        
        @return Nothing
        """
        
        self.secondary_backends.append(backend)
    
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
        
        primary.begin_transaction()
        
        stored_object = primary.insert_object(object)
        
        for secondary in secondaries:
            datastore_identity = secondary.insert_object(object)
            
            primary.create_peer_identity(
                stored_object,
                datastore_identity
            )
        
        primary.commit_transaction()
            
        return stored_object
        
    def update(self, source, object):
        """
        Update an existing object.
        
        @param source: The object source' classname.
        @param source: The local object.
        """
        
        primary = self.datastore.primary_backend
        secondaries = self.datastore.secondary_backends
        
        primary.begin_transaction()
        
        primary.update_object(object)
        
        datastore_identities = {}
        
        for identity in object.identities:
            datastore_identities[identity.backend.name] = DataStorePeerIdentity(
                backend=identity.backend.name,
                type=identity.data_type,
                identity=identity.identity
            )
        
        for secondary in secondaries:
            secondary.update_object(
                datastore_identities[secondary.__class__.__name__],
                object
            )
        
        primary.commit_transaction()
    
    def delete(self, source, object):
        """
        Delete an existing object.
        
        @param source: The object source' classname.
        @param source: The local object.
        """
        
        primary = self.datastore.primary_backend
        secondaries = self.datastore.secondary_backends
        
        primary.begin_transaction()
        
        datastore_identities = {}
        
        for identity in object.identities:
            datastore_identities[identity.backend.name] = DataStorePeerIdentity(
                backend=identity.backend.name,
                type=identity.data_type,
                identity=identity.identity
            )
        
        for secondary in secondaries:
            secondary.delete_object(
                datastore_identities[secondary.__class__.__name__]
            )
            
        primary.delete_object(object)
        
        primary.commit_transaction()

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
        def all_calendars(self, session, query):
            result = session.query(Calendar).filter(Calendar.isDeleted == False).all()
            
            return result
        
        def calendar_by_id(self, session, query):
            raise ObjectNotFound
        
        def calendars_by_string(self, session, query):
            return []
        
        def all_events(self, session, query):
            return []
        
        def event_by_id(self, session, query):
            try:
                result = session \
                       .query(Event) \
                       .filter(Event.id == query.id) \
                       .filter(Event.isDeleted == False) \
                       .one()
                
            except sqlalchemy.orm.exc.NoResultFound:
                raise ObjectNotFound
            
            return result
        
        def events_by_string(self, session, query):
            return []
        
        def events_at_date(self, session, query):
            
            result = session \
                   .query(Event) \
                   .filter(sqlalchemy.func.strftime('%Y-%m-%d', Event.start) <= query.date) \
                   .filter(sqlalchemy.func.strftime('%Y-%m-%d', Event.end) >= query.date) \
                   .filter(Event.isDeleted == False) \
                   .all()
            
            return result
        
        def all_contacts(self, session, query):
            return []
        
        def contact_by_id(self, session, query):
            raise ObjectNotFound
        
        def contacts_by_string(self, session, query):
            return []
    
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
        Commit the current transaction.
        """
        
        self.session.commit()
    
    def request_backend(self, name):
        """
        Request a backend object from the database.
        When the object was not found, a new object will be created.
        
        @param name: The name of the backend.
        
        @return A Backend instance.
        """
        
        try:
            backend = self.session \
                    .query(Backend) \
                    .filter(Backend.name == name) \
                    .one()
                    
        except sqlalchemy.orm.exc.NoResultFound:
            backend = Backend(name=name)
            
            self.session.add(backend)
        
        return backend
    
    def create_peer_identity(self, object, datastore_identity):
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
        object.deletedOn = datetime.datetime.now()

class GoogleBackend(DataStoreBackend):
    """
    Backend implementation using Google's GData API.
    """
    
    class Query(DataStoreBackend.Query):
        def calendar_by_id(self, service, query):
            return service.calendar_client.get_calendar_entry(uri=query.id)
        
        def event_by_id(self, service, query):
            return service.calendar_client.get_event_entry(uri=query.id)
        
        def contact_by_id(self, service, query):
            return service.contacts_client.get_contact(uri=query.id)
    
    class Adapter(DataStoreBackend.Adapter):
        date_format_time = '%Y-%m-%dT%H:%M:%S.000Z'
        date_format_allday = '%Y-%m-%d'
    
        def _hastime(self, object):
            """
            Check if the given datetime object contains time.
            
            TODO: this implementation is not optimal as an intentional 
            TODO: date at 00:00:00 produces a false positive result.
            
            @param object: The datetime object.
            """
            
            if hasattr(object, 'hour') and hasattr(object, 'minute') and hasattr(object, 'second'):
                return (object.hour != 0 or object.minute != 0 or object.second != 0)
            
            return False
        
        def _event_to_gdata(self, local_object, gdata_object):
            """
            Copy data from a local event object to a gdata event object.
            
            @param local_object: The local event object.
            @param gdata_object: The gdata event object.
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
                where = gdata_object.where[0]
                where.value = local_object.location
                
            else:
                where = gdata.calendar.data.CalendarWhere(
                    value=local_object.location
                )
                
                gdata_object.where.append(where)
            
            #-----------------------------------------------------------------------
            # Event: when
            #-----------------------------------------------------------------------
            if self._hastime(local_object.start) and self._hastime(local_object.end):
                date_format = self.date_format_time
            elif not self._hastime(local_object.start) and not self._hastime(local_object.end):
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
    
        def new_identity(self):
            identity = DataStorePeerIdentity()
            identity.backend = 'GoogleBackend'
            
            return identity
    
    class CalendarAdapter(Adapter):
        def insert(self, service, object):
            pass
        
        def update(self, service, identity, object):
            pass
        
        def delete(self, service, identity):
            pass
    
    class EventAdapter(Adapter):
        def insert(self, service, object):
            entry = gdata.calendar.data.CalendarEventEntry()
            
            entry = self._event_to_gdata(object, entry)
            
            """ TODO catch errors """
            new_entry = service.calendar_client.InsertEvent(entry)
            
            identity = self.new_identity()
            identity.type = 'Event'
            identity.identity = new_entry.GetEditLink().href
            
            return identity
        
        def update(self, service, gdata_entry, object):
            updated_entry = self._event_to_gdata(object, gdata_entry)
            
            """ TODO catch errors """
            service.calendar_client.Update(updated_entry)
        
        def delete(self, service, gdata_entry):
            """ TODO catch errors """
            service.calendar_client.Delete(gdata_entry)
    
    class ContactAdapter(Adapter):
        def insert(self, service, object):
            pass
        
        def update(self, service, identity, object):
            pass
        
        def delete(self, service, identity):
            pass
    
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
            'Calendar' : self.CalendarAdapter(),
            'Event' : self.EventAdapter(),
            'Contact' : self.ContactAdapter(),
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
    
    def insert_object(self, object):
        """
        insert a new data object.
        
        @param object: The object to insert.
        
        @return The identity of the remote object.
        """
        
        adapter = self.adapters[object.__class__.__name__]
        identity = adapter.insert(self.service, object)
        
        return identity
    
    def update_object(self, identity, object):
        """
        Update an existing object.
        
        @param identity: The object's peer identity.
        @param object: The new object data.
        """
        
        query = self.datastore.get_query('event_by_id')
        query.id = identity.identity
        
        current_entry = self.find_objects(query)
        
        adapter = self.adapters[identity.type]
        adapter.update(self.service, current_entry, object)
   
    def delete_object(self, identity):
        """
        Delete an existing object.
        
        @param identity: The object's peer identity.
        """
        
        query = self.datastore.get_query('event_by_id')
        query.id = identity.identity
        
        current_entry = self.find_objects(query)
        
        adapter = self.adapters[identity.type]
        adapter.delete(self.service, current_entry)
