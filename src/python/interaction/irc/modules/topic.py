# -*- coding: UTF-8 -*-
'''
Created on 27.01.2012

@author: rack
'''
import logging
import random

from datetime import date

from interaction.irc.module import InteractiveModule, InteractiveModuleCommand, InteractiveModuleResponse
from components.topic import TopicNotFound, AdditionNotFound, NoAdditionAvailable, NoAffectedRows

#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------
BOT_IS_OPERATOR = 2
RANDOM_YEAR_START = 1983
RANDOM_YEAR_END = 2020
DEFAULT_TOPIC = 'Willkommen im Sammelbecken für sozial Benachteiligte'
#-------------------------------------------------------------------------------
# Module 'Logic'
#-------------------------------------------------------------------------------
class Topic(InteractiveModule):
    """
    This module provides topic functions    
    """
    def initialize(self):
        """
        Initialize the module.
        """       
        self.me = self.client.me
        self.logger = logging.getLogger('interaction.irc.topic')
        self.component = self.client.bot.get_subsystem('topic-component')

        
    def module_identifier(self):
        """
        Declare the module identifier.
        """
        return 'TopicMod'
    
    def init_commands(self):
        return [
                InteractiveModuleCommand(
                                         keyword='topic',
                                         callback=self.display_current_topic
                                         ),
                InteractiveModuleCommand(
                                         keyword='settopic',
                                         callback=self.set_new_topic,
                                         pattern=r'^(.+)$',
                                         syntaxhint='<new topic>'
                                         ),
                InteractiveModuleCommand(
                                         keyword='addtopic',
                                         callback=self.add_new_addition,
                                         pattern=r'^(.+)$',
                                         syntaxhint='<addition>'
                                         ),
                InteractiveModuleCommand(
                                         keyword='deltopic',
                                         callback=self.del_addition,
                                         pattern=r'^(.+)$',
                                         syntaxhint=r'<id>'
                                         ),
                InteractiveModuleCommand(
                                         keyword='listtopic',
                                         callback=self.display_topic_additions
                                         )
                ]
    
    def display_current_topic(self, request):
        """
        Display the current topic.
        
        Usage: .topic
               
        @return InteractiveModuleResponse
        """
        response = InteractiveModuleResponse()
        
        try:
            topic = self.component.get_last_topic()           
            topic_string = self.component.create_topic_string(topic.text,topic.addition.text,topic.year)
            response.add_line('{0} set by {1}'.format(topic_string,topic.user))
        except TopicNotFound:
            response.add_line("No topic available.")
        
        return response
    
    def set_new_topic(self, request):
        """
        Change the topic of a channel.
        
        Usage: .settopic <text|'reset'>
        If the module receive the string 'reset', it will set the default topic
        
        @param request: A runtime request of an InteractiveModule command.
        
        @return InteractiveModuleResponse 
        """        
        response = InteractiveModuleResponse()
        
        #Normally, here I would check if there was set the mode +t in channel modes
        #because if it was set, I won't need to check the userMode.
        #But get_modes() is not implemnted, yet :(
        #channelModes = channelObject.get_modes()
        
        channel_object = self.usermgmt.chanlist.get(request.target)
        userMode = channel_object.get_user_mode(self.me.source.nickname)
        try:
            if (userMode == BOT_IS_OPERATOR):
                text = request.parameter[0]
                
                if (text == 'reset'): #default topic
                    text = DEFAULT_TOPIC
    
                addition = self.component.get_random_addition().text
                year = random.randint(RANDOM_YEAR_START,RANDOM_YEAR_END)
                               
                topic_cmd = self.client.get_command('Topic').get_sender()  
                topic_cmd.channel = request.target
                topic_cmd.topic = self.create_topic_string(text,addition,year)
                topic_cmd.send()
                
                self.component.insert_topic(text,addition,year,request.source.nickname)                                
            else:
                response.add_line("Bot needs to be an operator to do this.")
        except NoAdditionAvailable:
                response.add_line("There are no topic additions available at the moment.")

        return response
    
    
    def add_new_addition(self, request):
        """
        Insert a new addition to database
        
        Usage: .addtopic <addtion(text)>
        
        @param request: A runtime request of an InteractiveModule command.
        
        @return InteractiveModuleResponse
        """
        response = InteractiveModuleResponse()
        self.component.insert_addition(request.parameter[0],request.source.nickname)
        response.add_line("The process was successful.")
        
        return response
    
    
    def del_addition(self, request):
        """
        Delete a addition with the given id.
        
        .deltopic <id>
        
        @param request: A runtime request of an InteractiveModule command.
        
        @return: InteractiveModuleResponse
        """
        response = InteractiveModuleResponse()               

        try:
            id = int(request.parameter[0])
            self.component.delete_addition_by_id(id)
            response.add_line("Delete was successful.")
        except NoAffectedRows:
            response.add_line("No entry was deleted.")
        except ValueError:
            response.add_line("Please enter a valid ID!")
        
        return response
        
                    
    def display_topic_additions(self, request):
        """
        Send a link to a list with all additions.
        
        Usage: .listtopic
        
        @return: InteractiveModuleResponse
        """
        return InteractiveModuleResponse("www.derlinkfehltnoch.de")
    
    
    def create_topic_string(self,text,addition,year):
        """
        Return a formated topic string with text, addition and year
        
        @param text: a topic text
        @param addition: an addition text
        @param year: a year for the second addition part
        
        @return: formated string
        """          
        if (year <= date.today().year):
            since_until = "since"
        else:
            since_until = "until"
            
        return "127,1.:. Welcome� 7,1� 14,1F4,1=15,1O7,1=0,1P" \
             + "7,1=0,1T7,1=0,1I7,1=15O4,1=14,1N 7,1�" \
             + " 7,14Topic: {0} 47,1� {1} {2} {3}! .:.".format(text, addition, since_until, year)