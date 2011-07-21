#!/usr/bin/python
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

@since Mar 16, 2011
@author Mario Steinhoff
"""

__version__ = '$Rev$'

import argparse

from core.bot import Bot

def parseargs():
    parser = argparse.ArgumentParser(prog='config', description='manipulate the bot configuration')
    subparser = parser.add_subparsers()
    
    cmd_init = subparser.add_parser('init', help='init --help', description='initialize configuration with default values. when no id is given, all known configurations will be initialized.')
    cmd_init.set_defaults(func=config_init)
    cmd_init.add_argument('--id', dest='identifier', help='only initialize the specified configuration')
    
    cmd_read = subparser.add_parser('read', help='read --help')
    cmd_read.set_defaults(func=config_read)
    cmd_read.add_argument(dest='identifier', help='the configuration identifier')
    cmd_read.add_argument('--key', dest='key', help='the configuration key to change')
    
    cmd_write = subparser.add_parser('write', help='write --help')
    cmd_write.set_defaults(func=config_write)
    cmd_write.add_argument(dest='identifier', help='the configuration identifier')
    cmd_write.add_argument(dest='key', help='the configuration key to change')
    cmd_write.add_argument(dest='type', help='the data type', choices=['int', 'bool', 'string', 'list'])
    cmd_write.add_argument(dest='value', help='the new value', nargs='+')
    
    args = parser.parse_args()
    args.func(args)

def config_init(args):
    bot = Bot()
    
    def _init(identifier, object):
        print 'initializing configuration: {0}'.format(identifier)
        
        object.init(object.default_values())
        object.save()
    
    if args.identifier == None:
        for (identifier, object) in bot.get_configs().items():
            _init(identifier, object)
    
    else:
        identifier = args.identifier
        
        try:
            object = bot.get_config(identifier)
            
            _init(identifier, object)
        
        except KeyError:
            print "{} is not a valid identifier".format(identifier)

def config_read(args):
    bot = Bot()
    
    identifier = args.identifier
    
    def _read(identifier, key, value, padding=0):
        print "{}.{} {}= '{}' ({})".format(identifier, key, ' ' * padding, value, type(value))
    
    try:
        object = bot.get_config(identifier)
    except KeyError:
        print "{} is not a valid identifier".format(identifier)
        return
        
    if(args.key == None):
        spacelist = [len(item) for item in object.get_all().keys()]
        
        if spacelist:
            space = max(spacelist)
        else:
            space = 0
        
        for (key, value) in object.get_all().items():
            _read(identifier, key, value, (space - len(key)))
        
    else:
        try:
            key = args.key
            value = object.get(key)
        except KeyError:
            print "{} is not a valid key".format(key)
            return
            
        _read(identifier, key, value)

def config_write(args):
    bot = Bot()
    
    identifier = args.identifier
    key = args.key
    type = args.type
    value = args.value
    
    try:
        object = bot.get_config(identifier)
        
    except KeyError:
        print "{} is not a valid identifier".format(identifier)
        
    if key not in object.valid_keys():
        print "{} is not a valid key".format(key)
        return
        
    
    value = ' '.join(value)
    
    if type == 'int':
        new_value = int(value)
        
    elif type == 'bool':
        new_value = bool(value)
        
    elif type == 'list':
        new_value = value.split(',')
    
    else:
        new_value = value
    
    
    object.set(key, new_value)
    object.save()


if __name__ == '__main__':
    parseargs()
