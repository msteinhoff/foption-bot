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

@since 06.01.2010
@author Mario Steinhoff
"""

from os import path

from core.constants          import DIR_CONFIG
from core.messages           import message
from persistence.persistence import Persistence

class Config(object):
    """
    Base class for system configuration
    """

    def __init__(self, name, persistence, valid, defaults={}):
        """
        initialize the configuration
        
        @param name: the configuration name
        @param persistence: the persistence
        @param valid: a list with valid keys
        @param defaults: a dictionary with default values. the 
        """
        
        if not isinstance( persistence, Persistence ):
            raise TypeError( "invalid persistence instance" )
    
        self.name  = name
        self.valid = valid
        self.keys  = self.__checkKeys(defaults)
        self.persistence = persistence
        
        # Go-Go-Gadget Helicopter
        self.load()


    def __del__(self):
        """
        cleanup: try to save configuration data to persistence before deletion
        """
        
        self.save()
    
    
    def __checkKeys(self, keys):
        """
        check a given configuration dictionary against valid keys
        invalid entries will be removed 
        
        @param keys the dictionary to check
        
        @return a dictionary with all valid keys
        """
        
        result = {}
        
        for key, value in keys:
            if key not in self.valid:
                continue
            
            result[key] = value
            
        return result
        
    
    def __getattr__(self, name):
        """
        map configuration keys to class attribute for ease of use
        
        read a configuration key
        
        @param name: name of the configuration key
        
        @return the configuration key
        
        @raise AttributeError: if the key is not found 
        """
        
        if name not in self.keys:
            raise AttributeError
        
        return self.keys[name]
    
    
    def __delattr__(self, name):
        """
        map configuration keys to class attribute for ease of use
        
        delete a configuration key
        
        @param name: name of the configuration key
        
        @raise AttributeError: if the key is not found 
        """
        
        if name not in self.keys:
            raise AttributeError
        
        del self.keys[name]
    
    
    def __setattr__(self, name, value):
        """
        map configuration keys to class attribute for ease of use
        
        set a configuration key
        
        @param name: name of the configuration key
        @param value: the associated value
        """
        
        self.keys[name] = value
        pass
    
    
    def save(self):
        """
        save the current configuration data to persistence
        """
        
        try:
            filename = path.join(DIR_CONFIG, self.name)
            
            self.persistence.write(filename, self.keys)
            
            log.info(message[01000])
            
        except:
            log.error(message[01001])
            
        
        
    def load(self):
        """
        load configuration data from persistence
        """
        
        try:
            filename = path.join(DIR_CONFIG, self.name)
            
            self.keys = self.__checkKeys(self.persistence.read(filename))
            
            log.info(message[01002])
            
        except:
            log.error(message[01003])
