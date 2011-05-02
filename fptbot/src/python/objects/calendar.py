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
@author msteinhoff
"""

__version__ = '$Rev$'

class Calendar(object):
    AUTO = 1
    MANUAL = 2
    
    def __init__(self, id=None, name=None, type=None):
        self.id = id
        self.name = name
        self.type = type
        
    def __str__(self):
        return ''

class Event(object):
    def __init__(self, id=None, etag=None, start=None, end=None, title=None, description=None, location=None):
        self.id = id
        self.etag = etag
        self.start = start
        self.end = end
        self.title = title
        self.description = description
        self.location = location
        
    def __str__(self):
        return ''

class Contact(object):
    def __init__(self, id=None, firstname=None, lastname=None, nickname=None, birthday=None):
        self.id = id
        self.firstname = firstname
        self.lastname = lastname
        self.nickname = nickname
        self.birthday = birthday
        
    def __str__(self):
        return ''

class AuditEntry(object):
    def __init__(self, id=None, datetime=None, principal=None, action=None, datatype=None, databefore=None, dataafter=None):
        self.id = id
        self.datetime = datetime
        self.principal = principal
        self.action = action
        self.datatype = datatype
        self.databefore = databefore
        self.dataafter = dataafter
        
    def __str__(self):
        return ''
    
