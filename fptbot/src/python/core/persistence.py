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

@since Jan 08, 2011
@author Mario Steinhoff
"""

__version__ = '$Rev$'

import logging
import sqlite3
import gdata.calendar.client
import gdata.contacts.client

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from core import runlevel
from core import subsystem
from core.config import Config

# ------------------------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------------------------
class DatabaseError(Exception): pass

# ------------------------------------------------------------------------------
# Business Logic
# ------------------------------------------------------------------------------
class SqlitePersistence(subsystem.Subsystem):
    RUNLEVEL = runlevel.Runlevel(
        autoboot=True,
        minimum_start=runlevel.LOCAL_FILESYSTEM
    )
    
    """
    Provide sqlite persistence to all sub-systems.
    """
    
    class Mapping():
        def get_type(self):
            raise NotImplementedError
        
        def get_typename(self):
            raise NotImplementedError
        
        def adapt(self, value):
            raise NotImplementedError
        
        def convert(self, value):
            raise NotImplementedError

    type_mapping = []
    
    def __init__(self, bot, sqlite_file):
        """
        Create a new persistence instance.
        
        @param sqlite_file: The SQLite database.
        """
        subsystem.Subsystem.__init__(self, bot)
        
        self.sqlite_file = sqlite_file
        
        for clazz in self.type_mapping:
            object = clazz()
            sqlite3.register_adapter(object.type, object.adapt)
            sqlite3.register_converter(object.typename, callable)
    
    def start(self):
        """
        Open the sqlite connection.
        
        Implementation of Subsystem.start()
        """
        
        if not self.sqlite_file:
            raise KeyError('missing sql file')
        
        sqlite_file = self.bot.get_config_key(self.sqlite_file)
        
        self.connection = sqlite3.connect(sqlite_file)
        self.connection.row_factory = sqlite3.Row
        
        self._running()

    def stop(self):
        """
        Close the sqlite connection.
        
        Implementation of Subsystem.stop()
        """
        
        self.connection.close()
        
        self._halted()
    
    def get_connection(self):
        """
        Return the SQLite connection instance.
        """
        
        return self.connection
    
    def get_cursor(self):
        """
        Return a new SQLite cursor.
        """
        
        return self.connection.cursor()

class SqlAlchemyPersistence(subsystem.Subsystem):
    RUNLEVEL = runlevel.Runlevel(
        autoboot=True,
        minimum_start=runlevel.LOCAL_SERVICE
    )
    
    """
    Provide access to the SQLAlchemy ORM for all sub-systems.
    """
    
    Base = declarative_base()
    
    def __init__(self, bot, connect_string):
        """
        Create a new persistence instance.
        
        @param connect_string: The SQLAlchemy connect string.
        """
        subsystem.Subsystem.__init__(self, bot)
        
        self.connect_string = connect_string
        
        bot.get_logger('sqlalchemy.engine').setLevel(logging.INFO)
    
    def _start(self):
        """
        Create a SqlAlchemy session.
        
        Implementation of Subsystem.start()
        """
        
        if not self.connect_string:
            raise KeyError('missing connect string')
        
        connect_string = self.bot.get_config_key(self.connect_string)
        
        self.engine = create_engine(connect_string)
        self.sessionobj = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
        self.session = self.sessionobj()
        
        self._running()
        
    def _stop(self):
        """
        Close the SqlAlchemy session.
        
        Implementation of Subsystem.stop()
        """
        
        if self.session:
            self.session.close()
            
        self._halted()
    
    def get_session(self):
        """
        Create a new session instance.
        
        @return sqlalchemy.orm.session.Session
        """
        
        return self.session

class GoogleApiService(subsystem.Subsystem):
    RUNLEVEL = runlevel.Runlevel(
        autoboot=True,
        minimum_start=runlevel.NETWORK_SERVICE
    )
    
    """
    Initialize the Google client API and handle all authentication logic.
    """
    
    # TODO: externalize
    source = 'foption-bot-v1'
    
    def __init__(self, bot):
        subsystem.Subsystem.__init__(self, bot)
        
        self.bot.register_config(GoogleApiServiceConfig)
        
        self.calendar_client = None
        self.contacts_client = None
        
    def _start(self):
        """
        Register a new session at the Google API endpoint.
        
        Implementation of Subsystem.start()
        """
        
        config = self.bot.get_config(GoogleApiServiceConfig.identifier)
        
        self.calendar_client = gdata.calendar.client.CalendarClient(
            source=self.source
        )
        
        self.calendar_client.ClientLogin(
            config.get('gdata-username'),
            config.get('gdata-password'),
            self.calendar_client.source
        )

        self.contacts_client = gdata.contacts.client.ContactsClient(
            source=self.source
        )
        
        self.contacts_client.ClientLogin(
            config.get('gdata-username'),
            config.get('gdata-password'),
            self.contacts_client.source
        )
        
        self._running()
    
    def _stop(self):
        """
        Currently does nothing, as the Google client API does not require 
        to close, shutdown or release any resources.
        
        Implementation of Subsystem.stop()
        """
        
        self._halted()
    
    def get_calendar_client(self):
        return self.calendar_client
    
    def get_contacts_client(self):
        return self.contacts_client

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------
class GoogleApiServiceConfig(Config):
    identifier = 'services.google.api'
    
    def valid_keys(self):
        return [
            'gdata-username',
            'gdata-password',
            'gdata-tokens',
            'gdata-client-id',
            'gdata-client-secret'
        ]
    
    def default_values(self):
        return {
            'gdata-username' : '',
            'gdata-password' : '',
            'gdata-tokens' : {},
            'gdata-client-id' : '',
            'gdata-client-secret' : ''

        }

