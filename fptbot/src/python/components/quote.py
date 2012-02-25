'''
Created on 22.02.2012

@author: rack
'''

import logging

from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from datetime import date

from core import runlevel
from core.component import Component, ComponentError
from objects.quote import Quote

#-------------------------------------------------------------------------------
# Exceptions
#-------------------------------------------------------------------------------
class QuoteComponentError(ComponentError): pass
class NoQuoteAvailable(QuoteComponentError): pass
class NoAffectedRows(QuoteComponentError): pass 

#-------------------------------------------------------------------------------
# Business Logic
#-------------------------------------------------------------------------------
class QuoteComponent(Component):
    RUNLEVEL = runlevel.Runlevel(
    autoboot=True,
    minimum_start=runlevel.LOCAL_COMPONENT
    )
    
    def __init__(self, bot):
        """
        Initialize all required variables.
        """
        Component.__init__(self, bot)
        
        self.bot = bot        
        self.logger = logging.getLogger('components.quote') 
        self.persistence = self.bot.get_subsystem('local-persistence')
        
        
    def insert_quote(self,text,user):
        """
        Insert a new quote to database
        
        @param text: the quote text
        @param user: the person who likes to add the quote
        
        @return: None
        """
        added_at = date.today()
        quote = Quote(date=added_at, text=text, user=user)
        
        session = self.persistence.get_session()
        session.add(quote)
        session.commit()

    
    def delete_quote_by_id(self,id):
        """
        Delete a quote with the given id
        
        @param  id: number of the quote which will be deleted
        
        @return: None
        
        @raise NoAffectedRows if sqlalchemy couldn't perform the deleting
        """        
        session = self.persistence.get_session()      
        affected_rows = session.query(Quote).filter(Quote.id==id).delete()
        session.commit()

        if (affected_rows < 1): 
            raise NoAffectedRows

    
    def get_quote_by_id(self,id):
        """
        Return a quote with the given id
        
        @param id: identifier of the quote which will be deleted
        
        @return None
        
        @raise NoQuoteAvailable if there is no quote with the given id
        """
        try:
            session = self.persistence.get_session()
            quote = session.query(Quote).filter(Quote.id==id).one()
            return quote
        except NoResultFound:
            raise NoQuoteAvailable
    
    
    def get_random_quote_by_string(self,string):
        """
        Retrun a random selected quote which have the given string in it.
        """
        try:
            session = self.persistence.get_session()
            quote = session.query(Quote).filter(Quote.text.like('%{0}%'.format(string))).order_by(func.random()).limit(1).one()
            return quote
        except NoResultFound:
            raise NoQuoteAvailable
            
        
    
    def get_ids_by_string(self,string):
        """
        Returns all quote ids which have the given string.
        
        @param string: The string you are looking for.
        
        @return: array of IDs 
        """
        session = self.persistence.get_session()
        quotes = session.query(Quote).filter(Quote.text.like('%{0}%'.format(string))).all()
        ids = []
        
        for x in quotes:
            ids.append(x.id)
            
        return ids

    
    def get_random_quote(self):
        """
        Return a random selected quote.
        
        @return: entity of quote
        
        @raise NoQuoteAvailable if there is an empty database
        """
        try:
            session = self.persistence.get_session()
            quote = session.query(Quote).order_by(func.random()).limit(1).one()
            return quote
        except NoResultFound:
            raise NoQuoteAvailable