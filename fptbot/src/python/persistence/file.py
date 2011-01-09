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

@since 08.01.2010
@author Mario Steinhoff
"""

from cPickle import dump
from cPickle import load

from persistence import Persistence


class File(Persistence):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
            
    def write(self, filename, object):
        """
        serialize a python object's state and write the data to the filesystem
        
        @param filename: the destination filename
        @param object:   the object to serialize
        """
        
        f = open(filename, "w")
        
        dump(object, f)
        
        f.close()
    
    def read(self, filename):
        """
        read the serialized data of a python object's state and create an object from it
        
        @param filename: the source filename
        
        @return the restored object 
        """
        
        f = open(filename, "r")
        
        object = load(f)
        
        f.close()
        
        return object
