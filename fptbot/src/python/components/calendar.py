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
class InvalidEventId(CalendarComponentError): pass

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
        
        self.datastore = DataStore(DataStoreOneWaySync)
        
        # Setup primary backend
        sqlite = SqlAlchemyBackend(self.bot.get_subsystem('local-persistence'))
        self.datastore.set_primary_backend(sqlite)
        
        # Setup secondary backend
        google = GoogleBackend(self.bot.get_subsystem('google-api-service'))
        self.datastore.register_secondary_backend(google)
        
        self._running()
        
    def _stop(self):
        """
        Shutdown the component and background services (DataStore, Backends).
        
        Implementation of Subsystem.stop()
        """
        self.datastore = None
        
        self._halted()
    
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
        
        result = self.datastore.insert_object(
            CalendarComponent.__class__.__name__, 
            event
        )
        
        return result
        
    def update_object(self, event):
        if event == None:
            return None
        
        if event.id == None:
            raise ValueError('event.id must be given')
        
        try:
            self.datastore.update_object(
                CalendarComponent.__class__.__name__, 
                event
            )
        
        except KeyError:
            raise InvalidEventId
        
    def delete_event(self, eventId):
        if eventId == None:
            return
        
        try:
            event = self.find_event_by_id(eventId)
            
            self.datastore.delete_object(
                CalendarComponent.__class__.__name__, 
                event
            )
        
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
        
        @param source: Where the object comes from.
        @param object: The object to be inserted.
        """
        raise NotImplementedError
    
    def update(self, source, object):
        """
        Handle update algorithm.
        
        @param source: Where the object comes from.
        @param object: The object to be updated.
        """
        raise NotImplementedError
    
    def delete(self, source, object):
        """
        Handle delete algorithm.
        
        @param source: Where the object comes frome.
        @param object: The object to be deleted.
        """
        raise NotImplementedError

class DataStoreOneWaySync(DataStoreSyncStrategy):
    def insert(self, source, object):
        context = self.datastore
        primary = context.primary_backend
        secondaries = context.secondary_backends
        
        storedObject = primary.insert_object(context, object)
        
        for secondary in secondaries:
            datastore_identity = secondary.insert_object(context, object)
            
            primary.create_peer_identity(
                context,
                storedObject,
                datastore_identity
            )
            
        return storedObject
        
    def update(self, source, object):
        context = self.datastore
        primary = context.primary_backend
        secondaries = context.secondary_backends
        
        primary.update_object(context, object)
        
        identities = {}
        
        for identity in primary.get_peer_identities(context, object):
            identities[identity.backend.name] = DataStorePeerIdentity(
                backend=identity.backend.name,
                type=identity.data_type,
                identity=identity.identity
            )
        
        for secondary in secondaries:
            secondary.update_object(
                context,
                object,
                identities[secondary.__class__.__name__]
            )
            
    def delete(self, source, object):
        pass

class DataStoreTwoWaySync(DataStoreSyncStrategy):
    def insert(self, source, object):
        return object
    def update(self, source, object):
        pass
    def delete(self, source, object):
        pass

class SqlAlchemyBackend(object):
    """
    Backend implementation using the SQLAlchemy ORM layer.
    """
    
    def __init__(self, persistence):
        """
        Initialize the sqlalchemy backend.
        
        @param persistence: The bot persistence.
        """
        
        self.session = persistence.get_session()
    
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

    
    def create_peer_identity(self, context, object, datastore_identity):
        """
        Create a mapping between a local object and an remote peer identity.
        
        @param context: The datastore context.
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
        
        self.session.commit()
    
    def get_peer_identities(self, context, object):
        """
        Retrieve a mapping for the given object.
        
        @param context: The datastore context.
        @param object: The local object.
        """
        
        dispatcher = {
            'Calendar': (CalendarPeerIdentity, CalendarPeerIdentity.calendar),
            'Event': (EventPeerIdentity, EventPeerIdentity.event),
            'Contact': (ContactPeerIdentity, ContactPeerIdentity.contact)
        }
        
        type = dispatcher[object.__class__.__name__]

        result = self.session.query(type[0]).filter(type[1] == object).all()
        
        return result

    
    def find_objects(self, context, query):
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
            result = self.session.query(Event).filter(Event.id == query.id).one()
            
            return result
        
        def find_events_at_date():
            
            result = self.session \
                   .query(Event) \
                   .filter(sqlalchemy.func.strftime('%Y-%m-%d', Event.start) <= query.date) \
                   .filter(sqlalchemy.func.strftime('%Y-%m-%d', Event.end) >= query.date) \
                   .all()
            
            return result
        
        dispatcher = {
           'all_calendars': find_all_calendars,
           'event_by_id': find_event_by_id,
           'events_at_date': find_events_at_date
        }
        
        request = query.get_name()
        
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
        
        return object
    
    def update_object(self, context, object):
        """
        Update an existing object.
        
        @param context: The datastore context.
        @param object: The object to update.
        """
        
        # TODO this is really ugly, as the whole session gets written to
        # TODO disk as opposed to the method name.
        # TODO need find a way to save only a specific object
        # TODO but should work anyway because when the session starts,
        # TODO there shouldnt be any objects pending.
        self.session.commit()
    
    def delete_object(self, context, object):
        """
        Delete an existing object.
        
        @param context: The datastore context.
        @param object: The object to delete.
        """
        
        self.session.delete(object)

class GoogleBackend(object):
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
    
    def hastime(self, object):
        """
        Check if the given datetime object contains time.
        
        TODO: this implementation is not optimal as an intentional 
        TODO: date at 00:00:00 produces a false positive result.
        
        @param object: The datetime object.
        """
        return (object.hour != 0 or object.minute != 0 or object.second != 0)
    
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
    
    def find_objects(self, context, query):
        """
        Find objects in the primary backend using a query object.
        
        @param context: The datastore context.
        @param query_object: The query_object with search criteria.
        
        @return A list with matching objects. The List will be empty if
        nothing was found.
        """
        
        def event_by_id():
            return self.service.calendar_client.get_event_entry(uri=query.id)
        
        dispatcher = {
            'event_by_id' : event_by_id
        }
        
        request = query.get_name()
        
        result = dispatcher[request]()
        
        return result
    
    def insert_object(self, context, object):
        """
        insert a new data object.
        
        @param context: The datastore context.
        @param object: The object to insert.
        
        @return The identity of the remote object.
        """
        
        identity = DataStorePeerIdentity()
        identity.backend = self.__class__.__name__
        
        def calendar():
            pass
        
        def event():
            entry = gdata.calendar.data.CalendarEventEntry()
            
            entry = self._event_to_gdata(object, entry)
            
            """ TODO catch errors """
            new_entry = self.service.calendar_client.InsertEvent(entry)
            
            identity.type = 'Event'
            identity.identity = new_entry.GetEditLink().href
            
        def contact():
            pass
        
        dispatcher = {
            'Calendar' : calendar,
            'Event' : event,
            'Contact' : contact
        }
        
        dispatcher[object.__class__.__name__]()
        
        return identity
    
    def update_object(self, context, object, identity):
        """
        Update an existing object.
        
        @param context: The datastore context.
        @param object: The object to update.
        @param identity: The object's peer identity.
        """
        
        def calendar():
            pass
        
        def event():
            query = context.get_query('event_by_id')
            query.id = identity.identity
            
            current_entry = self.find_objects(context, query)
            
            updated_entry = self._event_to_gdata(object, current_entry)
            
            """ TODO catch errors """
            self.service.calendar_client.Update(updated_entry)
            
        def contact():
            pass
        
        dispatcher = {
            'Calendar' : calendar,
            'Event' : event,
            'Contact' : contact
        }
        
        dispatcher[object.__class__.__name__]()
    
    def delete_object(self, context, object):
        """
        Delete an existing object.
        
        @param context: The datastore context.
        @param object: The object to delete.
        """
        
        print "delete object"
        print object
    

class FacebookBackend(object):
    """
    Backend implementation using the Facebook API.
    """
    
    pass

