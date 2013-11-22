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
from objects.calendar import Calendar, Contact
from tools import dataloader
from components.calendar import LocalBirthdayAuthority

if __name__ == '__main__':
    bot = Bot()
    bot.register_subsystem('sqlite-persistence', 'core.persistence.SqlitePersistence', sqlite_file=dataloader.Parameters.source)
    bot.init(runlevel.LOCAL_SERVICE)
    
    bot.start_subsystem('sqlite-persistence')
    sqlite = bot.get_subsystem('sqlite-persistence')
    calendar = bot.get_subsystem('calendar-component')
    
    logger = bot.get_logger('tools.import.contacts')
    
    contacts_to_insert = []
    calendar_to_insert = []
    
    for event in dataloader.get_events(sqlite.get_cursor(), [dataloader.Parameters.birthday_category]):
        contact = Contact()
        contact.nickname = event['Name']
        contact.birthday = datetime.datetime.strptime(event['Date_B'], '%Y-%m-%d')
        
        logger.info('adding item: %s', contact)
        #calendar.insert_object(contact)
    
    for category in dataloader.get_categories(sqlite.get_cursor(), [dataloader.Parameters.birthday_category]):
        calendar = Calendar()
        calendar.title = category['Name']
        calendar.color = category['Color'][1:]
        calendar.location = dataloader.Parameters.default_location
        calendar.authority = LocalBirthdayAuthority.NAME
        
        logger.info('added item: %s', calendar)
        #calendar.insert_object(contact)
    
    bot.init(runlevel.HALT)
