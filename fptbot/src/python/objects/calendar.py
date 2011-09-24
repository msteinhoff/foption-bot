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

@since Apr 26, 2011
@author Mario Steinhoff
"""

__version__ = '$Rev$'

from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Text
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship, backref

from core.persistence import SqlAlchemyPersistence

#-------------------------------------------------------------------------------
# Calendar
#-------------------------------------------------------------------------------
class Calendar(SqlAlchemyPersistence.Base):
    """
    Represent a calendar for the calendar component.
    """
    
    AUTO = 1
    MANUAL = 2
    
    __tablename__ = 'calendars'
    
    # DDL
    id = Column(Integer, primary_key=True)
    isDeleted = Column(Boolean, default=False)
    deletedOn = Column(DateTime, nullable=True)
    
    name = Column(String(255))
    type = Column(Integer)
    
    def __repr__(self):
        return '<Calendar(id={0},name={1}|type={2})>'.format(
            self.id, 
            self.name, 
            self.type
        )

class Event(SqlAlchemyPersistence.Base):
    """
    Represent an event for the calendar component.
    """
    
    __tablename__ = 'events'
    
    # DDL
    id = Column(Integer, primary_key=True)
    isDeleted = Column(Boolean, default=False)
    deletedOn = Column(DateTime, nullable=True)
    
    calendar_id = Column(Integer, ForeignKey('calendars.id'))
    etag = Column(String(255), nullable=True)
    start = Column(DateTime)
    end = Column(DateTime)
    allday = Column(Boolean, default=False)
    title = Column(String(255))
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    
    # ORM
    calendar = relationship('Calendar', backref=backref('events'), order_by=id)
    
    def __repr__(self):
        return '<Event(id={0}|calendar={1}|etag={2}|start={3}|end={4}|title={5})>'.format(
            self.id, 
            self.calendar, 
            self.etag, 
            self.start, 
            self.end, 
            self.title
        )

class Contact(SqlAlchemyPersistence.Base):
    """
    Represent a contact for the calendar component.
    
    SQLAlchemy mapped class.
    """
    
    __tablename__ = 'contacts'
    
    # DDL
    id = Column(Integer, primary_key=True)
    isDeleted = Column(Boolean, default=False)
    deletedOn = Column(DateTime, nullable=True)

    firstname = Column(String(64), nullable=True)
    lastname = Column(String(64), nullable=True)
    nickname = Column(String(32))
    birthday = Column(Date)
    
    def __repr__(self):
        return '<Contact(id={0}|firstname={1}|lastname={2}|nickname={3}|birthday={4})>'.format(
            self.id, 
            self.firstname, 
            self.lastname, 
            self.nickname, 
            self.birthday
        )

#-------------------------------------------------------------------------------
# Backend mapping
#-------------------------------------------------------------------------------

class Backend(SqlAlchemyPersistence.Base):
    """
    Represents a secondary backend.
    """
    
    __tablename__ = 'backends'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(64))

class BackendPeerIdentity(SqlAlchemyPersistence.Base):
    """
    Represent a remote (peer) identity for a locally stored object.
    
    The class structure is as the following:
    + BackendPeerIdentity
    +-- CalendarPeerIdentity
    +-- EventPeerIdentity
    +-- ContactPeerIdentity
    """
    __tablename__ = 'backend_identity'
    
    identity = Column(String(255), primary_key=True)
    backend_id = Column(Integer, ForeignKey('backends.id'))
    data_type = Column(String(64))
    
    backend = relationship('Backend')
    
    __mapper_args__ = {
       'polymorphic_on': data_type
   }

class CalendarPeerIdentity(BackendPeerIdentity):
    __mapper_args__ = {
       'polymorphic_identity': 'Calendar'
    }

    calendar_id = Column(Integer, ForeignKey('calendars.id'))
    calendar = relationship('Calendar', backref=backref('identities', order_by=BackendPeerIdentity.backend_id, cascade="all, delete-orphan"))
    

class EventPeerIdentity(BackendPeerIdentity):
    __mapper_args__ = {
       'polymorphic_identity': 'Event'
    }

    event_id = Column(Integer, ForeignKey('events.id'))
    event = relationship('Event', backref=backref('identities', order_by=BackendPeerIdentity.backend_id))

class ContactPeerIdentity(BackendPeerIdentity):
    __mapper_args__ = {
       'polymorphic_identity': 'Contact'
    }

    contact_id = Column(Integer, ForeignKey('contacts.id'))
    contact = relationship('Contact', backref=backref('identities', order_by=BackendPeerIdentity.backend_id))


#-------------------------------------------------------------------------------
# Auditing
#-------------------------------------------------------------------------------

class AuditEntry(SqlAlchemyPersistence.Base):
    """
    Represent an audit entry for the calendar component.
    
    SQLAlchemy mapped class.
    """
    
    __tablename__ = 'auditlog'

    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    principal = Column(String(128))
    action = Column(String(32))
    data_type = Column(String(255))
    data_before = Column(Text)
    data_after = Column(Text)
    
    __mapper_args__ = {
       'polymorphic_on': data_type
   }
    
    def __repr__(self):
        return '<AuditEntry(id={0}|datetime={1}|principal={2}|action={3}|datatype={4})>'.format(
            self.id, 
            self.datetime, 
            self.principal, 
            self.action, 
            self.datatype
        )

class CalendarAuditEntry(AuditEntry):
    __mapper_args__ = {
       'polymorphic_identity': 'calendar'
    }

class EventAuditEntry(AuditEntry):
    __mapper_args__ = {
       'polymorphic_identity': 'event'
    }

class ContactAuditEntry(AuditEntry):
    __mapper_args__ = {
       'polymorphic_identity': 'contact'
    }
