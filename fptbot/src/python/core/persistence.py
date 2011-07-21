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

import sqlite3

# ------------------------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------------------------
class DatabaseError(Exception): pass

# ------------------------------------------------------------------------------
# Business Logic
# ------------------------------------------------------------------------------
class Persistence(object):
    """
    Provide persistence to all sub-systems.
    
    Currently, the following storage systems are supported:
        - pickle.dump/pickle.load
        - file.readlines/file.writelines
        - sqlite
    """
    
    def __init__(self, sqlite_file):
        """
        Create a new persistence instance.
        
        @param sqlite_file: The SQLite database.
        """
        
        self.connection = sqlite3.connect(sqlite_file)
        self.connection.row_factory = sqlite3.Row
        
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
