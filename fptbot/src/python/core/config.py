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

@since Jan 06, 2011
@author Mario Steinhoff
"""

__version__ = '$Rev$'

import logging
try:
    import cPickle as pickle
except:
    import pickle
import os

# ------------------------------------------------------------------------------
# BusinessLogic
# ------------------------------------------------------------------------------
class Config(object):
    """
    Provide abstract system-wide configuration handling.
    
    TODO: Implement dict-style access for key/value-pairs.
    """
    
    def __init__(self, bot):
        """
        Initialize the configuration.
        
        @param bot: The bot instance.
        """
        
        self.bot = bot
        self.logger = logging.getLogger('core.config')
        
        self.init(self.default_values())
        self.load()
    
    def filter_valid_keys(self, dict):
        """
        Validate a configuration dictionary against the config structure.
        
        Keys that do not match will be removed and returned in
        a new dictionary.
        
        @param dict: The dictionary to validate
        
        @return A dictionary with all valid keys
        """
        
        result = {}
        
        for key in dict:
            if key not in self.valid_keys():
                continue
            
            result[key] = dict[key]
            
        return result
    
    def valid_keys(self):
        """
        Return a list representing valid configuration keys.
        """
        
        raise ValueError('no valid keys defined')
    
    def default_values(self):
        """
        Return a dictionary with default values. This dictionary
        is validated against the list returned by valid().
        """
        
        raise ValueError('no default values defined')
    
    def set(self, key, value):
        """
        Set a configuration value.
        
        @param key: the name of the entry
        @param value: the value of the entry
        """
        
        if key not in self.valid_keys():
            raise ValueError('invalid key: %s'.format(key))
        
        self._keys[key] = value
        
    def get(self, name):
        """
        Return a configuration value.
        
        @param name: the name of the entry
        """
        
        return self._keys[name]
    
    def get_all(self):
        """
        Return the complete configuration dictionary.
        """
        
        return self._keys
    
    def delete(self, name):
        """
        Remove a configuration value.
        
        @param name: the name of the entry
        """
        
        del self._keys[name]
    
    def init(self, data={}):
        """
        Initialize configuration dictionary with default values.
        
        Overwrite all current values.
        """
        
        self._keys = self.filter_valid_keys(data)
    
    def load(self):
        """
        Load configuration data from persistence.
        
        Existing keys are updated. If a key in the current instance
        exists but was not found in the persistence, it remains untouched. 
        """
        
        filename = os.path.join(self.bot.root, self.identifier)
        
        try:
            rawdata = self.readobject(filename)
            loaded = self.filter_valid_keys(rawdata)
            
            self._keys.update(loaded)
            
        except IOError as e:
            self.logger.error('could not load %s configuration: %s', self.identifier, e)
    
    def save(self):
        """
        Save the current configuration data to persistence.
        """
        
        filename = os.path.join(self.bot.root, self.identifier)
            
        try:
            self.writeobject(filename, self._keys)
            
        except IOError as e:
            self.logger.error('could not save %s configuration: %s', self.identifier, e)
    
    def readobject(self, filename):
        """
        Restore a python object from a file.
        
        Read the serialized data of a python object's state and create
        an object from it.
        
        @param filename: The source filename.
        
        @return the restored object 
        """
        
        with open(filename, 'r') as f:
            object = pickle.load(f)
        
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
            pickle.dump(object, f)
    
