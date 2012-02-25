# -*- coding: UTF-8 -*-
'''
Created on 24.02.2012

@author: rack

TODO: - limit .delquote to admin only?
'''
import logging

from interaction.irc.module import InteractiveModule, InteractiveModuleCommand, InteractiveModuleResponse
from components.quote import NoQuoteAvailable, NoAffectedRows

#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------
MAX_LENGTH_QUOTE = 375
#-------------------------------------------------------------------------------
# Module 'Logic'
#-------------------------------------------------------------------------------
class Quote(InteractiveModule):
    """
    This module provides quote functions
    """
    def initialize(self):
        self.me = self.client.me
        self.logger = logging.getLogger('interaction.irc.quote')
        self.component = self.client.bot.get_subsystem('quote-component')

    
    def module_identifier(self):
        """
        Declare the module identifier.
        """
        return 'QuoteMod'
    
    
    def init_commands(self):
        """
        Declare all commands of the module.
        """
        return [
                InteractiveModuleCommand(
                                         keyword='addquote',
                                         callback=self.add_new_quote,
                                         pattern=r'^(.+)$',
                                         syntaxhint='<text>'
                                         ),
                InteractiveModuleCommand(
                                         keyword='delquote',
                                         callback=self.del_quote,
                                         pattern=r'^(\d+)$',
                                         syntaxhint='<id>'
                                         ),
                InteractiveModuleCommand(
                                         keyword='quote',
                                         callback=self.display_quote,
                                         pattern=r'^(.+)$|^$',
                                         syntaxhint='<id|text>'
                                         ),
                InteractiveModuleCommand(
                                         keyword='searchquote',
                                         callback=self.search_quotes,
                                         pattern=r'^(.+)$',
                                         syntaxhint='<text>'
                                         )
                ]
        
    
    def display_quote(self, request):
        """
        Select a quote from database and post it to a channel.
        
        Usage: .quote [<text>|<id>]
        
        @param request: A runtime request of an InteractiveModule command.
        
        @return InteractiveModuleResponse
        """
        response = InteractiveModuleResponse()
        
        try:
            text = request.parameter[0]
            if (len(text) > 0):
                try:
                    id = int(text)
                    quote = self.component.get_quote_by_id(id)
                except ValueError:
                    quote = self.component.get_random_quote_by_string(request.parameter[0])
            else:
                quote = self.component.get_random_quote()
             
            response.add_line("{0} ({1})".format(quote.text,quote.id))
        except NoQuoteAvailable:
            response.add_line("No quotes in database.")
            
        return response
    
    
    def add_new_quote(self, request):
        """
        Add a new quote to database.
        Max length of the quote is 375 letters.
        
        Usage: .addquote <text>
        
        @param request: A runtime request of an InteractiveModule command.
        
        @return InteractiveModuleResponse
        """
        response = InteractiveModuleResponse()
        
        text = request.parameter[0]
        if len(text) <= MAX_LENGTH_QUOTE:
            self.component.insert_quote(text,request.source.nickname)
            response.add_line("The process was successful.")
        else:
            response.add_line("Max length of a quote is {0} letters. Yours is {1}."
                              .format(MAX_LENGTH_QUOTE,str(len(text))))
        
        return response
    
    
    def del_quote(self,request):
        """
        Delete a quote with the given id from database.
        
        Usage: .delquote <id>
        
        @param request: A runtime request of an InteractiveModule command.
        
        @return InteractiveModuleResponse
        """
        response = InteractiveModuleResponse()   
        try:
            id = int(request.parameter[0])
            self.component.delete_quote_by_id(id)
            response.add_line("Delete was successful.")
        except ValueError:
            response.add_line("If you like to delete a quote, you'll have to declare an ID instead of a string.")
        except NoAffectedRows:
            response.add_line("Delete didn't work. Maybe, there isn't a quote with the given ID.")    
 
        return response
    
    
    def search_quotes(self,request):
        """
        Search in database for quote with the given string.
        It will display all IDs of the founded quotes
        
        Usage: .searchquote <text>
        
        @param request: A runtime request of an InteractiveModule command.
        
        @return InteractiveModuleResponse
        """
        response = InteractiveModuleResponse()
        
        ids = self.component.get_ids_by_string(request.parameter[0])
        if len(ids) > 0:
            response.add_line("Found the string in following quotes: {0}".format(" ".join(str(ids))))
        else:
            response.add_line("There isn't a quote with the given id.")
        
        return response    