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

@since Jan 11, 2011
@author Mario Steinhoff
"""

from core.config            import Config

from interaction.irc.module import Module
from interaction.irc.client import Message, Privilege

from 

moduleName = "InfoModule"

class InfoModule(Module):
    '''
    Provide general information to users.
    '''

    class Config(Config):
        def __init__(self, persistence):
            valid = [
                "help_url",
                "twitter_url",
                "info_url",
                "ts_address",
                "ts_port",
                "ts_password"
            ]
            
            Config.__init__("module-admin", persistence, valid);
    
    def __init__(self, bot):
        commands = [
            (Message.PRIVMSG_CHANNEL, Message.PRIVMSG_CHANNEL, Privilege.USER,  'help',           self.displayHelpURL),
            (Message.PRIVMSG_CHANNEL, Message.PRIVMSG_CHANNEL, Privilege.USER,  'info',           self.displayInfoURL),
            (Message.PRIVMSG_CHANNEL, Message.PRIVMSG_CHANNEL, Privilege.USER,  'twitter',        self.displayTwitterURL),
            (Message.PRIVMSG_CHANNEL, Message.NOTICE,          Privilege.USER,  'ts3',            self.displayTeamspeakData),
            (Message.PRIVMSG_CHANNEL, Message.NOTICE,          Privilege.USER,  'todo',           self.addTodoEntry),
            
            (Message.PRIVMSG_USER,    Message.NOTICE,          Privilege.ADMIN, 'modlist',        self.displayModuleList),
            (Message.PRIVMSG_USER,    Message.NOTICE,          Privilege.ADMIN, 'ts3-updateaddr', self.updateTeamspeakAddress),
            (Message.PRIVMSG_USER,    Message.NOTICE,          Privilege.ADMIN, 'ts3-updatepw',   self.updateTeamspeakPassword),
        ]
        
        Module.__init__(bot, commands)
        
    def displayHelpURL(self, event, data):
        message = ""
    
    def displayInfoURL(self, event, data):
        message = ""
    
    def displayTwitterURL(self, event, data):
        message = ""
    
    def dislayModuleList(self, event, data):
        List = ""
        
        for i in InstanceModlist:
            try:
                r = re.search('<(?:.+)\.(.+?) instance at (?:.+)>',str(i)).group(1)
                List += (", " if List != "" else "") + "'" + r + "'"
            except:
                pass

    def displayTeamspeakData(self, event, data):
        message = "Address: %s:%s - Password: %s" % (
            self._config.ts_address,
            self._config.ts_port,
            self._config.ts_password
        )

    def updateTeamspeakAddress(self, address):
        try:
            matchlist = re.search("^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$",Text[1]).group(1,2,3,4)
        except:
            message = "Address: Ungültige IP-Adresse. Buchstabe in der IP"
            
        try:
            matchlist = re.search("^(\d{1,5})$",Text[1]).group(1)
        except:
            message = "Ungültiger Port! Deine Angabe enthält Zeichen oder ist zu lang."

        for i in matchlist:
            if int(i) > 255:
                message = "Address: Ungültige IP-Adresse. Zu Hohe Zahlen"
                return
                
        if int(matchlist) > 65536:
            message =  "Ungültiger Port! Port muss zwischen 1-65536 liegen"
            return

            
            self._config.ts_address = Text[1]
            self._config.ts_port = re.search("^(\d{1,5})$",Text[1]).group(1)
    
    def updateTeamspeakPassword(self, event, data):
        self._config.ts_password = data
    
    def addTodoEntry(self, event, data):
        self.Filename = "../public_html/fptbot.txt"
        Source = re.match("(.+?)!",Source).group(1)
        File = open(self.Filename, "a")
        File.write("\t" + Text + "\t\trequested by " + Source + "\n")
        File.close
        
        message = "Auftrag wurde gespeichert!"

        