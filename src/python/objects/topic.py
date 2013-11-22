'''
Created on 27.01.2012

@author: rack
'''

from sqlalchemy import Column, Integer, DateTime, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import ForeignKey

from core.persistence import SqlAlchemyPersistence

class Topic(SqlAlchemyPersistence.Base):
    """
    Represent an individual topic for the topic component
    """
    
    __tablename__ = 'topics'
    
    #DLL
    id = Column(Integer, primary_key=True)
    addition_id = Column(Integer, ForeignKey('topicadditions.id'))
    date = Column(DateTime)
    text = Column(Text)
    year = Column(Integer)
    user = Column(Text)
    
    #ORM - one-to-many
    addition = relationship('TopicAddition', backref=backref('topics'))
    
    def __repr__(self):
        return '<Topic(id={0}|date={1}|text={2}|year={3}|user={4})>'.format(
            self.id,
            self.date,
            self.text,
            self.year,
            self.user
        )
    
class TopicAddition(SqlAlchemyPersistence.Base):
    """
    Represent an addition for the topic component
    """
    
    __tablename__ = 'topicadditions'
    
    #DLL
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    text = Column(Text)
    user = Column(Text)
       
    def __repr__(self):
        return '<TopicAddition(id={0}|date={1}|text={2}|user={3})>'.format(
            self.id,
            self.date,
            self.text,
            self.user,
        )