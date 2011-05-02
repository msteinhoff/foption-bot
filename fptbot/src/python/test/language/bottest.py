'''
Created on Jan 12, 2011

@author: msteinhoff
'''

import gdata.calendar.client

def PrintUserCalendars(calendar_client):
    feed = calendar_client.GetAllCalendarsFeed()
    print feed.title.text
    
    for i, a_calendar in enumerate(feed.entry):
        print '\t%s. %s' % (i, a_calendar.title.text,)
        

calendar_client = gdata.calendar.client.CalendarClient(source='foption-fptbot-1.0')
calendar_client.ssl = True

calendar_client.ClientLogin('fptbot@googlemail.com', 'deinemudderfistedbots1337', calendar_client.source);

PrintUserCalendars(calendar_client)

