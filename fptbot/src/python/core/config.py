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

from os import path

from core.constants import DIR_CONFIG

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
        
        self._bot = bot
        
        self.init()
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
    
    def name(self):
        """
        Return the configuration's name.
        """
        
        try:
            return self.identifier
        
        except KeyError:
            raise NotImplementedError
    
    def valid_keys(self):
        """
        Return a list representing valid configuration keys.
        """
        
        raise NotImplementedError
    
    def default_values(self):
        """
        Return a dictionary with default values. This dictionary
        is validated against the list returned by valid().
        """
        
        raise NotImplementedError
    
    def set(self, key, value):
        """
        Set a configuration value.
        
        @param key: the name of the entry
        @param value: the value of the entry
        """
        
        if key not in self.valid_keys():
            raise ValueError('invalid key')
        
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
        
    def init(self):
        """
        Initialize configuration dictionary with default values.
        
        Overwrite all current values.
        """
        
        self._keys = self.filter_valid_keys(self.default_values())

    def load(self):
        """
        Load configuration data from persistence.
        
        Existing keys are updated. If a key in the current instance
        exists but was not found in the persistence, it remains untouched. 
        """
        
        filename = path.join(DIR_CONFIG, self.name())
        
        try:
            loaded = self.filter_valid_keys(self._bot.get_persistence().readobject(filename))
        
            self._keys.update(loaded)
            
        except IOError:
            # could not load shit dude
            pass
    
    def save(self):
        """
        Save the current configuration data to persistence.
        """
        
        try:
            filename = path.join(DIR_CONFIG, self.name())
                
            self._bot.get_persistence().writeobject(filename, self._keys)
            
        except IOError:
            # could not save shit dude
            pass
