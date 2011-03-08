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

from core.constants import DIR_DB_FACTS
from core.config import Config
from interaction.irc.module import Module
from interaction.irc.command import PrivmsgCmd

HOUR_IN_SECONDS = 3600

class Facts(Module):
    """
    This module posts random facts in the channel.
    """

    class FactsConfig(Config):
        def name(self):
            return 'interaction.irc.module.facts'
            
        def valid_keys(self):
            return [
                'startDate',
                'dbPath',
                'dbUpdateInterval',
                'factUrl',
            ]
        
        def default_values(self):
            return {
                'startDate'        : date(2010,4,8),
                'dbFile'           : DIR_DB_FACTS,
                'dbUpdateInterval' : HOUR_IN_SECONDS * 8,
                'factUrl'          : '' 
            }

    def initialize(self):
        self.persistence = self.client._bot.getPersistence()
        self.config = self.FactsConfig(self.persistence)

        try:
            self.data = self.persistence.readlines(self.config.get('dbFile'))
            
        except:
            self.data = []
            
        self.start_timer(date.today())

        
    def start_timer(self, dayToCheck):
        self.timer = Timer(
            self.config.get('dbUpdateInterval'),
            self.timer_event,
            [dayToCheck]
        )
        self.timer.start()
           
    def shutdown(self):
        self.Timer.cancel()
    
    def get_receive_listeners(self):
        return {PrivmsgCmd: self.action}
    

    def action(self, event):
        if random.randint(1,88) != 12:
            return
        
        target, message = event.parameter[0:2]

        if (len(self.WissenDB) > 0):
            Text = self.WissenDB.pop(0).strip().replace("%nbsp;", " ")
            PrivMsg(Target, "ACTION ist kluK und weiss: '" + Text + "'")
            
            list2txtfile(self.WissenDB, self.FilenameDB)
    

    
    def timer_event(self, dayWhenStarted):
        """
        """
        
        today = date.today()
        
        if (today == dayWhenStarted):
            return
        
        self.update_data()
        
        self.start_timer(today)

        
    def update_data(self):
        currentLength = len(self.data)
        


        if (len(self.WissenDB) > currentLength):
            print ">> 'wissen'-database received " + str(len(self.WissenDB) - length) + " new facts!" 
            list2txtfile(self.WissenDB, self.FilenameDB)
                

class FactPersistence(object):
    
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
