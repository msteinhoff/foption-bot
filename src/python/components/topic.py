# -*- coding: UTF-8 -*-
'''
Created on 30.01.2012

@author: rack
'''

import logging

from sqlalchemy import func,desc
from sqlalchemy.orm.exc import NoResultFound
from datetime import date

from core import runlevel
from core.component import Component, ComponentError
from core.config import Config
from objects.topic import TopicAddition, Topic

#-------------------------------------------------------------------------------
# Exceptions
#-------------------------------------------------------------------------------
class TopicComponentError(ComponentError): pass
class TopicNotFound(TopicComponentError): pass
class AdditionNotFound(TopicComponentError): pass
class NoAdditionAvailable(TopicComponentError): pass
class NoAffectedRows(TopicComponentError): pass 

#-------------------------------------------------------------------------------
# Business Logic
#-------------------------------------------------------------------------------
class TopicComponent(Component):
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
        self.logger = logging.getLogger('components.topic') 
        self.persistence = self.bot.get_subsystem('local-persistence')

               
    def insert_addition(self, text, user):
        """
        Insert a new addition to database.
        
        @param text: the real addition text
        @param user: the person who likes to add the addition
        
        @return: None
        """
        added_at = date.today()
        addition = TopicAddition(date=added_at, text=text, user=user)
        
        session = self.persistence.get_session()              
        session.add(addition)
        session.commit()
    
    
    def get_random_addition(self):
        """
        Return a random selected addition.
        
        @return: entity of addition
        
        @raise NoAdditionAvailable if there is an empty database
        """
        try:
            session = self.persistence.get_session()
            addition = session.query(TopicAddition).order_by(func.random()).limit(1).one()
            return addition
        except NoResultFound:
            raise NoAdditionAvailable
                        
    
    def delete_addition_by_id(self,id):
        """
        Delete a topic addition with the given id.
        
        @param id: number of the addition which will be deleted
        
        @return: None
        
        @raise AdditionNotFound if there is no addition with the given id
        @raise DeleteDidntWork if sqlalchemy couldn't perform the deleting 
        """
        
        session = self.persistence.get_session()      
        affected_rows = session.query(TopicAddition).filter(TopicAddition.id==id).delete()
        session.commit()

        if (affected_rows < 1): 
            raise NoAffectedRows
        
    
    def insert_topic(self,text,addition,year,user):
        """
        Insert a new topic.
        
        @param text: the real topic text
        @param addition: an entity of addition
        @param year: a (randomly) generated year for the topic addition
        @param user: the name of the user who likes to add the topic
        
        @return: None
        """
        topic = Topic(date=date.today(),text=text,year=year,user=user)
        topic.addition = addition
        
        session = self.persistence.get_session()
        session.add(topic)
        session.commit()
    
    
    def get_last_topic(self):
        """
        Return the current topic
        
        @return: an entity of topic
        
        @raise TopicNotFound if there isn't a topic in database
        """
        try:
            session = self.persistence.get_session()
            topic = session.query(Topic).order_by(desc(Topic.id)).limit(1).one()
            return topic
        except NoResultFound:
            raise TopicNotFound
        
#-------------------------------------------------------------------------------
# Config
#-------------------------------------------------------------------------------        
class TopicComponentConfig(Config):
    identifier = 'components.topic'