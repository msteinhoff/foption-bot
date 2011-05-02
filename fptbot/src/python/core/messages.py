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

This file contains all messages with associated message numbers that are
used through the whole project. When defining new messages, please use
named parameters wherever possible.

Currently, the following number ranges are defined:
 
00000-09999: Core
00001-00999: Bot
01000-01999: Config

10000-19999: Modules
20000-29999: Interaction
20001-20200: IRC
"""

__version__ = '$Rev$'

__all__ = [
    'message'
]

message = {}

message[01000] = 'configuration saved'
message[01001] = 'unable to save configuration'
message[01002] = 'configuration loaded'
message[01003] = 'unable to load configuration: config file was found'

message[20001] = ''
message[20002] = ''
message[20003] = ''
message[20005] = ''
message[20006] = ''
message[20007] = ''
message[20008] = ''
message[20009] = ''
message[20010] = ''
message[20011] = ''
message[20012] = ''
message[20013] = ''
message[20014] = ''
message[20015] = ''
message[20016] = ''

#reply.add('deine mutter hat gefailed.')
#return "OHFUCKOHFUCKOHFUCK Etwas lief schief! Datenbankfehler"
#return "Error 555!"
#reply.add('Deine Mutter hat die Datenbank gefressen')

