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

@since Apr, 07 2010
@author Rack Rackowitsch
@author Mario Steinhoff
"""

__version__ = '$Rev$'

import urllib
import re
import random

from threading import Timer
from datetime import date, datetime
from htmlentitydefs import name2codepoint

from core.constants import TIME_HOUR
from core.config import Config
from interaction.irc.module import Module
from interaction.irc.command import PrivmsgCmd

class Facts(Module):
    """
    This module posts random facts in the channel.
    """
    
    def initialize(self):
        bot = self.client.bot; 
        
        bot.register_config(FactsConfig)
        
        self.config = bot.get_config(FactsConfig.identifier)
        self.logger = bot.get_logger(FactsConfig.identifier)
        self.persistence = FactsPersistence(bot.get_persistence())
        
    def start(self):
        self.start_daily_timer(self.config.get('dbUpdateInterval'), self.update_data)
           
    def shutdown(self):
        self.cancel_timer()
    
    def get_receive_listeners(self):
        return {PrivmsgCmd: self.post}
    
    def post(self, event):
        if random.randint(1,88) != 12:
            return
        
        target, message = event.parameter[0:2]
        
        fact = self.persistence.get_random_fact()
        
        if not fact:
            return
        
        text = 'ACTION ist kluK und weiss: "{0}"'.format(fact)
        
        for channel in self.client.get_module('usermgmt').chanlist.get_channels():
            self.client.send_command(PrivmsgCmd, channel, text)
    
    def update_data(self):
        currentLength = len(self.data)
        if (len(self.WissenDB) > currentLength):
            print ">> 'wissen'-database received " + str(len(self.WissenDB) - length) + " new facts!" 
            list2txtfile(self.WissenDB, self.FilenameDB)
            Text = self.WissenDB.pop(0).strip().replace("%nbsp;", " ")
                
                
class FactsConfig(Config):
    identifier = 'interaction.irc.module.facts'
        
    def valid_keys(self):
        return [
            'startDate',
            'dbUpdateInterval',
            'factUrl',
        ]
    
    def default_values(self):
        return {
            'startDate'        : date(2010,4,8),
            'dbUpdateInterval' : TIME_HOUR * 8,
            'factUrl'          : ''
        }

class FactPersistence(object):
    def __init__(self, persistence):
        self.persistence = persistence
    
    def get_all_facts(self):
        pass
    
    def get_random_fact(self):
        pass
    
class FactInterface(object):
    def get_data(self):
        raise NotImplementedError

class SchoelnastAtFactInterface(FactInterface):
    
    def __init__(self):
        self.url = 'http://wissen.schoelnast.at/alles.shtml'
        
        self.regex = re.compile('<tr><td class="li">(\d{2}.\d{2}.\d{4})</td><td class="re2">(.+)<span class="blau">')

    def get_data(self):
        stream = urllib.urlopen(self.url)
        
        rawData = stream.readlines()

        for line in rawData:
            try:
                result = self.regex.search(line).group(1,2)
                
                date = datetime.strptime(result[0], '%d.%m.%Y').date()
                fact = result[1]
                
                if (Date > self.Config.WissenDate):
                    self.Config.WissenDate = Date
                    
                if (Date > start_Date):
                    a = self.unescape(r[1]).strip() + "\n"
                    self.WissenDB.append(a)
                else:
                    break
            
            except:
                pass

    def unescape(self,s):
        return re.sub('&(%s);' % '|'.join(name2codepoint), lambda m: unichr(name2codepoint[m.group(1)]), s)
