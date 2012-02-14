# -*- coding: UTF-8 -*-
'''
Created on 27.01.2012

@author: rack


'''
#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------
import logging
import random
from interaction.irc.module import InteractiveModule, InteractiveModuleCommand, InteractiveModuleResponse, InteractiveModuleRequest
from components.topic import DataNotFound, NoDataAvailable
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
        """
        try:
            topic = self.component.get_last_topic()
            topic_text = topic.text
            topic_addition = topic.topicaddition.text
            topic_year = topic.year
            topic_user = topic.user
            
            topic_string = self.component.create_topic_string(topic_text,topic_addition,topic_year)
            return InteractiveModuleResponse('{0} set by {1}'.format(topic_string,topic_user))
        except NoDataAvailable:
            return InteractiveModuleResponse("No topic available.")
        
    
    def set_new_topic(self, request):
        """
        Change the topic of a channel.
        
        .settopic <'text'|reset>
        """
        
        #Normally, here I would check if there was set the mode +t in channel modes
        #because if it was set, I won't need to check the userMode.
        #But get_modes() is not implemnted, yet :(
        #channelModes = channelObject.get_modes()
        
        channel_name = request.event.parameter[0]
        channel_object = self.usermgmt.chanlist.get(channel_name)
        userMode = channel_object.get_user_mode(self.client.me.source.nickname)
        try:
            if (userMode == 2):
                topic_text = request.parameter[0]
                
                if (topic_text == 'reset'): #standard topic
                    topic_text = 'Willkommen im Sammelbecken für sozial Benachteiligte'
    
                topic_addition = self.component.get_rnd_addition()
                topic_year = random.randint(1983,2020)
                topic_user = request.event.source.nickname
                self.component.insert_topic(topic_text,topic_addition,topic_year,topic_user)
            
                topic_addition_text = topic_addition.text
                topic_string = self.component.create_topic_string(topic_text,topic_addition_text,topic_year)
                        
                topic_cmd = self.client.get_command('Topic').get_sender()              
                topic_cmd.channel = channel_name
                topic_cmd.topic = topic_string
                topic_cmd.send()
            else:
                return InteractiveModuleResponse("Bot needs to be an operator to do this.")
        except NoDataAvailable:
            return InteractiveModuleResponse("There are no topic additions available at the moment.")
    
    
    def add_new_addition(self, request):
        """
        Insert a new addition to database
        
        .addtopic <addtion>
        """
        
        topic = request.parameter[0]
        nickname = request.event.source.nickname
        try:
            self.component.insert_addition(topic,nickname)
            return InteractiveModuleResponse("The process was successful.")
        except DataNotFound:
            return InteractiveModuleResponse("There is no addition with the given ID.")
    
    
    def del_addition(self, request):
        """
        Delete a addition.
        
        .deltopic <id>
        """               
        addition = request.parameter[0]
        try:
            id = int(addition)
            self.component.delete_addition_by_ID(id)
            return InteractiveModuleResponse("Delete was successful.")
        except DataNotFound:
            return InteractiveModuleResponse("An entry with the given ID was not found.")
        except:
            return InteractiveModuleResponse("Please enter a valid ID!")
        
                    
    def display_topic_additions(self, request):
        """
        Send a link to a list with all additions.
        """
        return InteractiveModuleResponse("www.derlinkfehltnoch.de")
        