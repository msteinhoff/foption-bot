'''
Created on 21.02.2012

@author: rack
'''

from sqlalchemy import Column, Integer, DateTime, Text
from core.persistence import SqlAlchemyPersistence

class Quote(SqlAlchemyPersistence.Base):
    """
    Represent a quote.
    """
    
    __tablename__ = 'quotes'
    
    #DLL
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    text = Column(Text)
    user = Column(Text)
    
    def __repr__(self):
        return '<Quote(id={0}|date={1}|text={2}|user={3})>'.format(
            self.id,
            self.date,
            self.text,
            self.user
        )