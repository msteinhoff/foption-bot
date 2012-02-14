# -*- coding: UTF-8 -*-
'''
Created on 30.01.2012

@author: rack
'''

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------
import logging
from core import runlevel
from core.component import Component, ComponentError
from core.config import Config
from datetime import date
from objects.topic import TopicAddition, Topic
from sqlalchemy import func,desc

#-------------------------------------------------------------------------------
# Exceptions
#-------------------------------------------------------------------------------
class TopicComponentError(ComponentError): pass
class DataNotFound(TopicComponentError): pass
class NoDataAvailable(TopicComponentError): pass
#-------------------------------------------------------------------------------
# Business Logic
#-------------------------------------------------------------------------------
class TopicComponent(Component):
        RUNLEVEL = runlevel.Runlevel(
        autoboot=True,
        minimum_start=runlevel.LOCAL_COMPONENT
    )
    
        def __init__(self, bot):
            Component.__init__(self, bot)
            self.bot = bot        
            self.logger = logging.getLogger('components.topic') 
            self.sqlite = self.bot.get_subsystem('local-persistence')

                   
        def insert_addition(self, text, user):
            """
            Insert a new addition to database.
            """
            added_at = date.today()
            addition = TopicAddition(date=added_at, text=text, user=user)
            session = self.sqlite.get_session()              
            session.add(addition)
            session.commit()
        
        
        def get_rnd_addition(self):
            """
            Return a random selected addition.
            """
            session = self.sqlite.get_session()
            additions = session.query(TopicAddition).order_by(func.random()).limit(1)
            
            try:           
                return additions[0] #fetchone() didn't work oO
            except:
                raise NoDataAvailable
                            
        
        def delete_addition_by_ID(self,id):
            """
            Delete a topic addition with the given id.
            """
            session = self.sqlite.get_session()       
            affectedRows = session.query(TopicAddition).filter(TopicAddition.id==id).delete()
            session.commit()
            
            if (affectedRows < 1):
                raise DataNotFound

        
        def insert_topic(self,text,addition,year,user):
            """
            Insert a new topic
            """
            topic = Topic(date=date.today(),text=text,year=year,user=user)
            topic.topicaddition = addition
            session = self.sqlite.get_session()
            session.add(topic)
            session.commit()
        
        
        def get_last_topic(self):
            """
            Returns the current topic
            
            """
            session = self.sqlite.get_session()
            topics = session.query(Topic).order_by(desc(Topic.id)).limit(1)
            
            try:         
                return topics[0] #fetchone() didn't work oO
            except:
                raise NoDataAvailable
        
        
        def create_topic_string(self,text,addition,year):
            """
            Return a formated topic string with text, addition and year
            """          
            if (year <= date.today().year):
                since_until = "since"
            else:
                since_until = "until"
            
            #should I export the string to config?    
            return "127,1.:. Welcome� 7,1� 14,1F4,1=15,1O7,1=0,1P" \
                 + "7,1=0,1T7,1=0,1I7,1=15O4,1=14,1N 7,1�" \
                 + " 7,14Topic: {0} 47,1� {1} {2} {3}! .:.".format(text, addition, since_until, year)
#-------------------------------------------------------------------------------
# Config
#-------------------------------------------------------------------------------        
class TopicComponentConfig(Config):
    identifier = 'components.topic'