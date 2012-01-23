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

@since Jan 6, 2011
@author Mario Steinhoff
"""

__version__ = '$Rev$'

import argparse

from core import runlevel
from core.bot import Bot

def parseargs():
    parser = argparse.ArgumentParser(prog='bot', description='run the bot')
    subparser = parser.add_subparsers()
    
    cmd_run = subparser.add_parser('run', help='run --help')
    cmd_run.set_defaults(func=bot_run)
    cmd_run.add_argument(dest='cfgdir', help='the configuration directory')
    
    args = parser.parse_args()
    args.func(args)

def bot_run(args):
    bot = Bot(root=args.cfgdir)
    bot.init(runlevel.NETWORK_INTERACTION)

if __name__ == '__main__':
    parseargs()
