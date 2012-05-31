# -*- coding: UTF-8 -*-
"""
$Id$

$URL$

Copyright (c) 2011 foption

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

@since Jul 23, 2011
@author Mario Steinhoff
"""

__version__ = '$$'

import datetime
import json

from core import runlevel
from core.bot import Bot
from objects.calendar import Calendar, Event
from components.calendar import GoogleBackend

try:
    bot = Bot()
    bot.init(runlevel.NETWORK_SERVICE)
    
    cc = bot.get_subsystem('calendar-component')
    """
    event = Event(start=datetime.date(2011, 9, 26), end=datetime.date(2011, 9, 27), title="sync-test")
    event = cc.insert_object(event)
    
    scnds = cc.datastore.secondary_backends
    gbe = [scnd for scnd in scnds if isinstance(scnd, GoogleBackend)][0]
    
    query = cc.datastore.get_query('event_by_id')
    local_id = [identity for identity in event.identities if identity.backend.typename == 'GoogleBackend'][0]
    
    query.id = json.loads(local_id.identity)['edit']
    
    gev = gbe.find_objects(query)
    
    query = cc.datastore.get_query('all_calendars_feed')
    
    for i, calendar in enumerate(gbe.find_objects(query).entry):
        print calendar.title.text
        print calendar.id.text
        
        print calendar.find_url(gbe.LINK_EVENTFEED)
        
        print "---"
    """
    
    calendar = Calendar(title='Party')
    cc.insert_object(calendar)
    
    event = Event(calendar=calendar, start=datetime.date(2011, 9, 30), end=datetime.date(2011, 10, 1), title="gangbang bei baums mutter")
    cc.insert_object(event)
    

except:
    bot.get_logger().exception('Unhandled exception')

finally:
    bot.init(runlevel.HALT)
