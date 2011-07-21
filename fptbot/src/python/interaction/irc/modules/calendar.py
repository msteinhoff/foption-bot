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

@since Aug, 05 2010
@author Rack Rackowitsch
@author Mario Steinhoff
"""

__version__ = '$Rev$'

import re

from datetime import date

from core.constants import TIME_MINUTE
from core.config import Config
from objects.calendar import Event

from components.calendar import InvalidEventId
from interaction.irc.module import InteractiveModule, InteractiveModuleCommand, InteractiveModuleReply, ModuleError, Location

#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------
REGEX_DATE = re.compile('^(\d{1,2})\.(\d{1,2})\.(\d{4})$')

#-------------------------------------------------------------------------------
# Exceptions
#-------------------------------------------------------------------------------
class CalendarModuleError(ModuleError): pass
class EventError(CalendarModuleError): pass
class EventNotFound(EventError): pass
class NoEventsFound(EventError): pass
class AmbiguousEventsFound(EventError): pass
class DateError(CalendarModuleError): pass
class DateFormatInvalid(DateError): pass
class DateRangeInvalid(DateError): pass

#-------------------------------------------------------------------------------
# Business Logic
#-------------------------------------------------------------------------------
class Calendar(InteractiveModule): 
    """
    This module provides calendaring functions.
    """
    
    #---------------------------------------------------------------------------
    # Module implementation
    #---------------------------------------------------------------------------
    def initialize(self):
        bot = self.client.bot;
        
        bot.register_config(CalenderConfig)
        
        self.logger = bot.get_logger('interaction.irc.calendar')
        self.config = bot.get_config('interaction.irc.calendar')
        self.component = bot.get_component('calendar');
    
    def start(self):
        self.start_daily_timer(self.config.get('reminderInterval'), self._display_reminder)
    
    def stop(self):
        self.cancel_timer()
    
    #---------------------------------------------------------------------------
    # InteractiveModule implementation
    #---------------------------------------------------------------------------
    def module_identifier(self):
        return 'Kalender'
    
    def init_commands(self):
        return [
            InteractiveModuleCommand(
                 keyword='kalender',
                 callback=self.display_calendar_address,
                 syntaxhint=''
            ),
            InteractiveModuleCommand(
                 keyword='listtoday',
                 callback=self.display_events_today,
                 syntaxhint=''
            ),
            InteractiveModuleCommand(
                 keyword='listdeleted',
                 callback=self.display_deleted_objects,
                 pattern=r'^(.*)$',
                 syntaxhint='[event|contact]'
            ),
            InteractiveModuleCommand(
                 keyword='restore',
                 callback=self.restore_deleted_object,
                 pattern=r'^[\d]+$',
                 syntaxhint='<id>'
            ),
            InteractiveModuleCommand(
                 keyword='syncdata',
                 callback=self.sync_data,
                 pattern=r'^(.+)$',
                 syntaxhint='google'),
            
            InteractiveModuleCommand(
                 keyword='addevent',
                 callback=self.insert_event,
                 pattern=r'^(\d{1,2}\.\d{1,2}\.\d{4}|\d{1,2}\.\d{1,2}\.\d{4}-\d{1,2}\.\d{1,2}\.\d{4})\s(.+)$',
                 syntaxhint='<datumvon>[-datumbis] <beschreibung>'
            ),
            InteractiveModuleCommand(
                 keyword='editevent',
                 callback=self.change_event,
                 pattern=r'^[\d]+\s(.+)\s(.+)$',
                 syntaxhint='<id> <start|ende|titel|beschreibung|ort> <wert>'
            ),
            InteractiveModuleCommand(
                 keyword='delevent',
                 callback=self.delete_event,
                 pattern=r'^([\d]+|\d{1,2}\.\d{1,2}\.\d{4})$',
                 syntaxhint='<id|datum>'
            ),
            InteractiveModuleCommand(
                 keyword='searchevent',
                 callback=self.search_event,
                 pattern=r'^(.+)$',
                 syntaxhint='<text>'
            ),
            InteractiveModuleCommand(
                 keyword='topicevent',
                 callback=self.topic_event,
                 pattern=r'^[\d]+$',
                 syntaxhint='<id>'
            ),
            
            InteractiveModuleCommand(
                 keyword='addcontact',
                 callback=self.insert_contact,
                 pattern=r'^(.+)\s(\d{1,2}\.\d{1,2}\.\d{4})$',
                 syntaxhint='<nickname> <geburtsdatum>'
            ),
            InteractiveModuleCommand(
                 keyword='editcontact',
                 callback=self.change_contact,
                 pattern=r'^[\d]+\s(.+)\s(.+)$',
                 syntaxhint='<id> <vorname|nachname|nickname|geburtsdatum> <wert>'
            ),
            InteractiveModuleCommand(
                 keyword='delcontact',
                 callback=self.delete_contact,
                 pattern=r'^([\d]+|(.+))$',
                 syntaxhint='<id>'
            ),
            InteractiveModuleCommand(
                 keyword='searchcontact',
                 callback=self.search_contact,
                 pattern=r'^(.+)$',
                 syntaxhint='<text>'
            )
        ]
    
    #---------------------------------------------------------------------------
    # Internal module commands
    #---------------------------------------------------------------------------
    def _get_date(self, date_string):
        """
        Check if the input_string contains a valid date.
        
        The input string is first converted using REGEX_DATE and then
        checked.
        
        @param date_string: The input string. See REGEX_DATE for the format.
        
        @return A date object.
        
        @raise DateFormatInvalid If no properly formatted date was given.
        @raise DateRangeInvalid  If the date values are out of range.
        """
        
        matchlist = REGEX_DATE.search(date_string)
        
        if not matchlist:
            raise DateFormatInvalid
        
        date_tokens = matchlist.group(1, 2, 3)
        
        try:
            return date(int(date_tokens[2]),int(date_tokens[1]),int(date_tokens[0]))
            
        except ValueError as e:
            raise DateRangeInvalid(e)
    
    def _display_reminder(self, date):
        """
        Timer callback function.
        """
        
        reply = self.display_events_by_date(None, Location.CHANNEL, None, [date])
        
        for channel in self.usermgmt.chanlist.get_channels().values():
            self.send_reply(channel, reply)
    
    #---------------------------------------------------------------------------
    # InteractiveModule commands - display
    #---------------------------------------------------------------------------
    def display_calendar_address(self, event, location, command, parameter):
        """
        Display the web calendar's address.
        """
        
        return InteractiveModuleReply().add_line(self.config.get('calendarUrl'))
    
    def display_events_today(self, event, location, command, parameter):
        """
        Display today's events, if any.
        """
        
        return self.display_events_by_date(event, location, command, [date.today()])
    
    def display_events_by_date(self, event, location, command, parameter):
        """
        Display events occuring at the given date.
        """
        
        reply = InteractiveModuleReply()
        
        date = parameter[0]
        
        try:
            calendar_events = self.component.find_events_by_date(date)
            
            if len(calendar_events) == 0:
                raise NoEventsFound
            
            for calendar_event in calendar_events:
                reply.add_line("ID {0}: {1}".format(calendar_event.id, calendar_event.title))
            
        except NoEventsFound:
            reply.add_line('Keine Termine gefunden.')
            
        return reply
    
    def display_deleted_objects(self, event, location, command, parameter):
        """
        """
        
        return InteractiveModuleReply().add_line('not implemented')
    
    def restore_deleted_object(self, event, location, command, parameter):
        """
        """
        
        return InteractiveModuleReply().add_line('not implemented')
    
    def sync_data(self, event, location, command, parameter):
        """
        """
        
        return InteractiveModuleReply().add_line('not implemented')
    
    #---------------------------------------------------------------------------
    # InteractiveModule commands - events
    #---------------------------------------------------------------------------
    def insert_event(self, event, location, command, parameter):
        """
        Create a new event.
        
        .addevent <startdate>[-<enddate>] title
        """
        
        reply = InteractiveModuleReply()
        
        date = parameter[0]
        title = parameter[1]
        
        try:
            if '-' not in date:
                dateFrom = self._get_date(date)
                dateTo = dateFrom
                
            else:
                dates = date.split('-')
                
                dateFrom = self._get_date(dates[0])
                dateTo = self._get_date(dates[1])
            
            event = Event(start=dateFrom, end=dateTo, title=title)
            event = self.component.insert_event(event)
            
            reply.add_line("Eintrag erfolgreich eingefügt! ID: {0}".format(event.id))
            
        except DateFormatInvalid:
            reply.add_line("Datum muss im Format [d]d.[m]m.yyyy sein. Bsp: 12.5.2010")
        
        except DateRangeInvalid as e:
            reply.add_line('Ungültiges Datum: {0}.'.format(e))
        
        return reply
    
    def change_event(self, event, location, command, parameter):
        """
        """
        
        return InteractiveModuleReply().add_line("not implemented")
    
    def delete_event(self, event, location, command, parameter):
        """
        .delevent [<id>|<datum>]
        """
        
        reply = InteractiveModuleReply()
        
        # when only one parameter is defined a string is returned
        id_or_date = parameter[0]
        
        try:
            try:
                date = self._get_date(id_or_date)
                
                #---------------------------------------------------------------
                # delete by date
                #---------------------------------------------------------------
                events = self.component.find_events_by_date(date)
                
                count = len(events)
                
                if count == 0:
                    raise NoEventsFound
                
                if count > 1:
                    raise AmbiguousEventsFound(events)
                
                eventId = events[0].id
            
            except DateFormatInvalid:
                #---------------------------------------------------------------
                # delete by id
                #---------------------------------------------------------------
                eventId = int(id_or_date)
                
            self.component.delete_event(eventId)
            
            reply.add_line("Done.")
            
        except InvalidEventId:
            reply.add_line("Kein Eintrag zu dieser ID gefunden.")
        
        except NoEventsFound:
            reply.add_line("Kein Eintrag zu diesem Datum gefunden.")
        
        except AmbiguousEventsFound as error:
            reply.add_line('Mehrere Einträge gefunden:')
            [reply.add_line("(ID={0}) {1}".format(event.id, event.title)) for event in error.message]
        
        return reply
    
    def search_event(self, event, location, command, parameter):
        """
        Search for an event
        
        .searchevent <text>
        """
        
        return InteractiveModuleReply().add_line("not implemented")
    
    def topic_event(self, event, location, command, parameter):
        """
        Post the given event to the current topic.
        .topicevent 
        
        TODO: implement
        """
        
        reply = InteractiveModuleReply()
        
        eventId = int(parameter[0])
        
        try:
            result = self.component.find_event_by_id(eventId)
            
            if result == None:
                raise EventNotFound
            
            reply.add_line('currently not implemented');
            
        except EventNotFound:
            reply.add_line('Kein Event mit ID {0} gefunden'.format(eventId))
            
        return reply
    
    #---------------------------------------------------------------------------
    # InteractiveModule commands - contacts
    #---------------------------------------------------------------------------
    def insert_contact(self, event, location, command, parameter):
        """
        """
        
        return InteractiveModuleReply().add_line("not implemented")
    
    def change_contact(self, event, location, command, parameter):
        """
        """
        
        return InteractiveModuleReply().add_line("not implemented")
    
    def delete_contact(self, event, location, command, parameter):
        """
        """
        
        return InteractiveModuleReply().add_line("not implemented")
    
    def search_contact(self, event, location, command, parameter):
        """
        """
        
        return InteractiveModuleReply().add_line("not implemented")


class CalenderConfig(Config):
    identifier = 'interaction.irc.calendar'
        
    def valid_keys(self):
        return [
            'reminderInterval',
            'calendarUrl'
        ]
    
    def default_values(self):
        return {
            'reminderInterval' : TIME_MINUTE * 5,
            'calendarUrl'      : ''
        }
