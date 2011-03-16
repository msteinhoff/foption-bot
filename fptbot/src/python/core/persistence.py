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
from cPickle import dump, load

class DatabaseError(Exception):
    pass

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


    def readobject(self, filename):
        """
        Restore a python object from a file.
        
        Read the serialized data of a python object's state and create
        an object from it.
        
        @param filename: The source filename.
        
        @return the restored object 
        """
        
        with open(filename, 'r') as f:
            object = load(f)
        
        return object
    
    def writeobject(self, filename, object):
        """
        Persist a python object to a file.
        
        Serialize a python object's state and write the data to the
        filesystem.
        
        @param filename: The destination filename.
        @param object: The object to serialize.
        """
        
        with open(filename, 'w') as f:
            dump(object, f)
    
    def readlines(self, filename):
        """
        Restore a python sequence from a file.
        
        Read the string data and create a sequence from it.
        
        @param filename: The source filename.
        
        @return the sequence.
        """
        with open(filename, "r") as f:
            list = f.readlines()
        
        return list

    def writelines(self, filename, sequence):
        """
        Persist a python sequence to a file.
        
        Write a sequence of strings to the filesystem using writelines().
        Each string object must have a line separator.
        
        @param filename: The destination filename.
        @param sequence: The sequence to write.
        
        @see file.writelines()
        """
        with open(filename, 'w') as f:
            f.writelines(sequence)
        
        f.close()
        
    
