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

from hashlib import md5
from datetime import date, timedelta
from string import hexdigits

from core.constants import DIR_DB_CALENDAR, TIME_MINUTE
from core.config import Config
from persistence.sqlite import SQLitePersistence, DatabaseError
from interaction.irc.command import PrivmsgCmd
from interaction.irc.module import InteractiveModule, InteractiveModuleReply, ModuleError, Location, Role
from interaction.irc.modules.usermgmt import UserNotAuthed, UserNotAuthorized, UserInvalid, UserExists

"""-----------------------------------------------------------------------------
Constants
-----------------------------------------------------------------------------"""
CATEGORY_EVENT    = 'EVENT'
CATEGORY_BIRTHDAY = 'BIRTHDAY'
CATEGORY_HOLIDAY  = 'HOLIDAY'

REGEX_DATE = re.compile('^(\d{1,2})\.(\d{1,2})\.(\d{4})$')
REGEX_CATEGORY_DEFAULT = re.compile('(BIRTHDAY|EVENT|HOLIDAY)')

"""-----------------------------------------------------------------------------
Exceptions
-----------------------------------------------------------------------------"""
class CalendarError(ModuleError): pass
class EventError(CalendarError): pass
class EventNotFound(CalendarError): pass
class AmbiguousEventsFound(CalendarError): pass
class MultipleEventsNotPossible(EventError): pass
class DateError(CalendarError): pass
class DateFormatInvalid(DateError): pass
class DateRangeInvalid(DateError): pass
class CategoryError(CalendarError): pass
class CategoryInvalid(CategoryError): pass
class CategoryExists(CategoryError): pass
class CategoryUsed(CategoryError): pass
class ColorError(CalendarError): pass
class ColorInvalid(ColorError): pass

"""-----------------------------------------------------------------------------
Business Logic
-----------------------------------------------------------------------------"""
class Calendar(InteractiveModule): 
    """
    This module provides calendaring functions.
    """
    
    
    """-------------------------------------------------------------------------
    Configuration
    -------------------------------------------------------------------------"""
    class CalenderConfig(Config):
        def name(self):
            return 'interaction.irc.module.calendar'
            
        def valid_keys(self):
            return [
                'dbFile',
                'reminderInterval',
                'calendarUrl',
            ]
        
        def default_values(self):
            return {
                'dbFile'           : DIR_DB_CALENDAR,
                'reminderInterval' : TIME_MINUTE * 5,
                'calendarUrl'      : '',
            }
    
    """-------------------------------------------------------------------------
    InteractiveModule methods
    -------------------------------------------------------------------------"""
    def module_identifier(self):
        return 'Kalender'
    
    def initialize(self):
        self.config = self.CalendarConfig(self.client._bot.getPersistence())
        
        self.persistence = CalendarPersistence(self.config.get('dbFile'))
        
        self.start_daily_timer(self.config.get('reminderInterval'), self.display_reminder)
        
    def shutdown(self):
        self.cancel_timer()
    
    def init_commands(self):
        self.add_command('kalender',  None,       Location.BOTH, PrivmsgCmd, Role.USER, self.display_calendar_address)
        self.add_command('listtoday', None,       Location.BOTH, PrivmsgCmd, Role.USER, self.display_events_today)
        self.add_command('topicid',   r'^[\d]+$', Location.BOTH, PrivmsgCmd, Role.USER, self.update_topic)
        
        self.add_command('addevent',  r'^(\d{1,2}\.\d{1,2}\.\d{4}|\d{1,2}\.\d{1,2}\.\d{4}-\d{1,2}\.\d{1,2}\.\d{4})\s(.+)$', Location.BOTH, PrivmsgCmd, Role.USER, self.add_event)
        self.add_command('delevent',  r'^([\d]+|\d{1,2}\.\d{1,2}\.\d{4})$',                                                 Location.BOTH, PrivmsgCmd, Role.USER, self.delete_event)

        self.add_command('addcat',    r'^[\S]+\s(#[0-9A-Fa-f]{3}|#[0-9A-Fa-f]{6})$', Location.BOTH, PrivmsgCmd, Role.USER, self.add_category)
        self.add_command('chgcat',    r'^[\S]+\s(#[0-9A-Fa-f]{3}|#[0-9A-Fa-f]{6})$', Location.BOTH, PrivmsgCmd, Role.USER, self.change_category)
        self.add_command('delcat',    r'^[\S]+$',                                    Location.BOTH, PrivmsgCmd, Role.USER, self.delete_category)

    def invalid_parameters(self, event, location, command, parameter):
        """
        """
        
        messages = {}
        messages['kalender']  = 'usage: .kalender'
        messages['listtoday'] = 'usage: .listtoday'
        messages['topicid']   = 'usage: .topicid <id>'
        messages['addevent']  = 'usage: .addevent <datumvon>[-datumbis] <beschreibung>'
        messages['delevent']  = 'usage: .delevent <id|datum>'
        messages['addcat']    = 'usage: .addcat <name> <farbe>'
        messages['chgcat']    = 'usage: .chgcat <name> <farbe>'
        messages['delcat']    = 'usage: .delcat <name>'
        
        return messages[command]

    """-------------------------------------------------------------------------
    Private helper methods
    -------------------------------------------------------------------------"""
    def get_date(self, date_string):
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
        
        date = matchlist.group(1, 2, 3)
        
        try:
            return date(int(date[2]),int(date[1]),int(date[0]))
            
        except ValueError as e:
            raise DateRangeInvalid(e)
        
    def get_hex_color(self, color_string):
        """
        Check if the input string contains a valid hex color code.
        
        Valid codes are '#' + 3 digits or 6 digits
        
        """
        
        length = len(color_string[1:])
        
        if color_string[0] != '#' or (length != 3 and length != 6):
            raise ColorInvalid
        
        for char in color_string[1:]:
            if char not in hexdigits:
                raise ColorInvalid

        return color_string
        
    """-------------------------------------------------------------------------
    Internal module commands
    -------------------------------------------------------------------------"""
    def display_reminder(self, date):
        """
        Timer callback function.
        """
        
        reply = self.display_events_by_date(None, Location.CHANNEL, None, [date])
        
        for channel in self.usermgmt.chanlist.channels:
            self.send_reply(PrivmsgCmd, channel, reply)
    
    """-------------------------------------------------------------------------
    Interactive module commands - display
    -------------------------------------------------------------------------"""
    def display_calendar_address(self, event, location, command, parameter):
        """
        Display the web calendar's address.
        """
        
        reply = InteractiveModuleReply()
        
        reply.add(self.config.get('calendarUrl'))
        
        return reply
    
    def display_events_today(self, event, location, command, parameter):
        """
        Display today's events, if any.
        """
        
        self.display_events_by_date(event, location, command, [date.today()])

    def display_events_by_date(self, event, location, command, parameter):
        """
        Display events occuring at the given date.
        
        called by bot           - reply public
        called by user: channel - reply public
        called by user: query   - reply private
        """
        
        reply = InteractiveModuleReply()
        
        date = parameter[0]
        
        if location == Location.CHANNEL:
            user = None
        else:
            user = self.getAuth(event.source)
        
        events = self.persistence.findEventsForReminder(
            date,
            '____-{0}–{1}'.format(date.month, date.day),
            CATEGORY_BIRTHDAY
        )
        
        results = []

        for event in events:
            if location == Location.CHANNEL:
                pass
            
            else:
                pass
            
            if event['User'] is None:
                # public
                results.append(event)
            
            else:
                    if (i[1] == CATEGORY_BIRTHDAY):
                        reply.add('{0} hat Geburtstag!'.format(i[0]))
                    else:
                        reply.add(i[0])
                    
                    self.persistence.updateEventReminder(i[3], True)
        
        if (len(PublicResults) > 0):
            if (self.Topic.isStandardTopic()) and (len(PublicResults) == 1):
                self.persistence.updateReminded(PublicResults[0][3])
                if (PublicResults[0][1] == CATEGORY_BIRTHDAY):
                    #ServerMsg("PRIVMSG Q :settopic " + self.Channel + " " + self.Topic.setTopic("Kalender","Happy Birthday " + i[0].encode('utf-8')) + "\n")
                    pass
                else:
                    #ServerMsg("PRIVMSG Q :settopic " + self.Channel + " " + self.Topic.setTopic("Kalender",i[0].encode('utf-8')) + "\n")
                    pass

            else:
                for i in PublicResults:
                    reply.add("<ID {0}> {1}".format(i[3], i[0]))
                    self.persistence.updateEventReminder(i[3], True)
                    
                reply.add("Als Topic übernehmen? .topicid <id>")
                
                return reply
            
    def update_topic(self, event, location, command, parameter):
        """
        Post the given event to the current topic.
        """
        
        reply = InteractiveModuleReply()
        
        eventId = int(parameter[0])
        
        try:
            result = self.persistence.findEventByID(eventId)
            
            if result == None:
                raise EventNotFound
    
            if result[1].lower() == CATEGORY_BIRTHDAY:
                topic = 'Happy Birthday {0}'.format(result[0])
            else:
                topic = result[0]
    
            """self.client.send_command(topic)"""
        
        except DatabaseError:
            reply.add('Deine Mutter hat die Datenbank gefressen')
        
        except EventNotFound:
            reply.add('Kein Event mit ID {0} gefunden'.format(eventId))
            
        return reply
    
    """-------------------------------------------------------------------------
    Module commands - events
    -------------------------------------------------------------------------"""
    def add_event(self, event, location, command, parameter):
        """
        Create a new event.
        
        .addevent <startdate>[-<enddate>] description
        
        TODO: commit + rollback database handling
        """

        category = parameter[0]
        date = parameter[1]
        entry = parameter[2]

        try:
            if location == Location.CHANNEL:
                user = None
            else:
                user = self.getAuth(event.source)

            if user == None:
                raise UserNotAuthed
            
            if not self.isUser(user):
                raise UserInvalid
            
            if not self.isCategory(category, user):
                raise CategoryInvalid
            
            if '-' not in date:
                date = self.get_date(date)
                
                self.persistence.insertEvent(entry, date, category, user)
    
            else:            
                if category.lower() == CATEGORY_BIRTHDAY:
                    raise MultipleEventsNotPossible
                    
                dates = date.split('-')
    
                dateFrom = self.get_date(dates[0])
                dateTo = self.get_date(date[1])
    
                delta = dateTo-dateFrom

                for day in range(delta.days+1):
                    date = dateFrom + timedelta(days=day)
                    
                    self.persistence.insertEvent(entry, date, category, user)

        except DatabaseError:
            return "Etwas lief schief! Datenbankfehler"
        
        except UserNotAuthed:  
            return "Du bist nicht geauthed!"
            
        except UserInvalid:
            return "Du hast dir noch keinen Account angelegt!"
        
        except DateFormatInvalid:
            return "Datum muss im Format [d]d.[m]m.yyyy sein. Bsp: 12.5.2010"
        
        except DateRangeInvalid as e:
            return 'Ungültiges Datum: ({0}).'.format(e)
        
        except CategoryInvalid:
            reply = InteractiveModuleReply()
            reply.add('Es gibt keine Kategorie "{0}".'.format(category))
            reply.add('Mit .addcat kann eine neue Kategorie hinzugefügt werden.')
            return reply
        
        except MultipleEventsNotPossible:
            return "Kein Rangeadd bei Birthday möglich!"

        except:
            return 'Ein unbehandelter Fehler ist aufgetreten, opfeeeeeer!'
            
        return "Eintrag erfolgreich eingefügt!"
    
    def delete_event(self, event, location, command, parameter):
        """
        .delevent [<id>|<datum>]
        """
    
        id_or_date = parameter[0]
        
        try:
            if location == Location.CHANNEL:
                user = None
            else:
                user = self.getAuth(event.source)
    
            try:
                date = self.get_date(id_or_date)
                
                """-------------------------------------------------------------
                delete by date
                -------------------------------------------------------------"""
                events = self.persistence.findEventsByDate(date, user)
                
                count = len(events)
                
                if count == 0:
                    raise EventNotFound
                
                if count > 1:
                    raise AmbiguousEventsFound(events)

                eventId = events[0]                
            
            except DateFormatInvalid:
                """-------------------------------------------------------------
                delete by ID
                -------------------------------------------------------------"""
                eventId = int(id_or_date)
                
            self.persistence.deleteEvent(eventId, user)

        except DatabaseError:
            return "Error 555!"
        
        except EventNotFound:
            return "Kein Eintrag zu diesem Datum gefunden."
        
        except AmbiguousEventsFound as events:
            reply = InteractiveModuleReply()
            reply.add('Mehrere Einträge gefunden:')
            [reply.add("ID: {0}, Name: {1}".format(event['ID'], event['Name'])) for event in events]
            return reply

        return "Done."

    """-------------------------------------------------------------------------
    Module commands - categories
    -------------------------------------------------------------------------"""
    def add_category(self, event, location, command, parameter):
        """
        .addcat name #color
        """

        category = parameter[0]
        color = parameter[1]         

        try:
            if location == Location.CHANNEL:
                user = None
            else:
                user = self.getAuth(event.source)
            
            if self.isCategory(category, user):
                raise CategoryExists
            
            color = self.get_hex_color(color)
                
            self.persistence.insertCategory(category, color, user)
        
        except DatabaseError:
            return "Unbekannter Fehler beim Einfügen. Bitte beim Chef :p melden!"
        
        except CategoryExists:
            return "Kategorie bereits vorhanden!"
        
        except ColorInvalid:
            return "HTML Farbcode bitte, z.B. #000000"
        
        return "Kategorie wurde eingefügt!"

    def change_category(self, event, location, command, parameter):
        """
        .chgcat [name] [color]
        """
        
        category = parameter[0]
        color = parameter[1]
        
        try:
            if location == Location.CHANNEL:
                user = None
            else:
                user = self.getAuth(event.source)
            
            if not self.isCategory(category, user):
                raise CategoryInvalid
            
            color = self.get_hex_color(color)
                
            self.persistence.updateCategory(category, color)

        except DatabaseError:
            return "Fehler [02] beim Einfügen. Bitte beim 'Chef' :p melden!"
            
        except CategoryInvalid:
            return "Diese Kategory gibt es nicht!"
        
        except ColorInvalid:
            return "HTML Farbcode bitte, z.B: '#000000'"
            
        return "Die Farbe für die Kategorie wurde geändert!"
    
    def delete_category(self, event, location, command, parameter):
        """
        .delcat [name]
        """
        
        category = parameter[0]
        
        try:
            if location == Location.CHANNEL:
                if REGEX_CATEGORY_DEFAULT.search(category.upper()):
                    raise UserNotAuthorized
                
                user = None
                
            else:
                user = self.getAuth(event.source)
    
            if not self.isCategory(category, user):
                raise CategoryInvalid
            
            if not self.isUnusedCategory(category, user):
                raise CategoryUsed
                    
            self.persistence.deleteCategory(category, user)
            
        except DatabaseError:
            return "Error 666!"
        
        except UserNotAuthorized:
            return "Die Standardkategorien können nicht gelöscht werden."
        
        except CategoryInvalid:
            return "Diese Kategory gibt es nicht!"
        
        except CategoryUsed:
            return "Eine Kategory kann erst gelöscht werden, wenn sie keine Einträge mehr hat."
        
        return "Done."
            
    """-------------------------------------------------------------------------
    Module commands - users
    -------------------------------------------------------------------------"""
    def add_user(self, event, location, command, parameter):
        """
        .adduser [password]
        """
        
        password = parameter[0]
        
        try:
            user = self.getAuth(event.source)
        
            if not user:
                raise UserNotAuthed
            
            if self.isPrivateUser(user):
                raise UserExists
        
            password_hash = md5(password).hexdigest()
            
            self.persistence.insertUser(user, password_hash)
        
        except DatabaseError:
            return "Fehler beim der Accounterstellung!"
        
        except UserNotAuthed:
            return "Du bist nicht geauthed!"
        
        except UserExists:
            return "Du hast bereits einen Account!"
        
        return "Dein Account wurde erstellt!"

"""-----------------------------------------------------------------------------
Persistence
-----------------------------------------------------------------------------"""
class CalendarPersistence(SQLitePersistence):
    def findEventByID(self, eventId):
        cursor = self.get_cursor()
        cursor.execute("SELECT ca.Name, ct.Name FROM CALENDAR AS ca, CATEGORY AS ct WHERE ca.ID=? AND ca.ID=ct.ID", [eventId])
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def findLastestEvent(self):
        cursor = self.get_cursor()
        cursor.execute("SELECT MAX(ca.ID) FROM CALENDAR AS ca")
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def findEventsByDate(self, date, user=None):
        cursor = self.get_cursor()
        cursor.execute("SELECT ca.ID, ca.Name FROM CALENDAR AS ca WHERE ca.Date_B=? AND ca.UserID IN (SELECT u.UserID FROM USER AS u WHERE u.Name=?)", [date, user])
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def findEventsForReminder(self, date_full, date_wildcard, wildcard_category):
        cursor = self.get_cursor()
        cursor.execute("SELECT ca.ID, ca.Name AS EVENT, ct.Name AS CATEGORY, u.Name AS USER FROM CALENDAR AS ca, CATEGORY AS ct, USER AS u WHERE ca.CatID=ct.CatID AND ca.UserID=u.UserID AND ca.Reminded=0 AND (ca.Date_B=? OR (ca.Date_B LIKE ? AND ct.Name=? COLLATE NOCASE))", [date_full, date_wildcard, wildcard_category])
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def isUser(self, user):
        cursor = self.get_cursor()
        cursor.execute("SELECT u.UserID FROM USER AS u WHERE u.Name=?", [user])
        result = cursor.fetchone()
        cursor.close()      
        return (False if result == None else True)
    
    def isCategory(self, name, user):
        cursor = self.get_cursor()
        cursor.execute("SELECT ct.CatID FROM CATEGORY AS ct WHERE ct.Name=? COLLATE NOCASE AND ct.UserID IN (SELECT u.UserID FROM USER AS u WHERE u.Name=?)", [name, user])
        result = cursor.fetchone()
        cursor.close()      
        return (False if result == None else True)

    def isUnusedCategory(self, name, user):
        cursor = self.get_cursor()
        cursor.execute("SELECT ca.CatID FROM CALENDAR AS ca WHERE ca.CatID IN (SELECT ct.CatID FROM CATEGORY AS ct WHERE ct.Name=? COLLATE NOCASE) AND ca.UserID IN (SELECT u.UserID FROM USER AS u WHERE u.Name=?)", [name, user])
        result = cursor.fetchone()
        cursor.close()
        return (True if result == None else False)             
    
    def insertEvent(self, name, date, category, user=None):
        cursor = self.get_cursor()
        cursor.execute("INSERT INTO CALENDAR (ID,UserID,CatID,Name,Date_B,Reminded) VALUES (NULL,(SELECT u.UserID FROM USER AS u WHERE u.Name=?),(SELECT ct.CatID FROM CATEGORY AS ct WHERE ct.Name=? COLLATE NOCASE),?,?,0)", [user, category, name, date])
        self.connection.commit()
        cursor.close()
        
        if self.connection.total_changes == 0:
            raise DatabaseError

    def insertCategory(self, name, color, user=None):
        cursor = self.get_cursor()
        cursor.execute("INSERT INTO CATEGORY (CatID,Name,Color,UserID) VALUES (NULL,?,?,(SELECT UserID FROM USER WHERE Name=?))", [name, color, user])
        self.connection.commit()
        cursor.close()
        
        if self.connection.total_changes == 0:
            raise DatabaseError
    
    def insertUser(self, user, password_hash):
        cursor = self.get_cursor()
        cursor.execute("INSERT INTO USER (UserID,Name,Password) VALUES (NULL,?,?)", [user, password_hash])
        self.connection.commit()
        cursor.close()
        
        if self.connection.total_changes == 0:
            raise DatabaseError
        
    def insertLink(self, user):
        cursor = self.get_cursor()
        cursor.execute("UPDATE LinkID IN CALENDAR WHERE Name=?", [user])        
        cursor.close()
    
    def updateEventReminder(self, eventId, reminded):
        cursor = self.get_cursor()
        cursor.execute("UPDATE CALENDAR SET Reminded=? WHERE ID=?", [reminded, eventId])
        self.connection.commit()
        cursor.close()
    
    def updateCategory(self, category, color, user=None):
        cursor = self.get_cursor()
        cursor.execute("UPDATE CATEGORY SET Color=? WHERE Name=? COLLATE NOCASE", [color, category])
        self.connection.commit()
        cursor.close()
        
        if self.connection.total_changes == 0:
            raise DatabaseError

    def deleteEvent(self, eventId, user=None):
        cursor = self.get_cursor()
        cursor.execute("DELETE FROM CALENDAR WHERE ID=? AND UserID IN (SELECT UserID FROM USER WHERE Name=?)", [eventId, user])
        self.connection.commit()
        cursor.close()
        
        if self.connection.total_changes == 0:
            raise DatabaseError

    def deleteCategory(self, name, user=None):
        cursor = self.get_cursor()
        cursor.execute("DELETE FROM CATEGORY WHERE Name=? COLLATE NOCASE AND UserID IN (SELECT u.UserID FROM USER AS u WHERE u.Name=?)", [name, user])
        self.connection.commit()
        cursor.close()
        
        if self.connection.total_changes == 0:
            raise DatabaseError
    