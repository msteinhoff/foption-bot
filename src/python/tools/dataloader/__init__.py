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

class Parameters(object):
    birthday_category = 1
    birthday_authority = '/local/birthday'
    
    event_categories = [2, 13]
    event_authority = '/local/user'
    
    default_location = u'Düsseldorf, Germany'
    source = '/Users/msteinhoff/Work/Eclipse/projects/foption/bot/data/sqlite/legacy.db'

def get_categories(cursor, category_ids):
    query = 'SELECT CatID, UserId, Name, Color FROM CATEGORY WHERE CatID IN ({seq})'.format(seq=','.join(['?']*len(category_ids)))
    cursor.execute(query, category_ids)
    
    return cursor.fetchall()

def get_events(cursor, category_ids):
    query = 'SELECT ID, UserID, CatID, Name, Date_B FROM CALENDAR WHERE CatID IN ({seq})'.format(seq=','.join(['?']*len(category_ids)))
    cursor.execute(query, category_ids)
    
    return cursor.fetchall()
