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

@since Mar 15, 2010
@author rack
"""

import random
import re
import datetime

from twitter import Twitter
from system import file2obj,obj2file,PrivMsg,ServerMsg
from config import Config

"""
    
        # TODO move to topic module
        self.TopicChanger = "Q"
        self.Topic = "" #Performance boost
"""

class Topic():
    regexpattern = r':(.+) (?:332 (?:.+)|(PRIVMSG|TOPIC)) ([\S]+) :((.topic|.addtopic|.deltopic|.listtopic|topic\?)(?: (.+)|$)|(?:(.+)$))'
    
    '''
    The module can change the topic of a channel on QuakeNet. In addition, the module posts
    the new topic on twitter.
    '''
        
    def __init__(self):
        self.Config = Config()
        self.FilenameDB = "db/topic.db" #Datenbank der Topic adds
        self.FilenameTxtlist = "../public_html/topic.txt"
        self.Twitter = Twitter("","")
        self.TopicDB = file2obj(self.FilenameDB)

    
    def handleInput(self,Matchlist):
        Source = Matchlist[0]
        Target = Matchlist[2]
        if (Matchlist[1] == ""):
            Topictext = Matchlist[3]
            self.Config.Topic = Topictext
        elif (Matchlist[1] == "TOPIC"):
            Topictext = Matchlist[3].strip()
            LastTopicNick = re.search("(.+?)!",Source).group(1)
            if (LastTopicNick != "Q"):
                self.Config.TopicChanger = LastTopicNick
                self.Config.Topic = Topictext
                self.Twitter.sendTweet("[" + LastTopicNick + "] " + Topictext.strip())
        else:
            Keyword = Matchlist[4]
            Text = Matchlist[5].split()
            if (Keyword == "topic?"):
                PrivMsg(Target, str(self.getTopic()))
            elif (Keyword == ".listtopic"):
                PrivMsg(Target, self.getTopicList())
            if (len(Text) > 0):
                if (Keyword == ".topic"):
                    Postnick = re.match("(.+?)!",Source).group(1)
                    ServerMsg("PRIVMSG Q :settopic " + Target + " " \
                                 + self.setTopic(Postnick," ".join(Text[0:])))
                elif (Keyword == ".addtopic"):
                    PrivMsg(Target,self.addTopic(" ".join(Text[0:])))
                elif (Keyword == ".deltopic"):
                    PrivMsg(Target, self.delTopic(" ".join(Text[0:])))
            
    
    #returns the topic        
    def getTopic(self):    #Einfache Topicr�ckgabe
        return self.Config.Topic + " set by " + self.Config.TopicChanger


    def isStandardTopic(self):
        if ("" in self.Config.Topic):
            return True
        return False
    

    #this method sets the topic
    def setTopic(self,Source,String):
        #Max 140 chars, because the max length of a twitter "tweet" is 140 chars  
        if (len(String)+len(Source)+3 > 140):
            return ("Diese Topic ist zu lang! Max 140 Zeichen. Deine Topic hat "
            + str(len(String)+len(Source)+3) + " Zeichen!")
        if (String == "reset"):
            TopicMsg = ""
        else:    
            TopicMsg = String.strip()
            self.Twitter.sendTweet("[" + Source + "] " + TopicMsg)
        
        #random addition for the topic
        x = len(self.TopicDB)
        TopicAddition = self.TopicDB[random.randrange(x)]
        Year = random.randint(1983,2020)
        self.Config.Topic = "127,1.:. Welcome� 7,1� 14,1F4,1=15,1O7,1=0,1P" \
                          + "7,1=0,1T7,1=0,1I7,1=15O4,1=14,1N 7,1�" \
                          + " 7,14Topic: " + TopicMsg + " 47,1� " + TopicAddition \
                          + " " + ("since" if Year <= datetime.date.today().year else "until") \
                          + " " + str(Year) + "! .:."
        
        self.Config.TopicChanger = Source
        return self.Config.Topic

    #for adding topic-additions
    def addTopic(self,String):
        self.TopicDB.append(String)
        obj2file(self.TopicDB,self.FilenameDB)
        self.writeTXTList()
        return "15Topicmodul: 7 '" + String + "' wurde zur Liste hinzugef�gt."

    #for deleting topic-additions
    def delTopic(self,String):
        for i in self.TopicDB:
            if (i == String):
                self.TopicDB.remove(String)
                obj2file(self.TopicDB,self.FilenameDB)
                self.writeTXTList()
                return "15Topicmodul: 7 '"+ String + "' wurde entfernt."

        return "15Topicmodul: 7 '"+ String + "' konnte nicht entfernt werden, da der String nicht vorhanden ist."

    
    def writeTXTList(self):
        '''
        This method write a text file with the topic additions.
        Each addition gets his own line
        '''#
        
        self.TopicDB.sort(key=str.lower)
        
        TXT = ""
        for i in self.TopicDB:
            TXT += i + "\n"
        
        File = open(self.FilenameTxtlist, 'w')
        File.writelines(TXT)
        File.close

        
    #link to the topic addition
    def getTopicList(self):
        return ""