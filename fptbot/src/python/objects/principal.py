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

@since Apr 26, 2011
@author Mario Steinhoff
"""

__version__ = '$Rev$'

class Principal(object):
    def __init__(self, login=None, password=None, role=None):
        self.login = login
        self.password = password
        self.role = role


class Right(object):
    def __init__(self, name=None, mask=None):
        self.name = name
        self.mask = mask


class Role(object):
    """
    Represent a role.
    
    Right.USER   = 1
    Right.AUTHED = 2
    Right.ADMIN  = 4
    
    TODO: need real object here or maybe move to own python module?
    """
    
    USER   = 1 # Right.USER
    AUTHED = 3 # Right.USER | Right.AUTHED
    ADMIN  = 7 # Right.USER | Right.AUTHED | Right.ADMIN
    
    def __init__(self):
        """
        This class may currently not be instantiated. 
        """
        
        raise NotImplementedError
    
    @staticmethod
    def valid(required, role):
        """
        Check whether the user role contains sufficient rights.
        
        @param required: The minimum rights to validate.
        @param role: The actual rights.
        
        @return True if there are sufficient rights, False otherwise.
        """
        
        return (required & role == required) 
