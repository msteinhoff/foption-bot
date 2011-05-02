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

@since Mar 12, 2011
@author Mario Steinhoff
"""

__version__ = '$Rev$'

import unittest

from core.constants import DIR_CONFIG
from core.config import Config

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.bot = DummyBot()
        
        self.config = DummyConfig(self.bot)
    
    def test_00_instantiation(self):
        self.assertTrue(isinstance(self.config._bot, DummyBot))
        self.assertTrue(len(self.config._keys) > 0)
        
    def test_01_name(self):
        self.assertEquals(self.config.name(), 'test.core.config')
        
    def test_02_validation(self):
        invalid = {'test5': 'foobar', 'test2' : 42}
        
        result = self.config.filter_valid_keys(invalid)
        
        self.assertTrue('test2' in result)
        self.assertTrue('test5' not in result)
        
    def test_03_data_io(self):
        object1 = 03
        object2 = 4.3382
        object3 = 'foobar42'
        
        self.config.set('test10', object1)
        self.config.set('test20', object2)
        self.config.set('test30', object3)
        
        self.assertTrue('test10' in self.config._keys)
        self.assertEquals(self.config.get('test10'), object1)
        
        self.assertTrue('test20' in self.config._keys)
        self.assertEquals(self.config.get('test20'), object2)
        
        self.assertTrue('test30' in self.config._keys)
        self.assertEquals(self.config.get('test30'), object3)
    
    def test_05_delete(self):
        self.config.delete('test2')
        
        self.assertRaises(KeyError, self.config.get, 'test2')
        self.assertTrue('test1' in self.config._keys)
    
    def test_06_save(self):
        self.config.save()
        self.config.set('test10', 'foobar84')
        
        filename = '{0}/{1}'.format(DIR_CONFIG, self.config.name())
        
        self.assertTrue(filename in self.bot.get_persistence().storage)
        self.assertEquals(self.bot.get_persistence().storage[filename]['test1'], 10)
        self.assertTrue('test10' not in self.bot.get_persistence().storage[filename])
    
    def test_07_load(self):
        pass        

class DummyBot():
    def __init__(self):
        self.persistence = MemoryPersistence()
    
    def get_persistence(self):
        return self.persistence

class MemoryPersistence():
    def __init__(self):
        self.storage = {}
        
    def readobject(self, filename):
        if filename not in self.storage:
            self.storage[filename] = {}
            
        return self.storage[filename]
    
    def writeobject(self, filename, object):
        self.storage[filename] = {}
        self.storage[filename].update(object)

class DummyConfig(Config):
    identifier = 'test.core.config'
        
    def valid_keys(self):
        return ['test1', 'test2', 'test3', 'test10', 'test20', 'test30']
    
    def default_values(self):
        return {'test1': 10, 'test2': 'foobar', 'test3': False}

