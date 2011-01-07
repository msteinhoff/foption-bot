#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: fptbot.py

import socket
import re
import sys
import cPickle

from config import Config #nicht löschen
from system import System #nicht löschen

def addModule(modname):
    try:
        exec("from " + modname.lower() + " import " + modname);
    except:
        print ">> ERROR: Module " + modname + " not found!"
        return 
    try:
        exec("res = " + modname + "()")
        return res        
    except:
        print ">> ERROR creating Module " + modname + "!"
        return


def getModule(Constructor,Modlist):
    try:
        Constructor = re.search("^(?:.+)\.(.+?)$",str(Constructor)).group(1)
    except:
        pass
    
    x = 0
    while (x < len(Modlist)):
        try:
            r = re.search('<(?:.+)\.(.+?) instance at (?:.+)>',str(Modlist[x])).group(1)
            if (Constructor == r):
                break
        except:
            pass
        
        x += 1
    
    return Modlist[x]

def SaveCfg(Cfg):
    Settings = [\
                Cfg.Admin,              #0
                Cfg.TopicChanger,       #1
                Cfg.Topic,              #2
                Cfg.TS3IP,              #3
                Cfg.TS3Port,            #4
                Cfg.TS3PW,              #5
                Cfg.WissenDate,         #6
                ]
    
    obj2file(Settings,"fptbot.conf")
    print ">> bot settings saved."
    
def LoadCfg(Cfg):
    try:
        Settings = file2obj("fptbot.conf")

        Cfg.Admin = Settings[0]
        Cfg.TopicChanger = Settings[1]
        Cfg.Topic = Settings[2]
        Cfg.TS3IP = Settings[3]
        Cfg.TS3Port = Settings[4]
        Cfg.TS3PW = Settings[5]
        Cfg.WissenDate = Settings[6]
        print ">> bot config succesfully loaded."
        return Cfg
    except:
        print ">> ERROR: no config file was found. Creating a new one!"
        return Cfg
        
        
def obj2file(obj,FileName):
    f = open(FileName,"w")
    cPickle.dump(obj,f)
    f.close()

#Config Laden    
def file2obj(FileName):
    f = open(FileName,"r")
    return cPickle.load(f)
    f.close()

def main():
    
    Mods_loaded = False
    Socket_established = False

    Conf = Config()
    Conf = LoadCfg(Conf)
    ServerSocket = None
    
            if (Socket_established):
                if (Mods_loaded == False):
                    try:
                        s = System(ServerSocket)
                        Conf.Modlist.append(s)
                    
                        for i in Conf.Modules:
                            Conf.Modlist.append(addModule(i))
                    
                        Mods_loaded = True
                        print ">> modules loaded"
                    except:
                        print ">> ERROR: failed to load modules!"
                else:
                    print ">> updating socket - o rly?"
                    x = getModule(System, Conf.Modlist)
                    x.updateStream(ServerSocket)


    Conf.Run = True
    SaveCfg(Conf)
    print ">> closing program"
    sys.exit()
