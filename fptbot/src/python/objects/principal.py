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

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship, backref

from core.persistence import SqlAlchemyPersistence

class Principal(SqlAlchemyPersistence.Base):
    """
    Represent a principal for the principal component.
    
    SQLAlchemy mapped class.
    """
    
    __tablename__ = 'principals'
    
    id = Column(Integer, primary_key=True)
    login = Column(String(32))
    password = Column(String(255))
    role = Column(Integer)
    disabled = Column(Boolean)

class Nickname(SqlAlchemyPersistence.Base):
    """
    Represent a IRC nickname associated with a principal.
    
    SQLAlchemy mapped class.
    """
    
    __tablename__ = 'nicknames'
    
    nickname = Column(String(32), primary_key=True)
    principal_id = Column(Integer, ForeignKey('principals.id'), nullable=True)
    
    principal = relationship(Principal, backref=backref('nicknames', order_by=nickname))

class Role(object):
    """
    Represent a role.
    
    Right.USER   = 1
    Right.AUTHED = 2
    Right.ADMIN  = 4
    
    TODO: rework role/rights concept.
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

    @staticmethod
    def string(role):
        """
        Return the string representation of the given role.
        
        @param role: The role.
        
        @return The role string.
        """
        
        strings = {
            1: 'User',
            2: 'Authenticated',
            3: 'Authenticated',
            4: 'Administrator',
            7: 'Administrator'
        }
        
        return strings[role]

class Right(object):
    """
    Represents an individual right. (read, write, delete, etc)
    """
    def __init__(self, name=None, mask=None):
        self.name = name
        self.mask = mask

