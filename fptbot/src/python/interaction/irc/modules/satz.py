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

@since Apr 08, 2010
@author rack
"""

import re
import time
import random
import datetime

from copy import deepcopy
from threading import Timer
from config import Config
from system import file2obj,obj2file,PrivMsg

class Satz():
    regexpattern = r':(.+) PRIVMSG ([\S]+) :(?:.fail (.+)|.satz(?:([\S]+)\s?([\S]*)$| ([\S]+)|$))'
    __CharSet = {\
               'a': 1,'b': 3,'c': 2,'d': 2,'e': 1,'f': 3,'g': 2,'h': 2,'i': 1,
               'j': 4,'k': 3,'l': 2,'m': 2,'n': 1,'o': 3,'p': 4,'q': 4,'r': 1,
               's': 1,'t': 2,'u': 2,'v': 4,'w': 3,'x': 4,'y': 4,'z': 3
               }
    
    '''
    .satz -> Satzausgabe
    .satz <wort> -> Wort anhängen
    .satz.score -> akutelle Highscore
    .satz.highscore -> Gesamthighscore
    .satz.reset -> Satz löschen, ohne -Punkte berechnen
    .fail <nick> -> Satz löschen mit -Punkten berechnen
    '''


    def __init__(self):
        self.Config = Config()
        self.__FilenameCfg = "satz.conf"
        self.__SatzDB = "db/satz.db"
        self.__SaveSettingsInterval = 3000 #secs
        self.__Channel = self.Config.Channel
        self.__Run = True
        
        #Loading settings -- BEGIN --
        s = file2obj(self.__FilenameCfg)
        if (s != False):
            self.__Highscore = s[0]
            self.__Score = s[1]
            self.__Satz = s[2]
            self.__NickBan = s[3]
        else:
            self.__Run = False
        #Loading settings -- END --
        
        h = file2obj(self.__SatzDB)
        if (h != False):
            self.__SatzHistory = h
        else:
            self.__Run = False
        
        self.__Votes = {}
        self.__Wortreservierung = []
        self.__LastPostTime = time.time()
        self.__tmpVoter = ""
        
        self.Timer = Timer(self.__SaveSettingsInterval,self.isNextDay,[datetime.date.today()])
        self.Timer.start()
    
    def shutdown(self):
        if (self.__Run):
            self.saveConfig()
            self.Timer.cancel()
            print ">> Satz-config saved!"
        
        
    def saveConfig(self):
        varConfig = [self.__Highscore,self.__Score,self.__Satz,self.__NickBan]
        obj2file(varConfig, self.__FilenameCfg)
        obj2file(self.__SatzHistory, self.__SatzDB)        


    def handleInput(self,Matchlist):
        #print str(Matchlist) #('rack!~rack@rack.users.quakenet.org', '#rack', '', '', '.satz', '', '')
        Source = Matchlist[0]
        Target = Matchlist[1]
        
        if (self.__Run):
            if (Matchlist[3] == "") and (Matchlist[2] == ""): #.satz <wort>
                self.__addWort(Source,Target,Matchlist[5])
            
            elif (Matchlist[3] == ".score"):
                PrivMsg(Target, "Punktestande (Runde): " + self.__getScore(),"15SatzSpiel: 7")
            
            elif (Matchlist[3] == ".highscore"):
                PrivMsg(Target, "Punktestande (Gesamt): " + self.__getHighscore(),"15SatzSpiel: 7")
                
            elif (Matchlist[3] == ".verkackt") and (Matchlist[4] != ""):
                self.__votePlayer(Source, Target, Matchlist[4])
            
            elif (Matchlist[3] == ".old"):
                if (Matchlist[4] != ""): #ID mit angegeben!
                    try:
                        ID = int(Matchlist[4])
                        if (ID > 0) and (ID <= len(self.__SatzHistory)):
                            length = len(self.__SatzHistory)
                            Sentence = self.__getHistorySentence(ID-1)
                            PrivMsg(Target, "'" + " ".join(Sentence[0][0:]) + "' verkackt von '"  
                                    + Sentence[1] + "' [" + str(ID) + "/" + str(length) + "]","15SatzSpiel: 7")
                        else:
                            PrivMsg(Target, "Die ID muss zwischen 1 und " 
                                    + str(len(self.__SatzHistory)) + " liegen.","15SatzSpiel: 7")
                    except:
                        PrivMsg(Target, "ID muss eine Zahl sein!","15SatzSpiel: 7")
                else:
                    Sentence, ID = self.__getHistorySentence()
                    PrivMsg(Target, "'" + " ".join(Sentence[0][0:]) + "' verkackt von '" 
                            + Sentence[1] + "' [" + str(ID) + "/" + str(len(self.__SatzHistory)) + "]","15SatzSpiel: 7")
    
            elif (Matchlist[3] == ".reset"):
                if (len(self.__Satz) > 0):
                    self.__MergeScore()
                else:
                    PrivMsg(Target, "Es gibt keine Satzrunde zum reseten!","15SatzSpiel: 7")
                
            elif (Matchlist[2] != ""): #.fail nick  ->> nick = Matchlist[2]
                self.__votePlayer(Source, Target, Matchlist[2])
            
        else:
            PrivMsg(Target, "Fehler beim Laden der Cfg-Datei! Spielen NICHT möglich","15SatzSpiel: 7")


    def isNextDay(self,Date):
        today = datetime.date.today()
        if (today != Date):
            self.saveConfig()
        self.Timer = Timer(self.__SaveSettingsInterval,self.isNextDay,[datetime.date.today()])
        self.Timer.start()


    def __getHistorySentence(self,ID=None):
        if (ID != None):
            return self.__SatzHistory[ID]
        else:
            ID = random.randint(1,len(self.__SatzHistory))
            return self.__SatzHistory[ID-1],ID
        
    
    def __getSatz(self):
        return " ".join(self.__Satz[0:])
    
    
    def __getScore(self):
        return str(self.__Score)
    
    
    def __getHighscore(self):
        return str(self.__Highscore)
    
    
    def __votePlayer(self,Source,Target,Vote):
        if (self.Config.Nicklist.has_key(Vote)):
            Player = self.__getPlayer(Vote)
            Voter = re.match("(.+?)!", Source).group(1)
            self.__tmpVoter = self.__getPlayer(Voter)
           
        elif (self.__Score.has_key(Vote)):
            Player = Vote
            Voter = re.match("(.+?)!", Source).group(1)
            self.__tmpVoter = self.__getPlayer(Voter)
        else:
            PrivMsg(Target, "Es spiel kein Spieler mit dem Namen '" \
                           + Vote + "' mit.","15SatzSpiel: 7")
            return
    
        if (self.__Votes.has_key(Player)):
            x = self.__Votes[Player]
            x = x.split(",")
            if (self.__tmpVoter in x == False):
                self.__Votes[Player] += "," + self.__tmpVoter
                self.__tmpVoter = ""
            else:
                PrivMsg(self.__Channel, "Du hast bereits '" + Player \
                        + "' nominiert!","15SatzSpiel: 7")
                return
        else:
            if (self.__Score.has_key(Player)):
                self.__Votes[Player] = self.__tmpVoter
                self.__tmpVoter = ""
            else:
                PrivMsg(self.__Channel, "Es spielt kein Spieler mit dem Auth/Ident '" 
                        + Player + "' mit.","15SatzSpiel: 7")
                return
            
        PrivMsg(self.__Channel, "'" + Player + "' wurde bisher von '" \
                + str(self.__Votes[Player]) + "' nominiert! Benötigt werden " \
                + (str(len(self.__Score)-1) if len(self.__Score) < 6 else str(int(len(self.__Score)/2))) \
                + " Nominierungen.","15SatzSpiel: 7")
        
                
        #Punkteberechnung für 5 oder weniger Spieler: Regel "n-1"
        if (len(self.__Votes) < 6):
            Voters = self.__Votes[Player]
            if (Voters.count(",")+1 >= len(self.__Score)-1):
                pkt = int((self.__calcScore(self.__Satz[len(self.__Satz)-1]) + 100 - len(self.__Satz)) * 1.9)
                PrivMsg(self.__Channel, "4'" + Player + "' hat den Satz verkackt und bekommt dafür -" \
                        + str(pkt) + " Punkte","15SatzSpiel: 7")
                self.__MergeScore(pkt,Player)
                
        else:
            Voters = self.__Votes[Player]
            if (Voters.count(",")+1 >= int(len(self.__Score)/2)):
                pkt = int((self.__calcScore(self.__Satz[len(self.__Satz)-1]) + 100 - len(self.__Satz)) * 1.9)
                PrivMsg(self.__Channel, "4'" + Player + "' hat den Satz verkackt und bekommt dafür -" \
                        + str(pkt) + " Punkte","15SatzSpiel: 7")
                self.__MergeScore(pkt,Player)


    def __getPlayer(self,Nick):
        if (self.Config.Nicklist.has_key(Nick)):
            n = self.Config.Nicklist[Nick]
            if (n[1] != ''):
                return n[1]
            else:
                return n[2]
        return Nick
                     

    def __addWort(self,Source,Target,Wort=""):
        
        if (time.time() - self.__LastPostTime > 2):

            Nick = re.match("(.+?)!", Source).group(1)
            
            if (Wort == ""): #satz ausgeben
                tmp = self.__getSatz()
                    
                if (tmp == ""): #Gibt noch keinen Satz
                    tmp = "Fang einen neuen Satz an!"
                    
                PrivMsg(Target, tmp,"15SatzSpiel: 7")
                return        
            
            #Wortreservierungsteil
            #Falls jmd anderes zuvor schreibt, wird geblockt
            if (Wort != "") and (len(self.__Wortreservierung) > 0):
                if (time.time() - self.__Wortreservierung[1] < 30):
                    if (self.__getPlayer(Nick) != self.__Wortreservierung[0]):
                        PrivMsg(Target, "Du bist nicht " + self.__Wortreservierung[0],"15SatzSpiel: 7")
                        return
                else:
                    # "30 sek abgelaufen"
                    self.__Wortreservierung = []
            
            
            #Wenn jmd ein Komma schreibt, darf er das nächste Wort noch anfügen. Zeit -> 30 Sekunden
            if (Wort == ",") and (self.__getPlayer(Nick) != self.__NickBan) and (len(self.__Wortreservierung) == 0):
                self.__Wortreservierung.append(self.__getPlayer(Nick))
                self.__Wortreservierung.append(time.time())
                PrivMsg(Target, Nick + " hat eine Wortreservierung für 30 Sekunden.","15SatzSpiel: 7")
                self.__Satz[len(self.__Satz)-1] += Wort
                return
            
            
            #Sonderzeichen ersetzen
            subWort = Wort.replace('ä','ae')\
                        .replace('ö','oe')\
                        .replace('ü','ue')\
                        .replace('ß','ss')\
                        .replace('#','4')\
                        .replace('-','4')\
                        .replace("'",'4')\
                        .replace('@','4')\
                        .replace('#','4')\
                        .replace('.','4')\
                        .replace('"','4')
            
            #Wort hat keine Sonderzeichen mehr und der Spieler ist nicht geblockt!
            if (subWort.isalnum()) and (self.__NickBan != self.__getPlayer(Nick)):
                #Das Wort gibt es schon
                if (self.__Satz.count(Wort)):
                    x = self.__calcScore(subWort) + 100 - len(self.__Satz) #Minuspunkte
                    
                    Player = self.__getPlayer(Nick)
                    if (self.__Score.has_key(Player)): #Spieler hat bereits Punkte
                        for nick in self.__Score.iterkeys():
                            if (Player == nick):
                                self.__Score[nick] -= x #Punkte werden abgezogen
                                break
                    else: #Spieler wird für diese Runde neu angelegt
                        self.__Score[Player] = x * -1
                    
                    PrivMsg(Target, "4 Das Wort " + Wort + " ist bereits im Satz. " \
                            + Nick + " bekommt deswegen " + str(x) + " Punkte abgezogen!","15SatzSpiel: 7")
                
                    
                    return
                #Wort ist noch nicht im Satz
                else:
                    x = self.__calcScore(subWort) + len(self.__Satz) #Punkte für das Wort
                    Player = self.__getPlayer(Nick)
                    
                    if (self.__Score.has_key(Player)):
                        self.__Score[Player] += x    #Punkte werden auf's Konto gutgeschrieben
                    else:
                        self.__Score[Player] = x
            
                self.__Satz.append(Wort)
            
                #Damit man nicht 2 Wörter hintereinander schreiben kann
                self.__NickBan = self.__getPlayer(Nick)
                
                #Falls es eine Wortreservierung gab, wird diese aufgehoben
                if (len(self.__Wortreservierung) > 0):
                    self.__Wortreservierung = []
        
                #Ausgabe der letzten Wörter des Satzes
                if (len(self.__Satz) > 10):
                    PrivMsg(Target, " ".join(self.__Satz[len(self.__Satz)-10:]),"15SatzSpiel: 7")
                else:
                    PrivMsg(Target, "..." + " ".join(self.__Satz),"15SatzSpiel: 7")
                    
                #"Doppelpost"-Spamprotection
                self.__LastPostTime = time.time()
                
            else:
                PrivMsg(Target, "4 Du hast bereits dass letzte Wort angehängt!","15SatzSpiel: 7")
                
    
    def __calcScore(self,Wort):
        '''
        Berechnet die Punkte für das übgergebende Wort anhand des "CharSet"
        '''
        Points = 0
        Wort = Wort.lower()
        
        for char in Wort:
            try:
                x = int(char)
                Points += x
            except:
                for key,value in self.__CharSet.iteritems():#super(Satz,self).__CharSet.iteritems():
                    if (char == key):
                        Points += value
                        break

        return Points
        
    
    
    def __MergeScore(self,Punkte=0,Loser=None):
        #Punkteabzug für die Verlierer
        if (self.__Score.has_key(Loser)):
            self.__Score[Loser] -= Punkte
            Name = Loser
            Score = self.__Score[Loser]
        else:
            Name = ""
            Score = 0
            
        #Ausgabe des Gewinnters
        for Key,Value in self.__Score.iteritems():
            if (Value > Score):
                Name = Key
                Score = Value
                
        PrivMsg(self.__Channel, "Der Gewinner dieser Runde ist '" \
                + Name + "' mit " + str(Score) + " Punkten. Es kann eine neue Runde " \
                + "mit .satz <wort> angefangen werden.","15SatzSpiel: 7")
            
        
        #Übertragen der Punkte
        #Punkte auf vorhandene Konten überspielen
        
        var_score = deepcopy(self.__Score)
        var_highscore = deepcopy(self.__Highscore)
        
        for Key,Value in var_score.iteritems():
            for Ident in var_highscore.iterkeys():
                if (Key == Ident):
                    self.__Highscore[Ident] += Value
                    del self.__Score[Key]
                    break
        
        #Konten für neue Spieler anlegen
        for Key,Value in self.__Score.iteritems():
            self.__Highscore[Key] = Value
        
        
        self.__resetSatz(Loser)
        
       
    def __resetSatz(self,Loser=None):
        if (len(self.__Satz) > 0):
            self.__SatzHistory.append([self.__Satz,Loser])
        
        self.__Satz = []
        self.__Score= {}
        self.__NickBan = ""
        self.__Votes = {}
        self.__tmpVoter = ""