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

from core.config import Config
from core.component import Component, ComponentError
from objects.principal import Principal, Role

# ------------------------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------------------------
class PrincipalComponentError(ComponentError): pass

# ------------------------------------------------------------------------------
# Business Logic
# ------------------------------------------------------------------------------
class PrincipalComponent(Component):
    def __init__(self, bot):
        self.bot = bot
        
        self.bot.register_config(PrincipalComponentConfig)
        
        self.config = self.bot.get_config('components.principal')
        self.logger = self.bot.get_logger('components.principal')
    
    def find_principal_by_id(self, id):
        pass
    
    def insert_principal(self, principal):
        pass
    
    def update_principal(self, principal):
        pass
    
    def delete_principal(self, id):
        pass
    
# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------
class PrincipalComponentConfig(Config):
    identifier = 'components.principal'
        
    def valid_keys(self):
        return []
    
    def default_values(self):
        return {}
