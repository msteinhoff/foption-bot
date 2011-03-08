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
import sqlite3
import hashlib
import datetime

from core.constants import DIR_DB_CALENDAR, TIME_MINUTE
from core.config import Config
from interaction.irc.module import InteractiveModule, InteractiveModuleReply, Location, Role
from interaction.irc.command import PrivmsgCmd

CATEGORY_EVENT    = 'event'
CATEGORY_BIRTHDAY = 'birthday'
CATEGORY_HOLIDAY  = 'holiday'

USER_DEFAULT = 'foption'

class DatabaseError(Exception):
    pass

class InvalidDate(Exception):
    pass

class InvalidDateFormat(InvalidDate):
    pass

class InvalidDateRange(InvalidDate):
    pass

class InvalidCategory(Exception):
    pass

class InvalidUser(Exception):
    pass

class UserNotAuthed(Exception):
    pass
    

class Calendar(InteractiveModule): 
    """
    This module provides calendaring functions.
    """
    
    REGEX_DATE_SINGLE = re.compile('^(\d{1,2})\.(\d{1,2})\.(\d{4})$')
    REGEX_CATEGORY_DEFAULT = re.compile('(BIRTHDAY|EVENT|HOLIDAY)')
    
    """-------------------------------------------------------------------------
    Configuration
    -------------------------------------------------------------------------"""
    class CalenderConfig(Config):
        def name(self):
            return 'interaction.irc.module.calendar'
            
        def valid_keys(self):
            return [
                'calendarUrl',
                'dbFile',
                'reminderInterval',
            ]
        
        def default_values(self):
            return {
                'calendarUrl'      : '',
                'dbFile'           : DIR_DB_CALENDAR,
                'reminderInterval' : TIME_MINUTE * 5
            }
    
    """-------------------------------------------------------------------------
    InteractiveModule methods
    -------------------------------------------------------------------------"""
    def module_identifier(self):
        return 'Kalender'
    
    def initialize(self):
        self.persistence = self.client._bot.getPersistence()
        self.config = self.CalendarConfig(self.persistence)
        
        self.db = sqlite3.connect(self.config.get('dbFile'))
        
        self.start_daily_timer(self.config.get('reminderInterval'), self.display_reminder)
        
    def shutdown(self):
        self.cancel_timer()
    
    def init_commands(self):
        self.add_command('kalender',  None,      Location.BOTH,  PrivmsgCmd, Role.USER,  self.display_help_address)
        self.add_command('listtoday', None,      Location.BOTH,  PrivmsgCmd, Role.USER,  self.display_events_today)
        self.add_command('topicid',   '^[\d]+$', Location.BOTH,  PrivmsgCmd, Role.USER,  self.update_topic)
        
        self.add_command('addevent',  '^$', Location.BOTH,  PrivmsgCmd, Role.USER,  self.add_event)
        self.add_command('delevent',  '^$', Location.BOTH,  PrivmsgCmd, Role.USER,  self.delete_event)

        self.add_command('addcat',    '^$', Location.BOTH,  PrivmsgCmd, Role.USER,  self.add_category)
        self.add_command('chgcat',    '^$', Location.BOTH,  PrivmsgCmd, Role.USER,  self.change_category)
        self.add_command('delcat',    '^$', Location.BOTH,  PrivmsgCmd, Role.USER,  self.delete_category)

        self.add_command('adduser',   '^$', Location.QUERY, PrivmsgCmd, Role.ADMIN, self.add_user)
        self.add_command('deluser',   '^$', Location.QUERY, PrivmsgCmd, Role.ADMIN, self.delete_user)

    def invalid_parameters(self, event, location, command, parameter):
        """
        """
        
        messages = {}
        messages['kalender']  = 'usage: .kalender'
        messages['listtoday'] = 'usage: .listtoday'
        messages['topicid']   = 'usage: .topicid [zahl]'
        messages['addevent']  = 'usage: .addevent '
        messages['delevent']  = 'usage: .delevent '
        messages['addcat']    = 'usage: .addcat '
        messages['chgcat']    = 'usage: .chgcat '
        messages['delcat']    = 'usage: .delcat '
        messages['adduser']   = 'usage: .adduser '
        messages['deluser']   = 'usage: .deluser '
        
        return messages[command]

    """-------------------------------------------------------------------------
    Private helper methods
    -------------------------------------------------------------------------"""
    #returns nickname, otherwise 'None'
    def getNickFromAuth(self,Auth):
        return self.Nicklist.getNickFromAuth(Auth)
    
    #if auth is available, it will return, otherwise it will return 'False'
    def getAuth(self,Source):
        n = re.match("(.+?)!", Source).group(1)
        try:
            if (self.Nicklist.getAuth(n) != ""):
                return self.Nicklist.getAuth(n)
            return False
        except:
            return False        

    def isLeapYear(self, Year):
        """
        """
        if (Year % 4 == 0):
            if (Year % 100 == 0) and (Year % 400 != 0):
                return False
            return True
        return False
    
    def is_hex_color(self, Hexcode):
        """
        # -> <#code>
        """
        if (len(Hexcode) == 7) and (Hexcode[0] == '#'):
            x = 1
            while (x <= 5):
                try:
                    int(Hexcode[x:x+2], 16)
                except:
                    return False
                x = x + 2
            return True
        return False
    
    def get_date(self, date_string):
        """
        """
        
        matchlist = self.REGEX_DATE_SINGLE.search(date_string)
        
        if not matchlist:
            raise InvalidDateFormat
        
        date = matchlist.group(1, 2, 3)
        
        try:
            return date(int(date[2]),int(date[1]),int(date[0]))
            
        except ValueError as e:
            raise InvalidDateRange(e)
        
        
    """-------------------------------------------------------------------------
    Module commands - display
    -------------------------------------------------------------------------"""
    def display_help_address(self, event, location, command, parameter):
        """
        """
        
        return self.config.get('calendarUrl')
    
    def display_events_today(self, event, location, command, parameter):
        """
        """
        
        self.Reminder(datetime.date.today())

    def display_reminder(self, date):
        """
        """
        
        DatePart = str(date).split('-')
        BdayDate = '____-' + DatePart[1] + '-' + DatePart[2]
        
        
        PublicResults = []

        for i in result:
            if (i[2] == 'foption'):
                PublicResults.append(i)
            else:
                Nick = self.getNickFromAuth(i[2].encode('utf-8'))
                if (Nick != None):
                    if (i[1] == 'Birthday'):
                        PrivMsg(Nick, i[0].encode('utf-8') + " hat Geburtstag!", "15Kalender:7 ")
                    else:
                        PrivMsg(Nick, i[0].encode('utf-8'), "15Kalender:7 ")
                    self.UpdateReminded(i[3])
        
        if (len(PublicResults) > 0):
            if (self.Topic.isStandardTopic()) and (len(PublicResults) == 1):
                self.UpdateReminded(PublicResults[0][3])
                if (PublicResults[0][1] == 'Birthday'):
                    ServerMsg("PRIVMSG Q :settopic " + self.Channel + " " + self.Topic.setTopic("Kalender","Happy Birthday " + i[0].encode('utf-8')) + "\n")
                else:
                    ServerMsg("PRIVMSG Q :settopic " + self.Channel + " " + self.Topic.setTopic("Kalender",i[0].encode('utf-8')) + "\n")
            else:
                for i in PublicResults:
                    PrivMsg(self.Channel,"<ID " + str(i[3]) + "> " + i[0].encode('utf-8'),"15Kalender:7 ")
                    self.UpdateReminded(i[3])
                    
                PrivMsg(self.Channel,"Als Topic �bernehmen? .topicid <id>","15Kalender:7 ")
                
        def update_topic(self, event, location, command, parameter):
            """
            """
        
        target = event.parameter[0]
        eventId = int(parameter[0])
            
        result = self.findEventByID(eventId)
            
        if (result == None):
            return 'Kein Event mit ID {0} gefunden'.format(eventId)

        topic = result[0].encode('utf-8')

        if result[1].lower() == CATEGORY_BIRTHDAY:
            topic = 'Happy Birthday {0}'.format(topic)
        
        """TODO: settopic"""
    
    """-------------------------------------------------------------------------
    Module commands - events
    -------------------------------------------------------------------------"""
    def add_event(self, event, location, command, parameter):
        """
        .add event <datum>[-<bis-datum>] event-beschreibung
        """

        category = parameter[0]
        date = parameter[1]
        entry = parameter[2]

        if location == Location.CHANNEL:
            user = None
        else:
            user = self.getAuth(event.source)
            
        try:
            if user == None:
                raise UserNotAuthed
            
            if not self.isUser(user):
                raise InvalidUser
            
            if not self.isCategory(category, user):
                raise InvalidCategory
            
            if '-' not in date:
                date = self.get_date(date)
                
                self.insertEvent(entry, date, category, user)
    
            else:            
                if category.lower() == CATEGORY_BIRTHDAY:
                    return "Kein Rangeadd bei Birthday möglich!"
                    
                dates = date.split('-')
    
                dateFrom = self.get_date(dates[0])
                dateTo = self.get_date(date[1])
    
                months_31_days = [1,3,5,7,8,10,12] #month with 31 days
                
                startDay   = dateFrom.day
                startMonth = dateFrom.month
                startYear  = dateFrom.year
                
                while (dateFrom.day <= dateTo.day) or (dateFrom.month < dateTo.month) or (dateFrom.year < dateTo.year):
                    Date_B = str(s_Tag) + "." + str(s_Monat) + "." + str(s_Jahr)
                    self.addQuery(Source, Target, Category, Date_B, Text,False)
                    s_Tag += 1
                    if (s_Monat in List):
                        if (s_Tag == 32):
                            s_Tag = 1
                            s_Monat += 1
                    elif (s_Monat == 2):
                        if (self.isLeapYear(s_Jahr)):
                            if (s_Tag == 30):
                                s_Tag = 1
                                s_Monat += 1
                        else:
                            if (s_Tag == 29):
                                s_Tag = 1
                                s_Monat += 1
                    else:
                        if (s_Tag == 31):
                            s_Tag = 1
                            s_Monat += 1
                    if (s_Monat == 13):
                        s_Monat = 1
                        s_Jahr += 1

        except DatabaseError:
            return "Etwas lief schief! Datenbankfehler"
        
        except UserNotAuthed:  
            return "Du bist nicht geauthed!"
            
        except InvalidUser:
            return "Du hast dir noch keinen Account angelegt!"
        
        except InvalidDateFormat:
            return "Datum muss im Format [d]d.[m]m.yyyy sein. Bsp: 12.5.2010"
        
        except InvalidDateRange as e:
            return 'Ungültiges Datum: ({0}).'.format(e)
        
        except InvalidCategory:
            result = InteractiveModuleReply()
            result.add('Es gibt keine Kategorie "{0}".'.format(category))
            result.add('Mit .addcat kann eine neue Kategorie hinzugefügt werden.')
            return result

        except:
            return 'Ein unbehandelter Fehler ist aufgetreten.'
            
        return "Eintrag erfolgreich eingefügt!"

    
    
    def delete_event(self, event, location, command, parameter):
        """
        .delevent [<id>|<datum>]
        """
    
        id_or_date = parameter[0]
        
        """---------------------------------------------------------------------
        Check input data
        ---------------------------------------------------------------------"""
        if location == Location.CHANNEL:
            user = None
        else:
            user = self.getAuth(event.source)

        matchlist = self.REGEX_DATE_SINGLE.search(id_or_date)
        
        if not matchlist:
            """-----------------------------------------------------------------
            delete by ID
            -----------------------------------------------------------------"""
            eventId = int(id_or_date)
            
            successful = self.deleteEvent(eventId)
                
            if successful:
                return "Done."
            else:
                return "Error 555!"
        
        else:
            """-----------------------------------------------------------------
            delete by date
            -----------------------------------------------------------------"""
            date = matchlist.group(1,2,3)
            
            eventDate = date(int(date[2]), int(date[1]), int(date[0]))
            
            events = self.findEventsByDate(eventDate, user)
            
            count = len(events)
            
            if count == 0:
                return "Kein Eintrag zu diesem Datum gefunden."
            
            if count > 1:
                result = InteractiveModuleReply()
                
                result.add('Mehrere Einträge gefunden:')
                
                for event in events:
                    result.add("ID: {0}, Name: {1}".format(event[0], event[1]))
                
                return result 
            
            successful = self.deleteEvent(events[0][0], user)
            
            if successful:
                return "Done."
            else:
                return "Error 555!"

    """-------------------------------------------------------------------------
    Module commands - categories
    -------------------------------------------------------------------------"""
    def add_category(self, event, location, command, parameter):
        """
        .addcat name #color
        """

        category = parameter[0]
        color = parameter[1]         

        """---------------------------------------------------------------------
        Check input data
        ---------------------------------------------------------------------"""
        if location == Location.CHANNEL:
            user = None
        else:
            user = self.getAuth(event.source)
        
        if self.isCategory(category, user):
            return "Kategorie bereits vorhanden!"
        
        if not self.isHTMLHex(color):
            return "HTML Farbcode bitte, z.B. #000000"
            
        """---------------------------------------------------------------------
        manipulate data
        ---------------------------------------------------------------------"""
        successful = self.insertCategory(category, color, user)
        
        if successful:
            return "Kategorie wurde eingefügt!"
        else:
            return "Unbekannter Fehler beim Einfügen. Bitte beim Chef :p melden!"

    def change_category(self, event, location, command, parameter):
        """
        .chgcat [name] [color]
        """
        
        category = parameter[0]
        color = parameter[1]
        
        """---------------------------------------------------------------------
        Check input data
        ---------------------------------------------------------------------"""
        if location == Location.CHANNEL:
            user = None
        else:
            user = self.getAuth(event.source)
        
        if not self.isCategory(category, user):
            return "Diese Kategory gibt es nicht!"
        
        if not self.isHTMLHex(color):
            return "HTML Farbcode bitte, z.B: '#000000'"
            
        """---------------------------------------------------------------------
        manipulate data
        ---------------------------------------------------------------------"""
        successful = self.updateCategory(category, color)
        
        if successful:
            return "Die Farbe für die Kategorie wurde geändert!"
        else:
            return "Fehler [02] beim Einfügen. Bitte beim 'Chef' :p melden!"
    
    def delete_category(self, event, location, command, parameter):
        """
        .delcat [name]
        """
        
        category = parameter[0]
        
        """---------------------------------------------------------------------
        Check input data
        ---------------------------------------------------------------------"""
        if location == Location.CHANNEL:
            if self.REGEX_CATEGORY_DEFAULT.search(category.upper()):
                return "Die Standardkategorien können nicht gelöscht werden."
            
            user = None
            
        else:
            user = self.getAuth(event.source)

        if not self.isCategory(category, user):
            return "Diese Kategory gibt es nicht!"
        
        if self.isUnusedCategory(category, user):
            return "Eine Kategory kann erst gelöscht werden, wenn sie keine Einträge mehr hat."
                
        """---------------------------------------------------------------------
        manipulate data
        ---------------------------------------------------------------------"""
        successful = self.deleteCategory(category, user)
            
        if successful:
            return "Done."
        else:
            return "Error 666!"
            
    """-------------------------------------------------------------------------
    Module commands - users
    -------------------------------------------------------------------------"""
    def add_user(self, event, location, command, parameter):
        """
        .adduser [password]
        """
        
        user = self.getAuth(event.source)
        password = parameter[0]
        
        """---------------------------------------------------------------------
        Check input data
        ---------------------------------------------------------------------"""
        if not user:
            return "Du bist nicht geauthed!"
        
        if self.isPrivateUser(user):
            return "Du hast bereits einen Account!"
        
        """---------------------------------------------------------------------
        manipulate data
        ---------------------------------------------------------------------"""
        password_hash = hashlib.md5(password).hexdigest()
        
        successful = self.insertUser(user, password_hash)
        
        if successful:
            return "Dein Account wurde erstellt!"
        else:
            return "Fehler beim der Accounterstellung!"
                
    
    def delete_user(self, event, location, command, parameter):
        """
        """
        pass

    """-------------------------------------------------------------------------
    Persistence commands
    -------------------------------------------------------------------------"""
    def findEventByID(self, eventId):
        cursor = self.db.cursor()
        cursor.execute("SELECT ca.Name, ct.Name FROM CALENDAR AS ca, CATEGORY AS ct WHERE ca.ID=? AND ca.ID=ct.ID", [eventId])
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def findLastestEvent(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT MAX(ca.ID) FROM CALENDAR AS ca")
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def findEventsByDate(self, date, user=None):
        cursor = self.db.cursor()
        cursor.execute("SELECT ca.ID, ca.Name FROM CALENDAR AS ca WHERE ca.Date_B=? AND ca.UserID IN (SELECT u.UserID FROM USER AS u WHERE u.Name=?)", [date, user])
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def findEventsForReminder(self, date_full, date_wildcard, category):
        cursor = self.db.cursor()
        cursor.execute("SELECT ca.ID, ca.Name, ct.Name, u.Name FROM CALENDAR AS ca, CATEGORY AS ct, USER AS u WHERE ca.CatID=ct.CatID AND ca.UserID=u.UserID AND ca.Reminded=0 AND (ca.Date_B=? OR (ca.Date_B LIKE ? AND ct.Name=? COLLATE NOCASE))", [date_full, date_wildcard, category])
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def isUser(self, user):
        cursor = self.db.cursor()
        cursor.execute("SELECT u.UserID FROM USER AS u WHERE u.Name=?", [user])
        result = cursor.fetchone()
        cursor.close()      
        return (False if result == None else True)
    
    def isCategory(self, name, user):
        cursor = self.db.cursor()
        cursor.execute("SELECT ct.CatID FROM CATEGORY AS ct WHERE ct.Name=? COLLATE NOCASE AND ct.UserID IN (SELECT u.UserID FROM USER AS u WHERE u.Name=?)", [name, user])
        result = cursor.fetchone()
        cursor.close()      
        return (False if result == None else True)

    def isUnusedCategory(self, name, user):
        cursor = self.db.cursor()
        cursor.execute("SELECT ca.CatID FROM CALENDAR AS ca WHERE ca.CatID IN (SELECT ct.CatID FROM CATEGORY AS ct WHERE ct.Name=? COLLATE NOCASE) AND ca.UserID IN (SELECT u.UserID FROM USER AS u WHERE u.Name=?)", [name, user])
        result = cursor.fetchone()
        cursor.close()
        return (True if result == None else False)             
    
    def insertEvent(self, name, date, category, user=None):
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO CALENDAR (ID,UserID,CatID,Name,Date_B,Reminded) VALUES (NULL,(SELECT u.UserID FROM USER AS u WHERE u.Name=?),(SELECT ct.CatID FROM CATEGORY AS ct WHERE ct.Name=? COLLATE NOCASE),?,?,0)", [user, category, name, date])
        self.db.commit()
        cursor.close()
        
        if self.db.total_changes == 0:
            raise DatabaseError

    def insertCategory(self, name, color, user=None):
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO CATEGORY (CatID,Name,Color,UserID) VALUES (NULL,?,?,(SELECT UserID FROM USER WHERE Name=?))", [name, color, user])
        self.db.commit()
        cursor.close()
        
        if self.db.total_changes == 0:
            raise DatabaseError
    
    def insertUser(self, user, password_hash):
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO USER (UserID,Name,Password) VALUES (NULL,?,?)", [user, password_hash])
        self.db.commit()
        cursor.close()
        
        if self.db.total_changes == 0:
            raise DatabaseError
        
    def insertLink(self, user):
        cursor = self.db.cursor()
        cursor.execute("UPDATE LinkID IN CALENDAR WHERE Name=?", [user])        
        cursor.close()
    
    def updateEventReminder(self, eventId, reminded):
        cursor = self.db.cursor()
        cursor.execute("UPDATE CALENDAR SET Reminded=? WHERE ID=?", [reminded, eventId])
        self.db.commit()
        cursor.close()
    
    def updateCategory(self, category, color, user=None):
        cursor = self.db.cursor()
        cursor.execute("UPDATE CATEGORY SET Color=? WHERE Name=? COLLATE NOCASE", [color, category])
        self.db.commit()
        cursor.close()
        
        if self.db.total_changes == 0:
            raise DatabaseError

    def deleteEvent(self, eventId, user=None):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM CALENDAR WHERE ID=? AND UserID IN (SELECT UserID FROM USER WHERE Name=?)", [eventId, user])
        self.db.commit()
        cursor.close()
        
        if self.db.total_changes == 0:
            raise DatabaseError

    def deleteCategory(self, name, user=None):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM CATEGORY WHERE Name=? COLLATE NOCASE AND UserID IN (SELECT u.UserID FROM USER AS u WHERE u.Name=?)", [name, user])
        self.db.commit()
        cursor.close()
        
        if self.db.total_changes == 0:
            raise DatabaseError
    