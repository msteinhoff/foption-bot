# -*- coding: UTF-8 -*-

'''
Created on 26.03.2010

@author: rack
'''

import tinyurl
import re

from twitter import Twitter
from youtube import YouTube

from system import PrivMsg

class Funlink():
    regexpattern = r':(.+) (?:PRIVMSG) ([\S]+) :.addurl(?: (.+))'
    
    def __init__(self):
        self.Twitter = Twitter("","")
        self.YouTube = YouTube()
        
    def handleInput(self,Matchlist):
        Source = Matchlist[0]
        Target = Matchlist[1]
        Text = Matchlist[2].split()
        
        try:
            URL = tinyurl.create_one(Text[0])
        except Exception:
            PrivMsg(Target,"4Error in 'TINYURL.Modul' >> '" + str(Exception) + "'")
            return
        
        Nick = re.match("(.+?)!", Source).group(1)
        
        if (len(Text) >= 2) or (re.search("(?:.+)youtube.com/(?:.+)v=(\w+)",Text[0]) and len(Text) == 1): #Beschreibung mit angegeben            
            x = "[" + Nick + "] "
            
            #Zusatzinformation ermitteln, wie [YouTube] [PNG] [TIF]
            if (re.search("(?:.+)youtube.com/(?:.+)v=(\w+)",Text[0])):
                x += "[YouTube] "
            elif (re.search("(\w+).rofl.to",Text[0])):
                r = re.search("(\w+).rofl.to",Text[0]).group(1)
                x += "[rofl.to] (" + str(r) +") "
            elif (re.search("collegehumor.com/(\w+)",Text[0])):
                r = re.search("collegehumor.com/(\w+)",Text[0]).group(1)
                x += "[CollegeHumor] (" + str(r) + ")"
            elif (re.search("newgrounds.com/",Text[0])):
                x += "[Newsground] "
            else:
                try:
                    Tag = re.search("\.(bmp|jpg|gif|img|jp2|jpeg|png|psd|tga|tif|txt)$",Text[0]).group(1)
                    x += "[" + Tag.upper() + "] "
                except:
                    pass
            
            if (len(Text) > 1):
                x += URL + " " + " ".join(Text[1:])
            else:
                r = re.search("(?:.+)youtube.com/(?:.+)v=([-_\w]+)",Text[0]).group(1)
                t = self.YouTube.getInfo(r)
                x += URL + " " + t
            
            #Twitter Tweets dürfen nicht länger als 140 Zeichen sein
            if (len(x) <= 140):
                self.Twitter.sendTweet(x)
                PrivMsg(Target,"hinzugefügt! - http://twitter.com/fptlnk","15Funlink:07 ")
            else:
                PrivMsg(Target,"Beschreibung zu lang. Max 140 Zeichen. Dein Add war " \
                + str(len(x)) + " Zeichen lang.","15Funlink:07 ")
        else: #Keine Beschreibung
                PrivMsg(Target,"Die Beschreibung fehlt!","15Funlink:07 ")