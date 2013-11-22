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

@since Sep 29, 2011
@author Mario Steinhoff
"""

__version__ = '$Rev$'

import datetime

from core import runlevel
from core.bot import Bot
from objects.calendar import Calendar, Event
from components.calendar import LocalUserAuthority
from tools import dataloader

if __name__ == '__main__':
    bot = Bot()
    bot.register_subsystem('sqlite-persistence', 'core.persistence.SqlitePersistence', sqlite_file=dataloader.Parameters.source)
    bot.init(runlevel.NETWORK_SERVICE)
    
    sqlite = bot.get_subsystem('sqlite-persistence')
    cursor = sqlite.get_cursor()
    calendar = bot.get_subsystem('calendar-component')
    
    logger = bot.get_logger('tools.import.contacts')
    
    calendar_references = {}
    
    for category in dataloader.get_categories(cursor, dataloader.Parameters.event_categories):
        newCalendar = Calendar()
        newCalendar.title = category['Name']
        newCalendar.color = category['Color'][1:]
        newCalendar.location = dataloader.Parameters.default_location
        newCalendar.authority = LocalUserAuthority.NAME
        
        logger.info('adding item: %s', newCalendar)
        
        calendar_references[category['CatID']] = newCalendar
        calendar.insert_object(newCalendar)
        
        one = True

    for event in dataloader.get_events(cursor, dataloader.Parameters.event_categories):
        
        newEvent = Event()
        newEvent.calendar = calendar_references[event['CatID']]
        newEvent.title = event['Name']
        newEvent.start = datetime.datetime.strptime(event['Date_B'], '%Y-%m-%d')
        newEvent.end = datetime.datetime.strptime(event['Date_B'], '%Y-%m-%d')
        newEvent.allday = True
        
        logger.info('adding item: %s in calendar %s', newEvent, newEvent.calendar)
        calendar.insert_object(newEvent)
    
    bot.init(runlevel.HALT)
