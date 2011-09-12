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

@since May 6, 2011
@author Mario Steinhoff
"""

__version__ = '$Rev$'

import urllib
import re
import datetime
import htmlentitydefs

from core.constants import TIME_HOUR
from core.config import Config
from core.component import Component, ComponentError
from objects.facts import Fact

# ------------------------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------------------------
class FactsComponentError(ComponentError): pass

# ------------------------------------------------------------------------------
# Business Logic
# ------------------------------------------------------------------------------
class FactsComponent(Component):
    def __init__(self, bot):
        self.bot = bot
        
        self.bot.register_config(FactsComponentConfig)
        
        self.config = self.bot.get_config('components.facts')
        self.logger = self.bot.get_logger('components.facts')
        
        self.bot.register_timer(
            'components.facts.update',
            'daily',
            self.config.get('retrievalInterval'),
            self.update_data
        )
    
    # --------------------------------------------------------------------------
    # Lifecycle
    # --------------------------------------------------------------------------
    def start(self):
        self.bot.get_timer('components.facts.update').start()
        
           
    def stop(self):
        self.bot.get_timer('components.facts.update').stop()
    
    # --------------------------------------------------------------------------
    # Component methods
    # --------------------------------------------------------------------------
    def find_all_facts(self):
        pass
    
    def find_random_fact(self):
        pass
    
    def insert_fact(self, fact):
        pass
    
    def delete_fact(self, id):
        pass
    
    def update_data(self):
        self.logger.info('updating data')
        
        source = SchoelnastAtFactSource()
        source.limit_date = self.config.get('lastRetrievalDate')
        
        data = source.get_data()
        
        for entity in data:
            self.insert_fact(entity)
            
        if data:
            self.config.set('lastRetrievalDate', datetime.date.today())
            self.config.save()
            
            self.logger.info('added %d new records', len(data))
        else:
            self.logger.info('no new data available')


class SchoelnastAtFactSource(object):
    """
    A data source for wissen.schoelnast.at.
    """
    
    URL = 'http://wissen.schoelnast.at/alles.shtml'
    
    LINE_PATTERN = r'<tr><td class="li"><a(.*)>(?P<date>\d{1,2}\.\d{1,2}\.\d{4})</a></td><td class="re2">(?P<fact>.*)<span class="blau">'
    LINE_DATE_FORMAT = '%d.%m.%Y'
    
    ENTITY_NAME_PATTERN = r'&({0});'.format('|'.join(htmlentitydefs.name2codepoint))
    ENTITY_CP_PATTERN = r'&#(\d{1,4});'
    
    def __init__(self):
        self.line_matcher = re.compile(self.LINE_PATTERN)
        self.entity_name_matcher = re.compile(self.ENTITY_NAME_PATTERN)
        self.entity_cp_matcher = re.compile(self.ENTITY_CP_PATTERN)
    
    def _entity2unichr(self, input):
        """
        # TODO optimize
        """
        
        def name_converter(entity_match):
            return unichr(htmlentitydefs.name2codepoint[entity_match.group(1)])
        
        def cp_converter(entity_match):
            return unichr(int(entity_match.group(1)))
        
        output = re.sub(self.entity_name_matcher, name_converter, input)
        output = re.sub(self.entity_cp_matcher, cp_converter, output)
        
        return output
    
    def get_data(self):
        stream = urllib.urlopen(self.URL)
        
        raw_lines = stream.readlines()
        
        stream.close()
        
        limit_date = getattr(self, 'limit_date', datetime.date(2000, 1, 1))
        
        new_data = []
        
        for raw_line in raw_lines:
            raw_line = raw_line.strip()
            
            match = self.line_matcher.search(raw_line)
            
            if not match:
                continue
            
            date = datetime.datetime.strptime(match.group('date'), self.LINE_DATE_FORMAT).date()
            
            if date < limit_date:
                continue
            
            fact = Fact()
            fact.date = date
            fact.text = self._entity2unichr(match.group('fact')).strip()
            
            new_data.append(fact)
           
        return new_data


# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------
class FactsComponentConfig(Config):
    identifier = 'components.facts'
        
    def valid_keys(self):
        return [
            'lastRetrievalDate',
            'retrievalInterval'
        ]
    
    def default_values(self):
        return {
            'lastRetrievalDate' : datetime.date(2011,1,1),
            'retrievalInterval' : TIME_HOUR * 8
        }
