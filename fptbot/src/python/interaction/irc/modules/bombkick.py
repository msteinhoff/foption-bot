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

@since May 01, 2010
@author rack
"""

class Bombkick():
    regexpattern = r':(.+) PRIVMSG ([\S]+) :(?:(\.schwarz|\.rot|\.gelb|\.blau|\.weiss|\.lila)|\.bombkick(?:$| ([\S]+)$)|(.bombstats))'
    
    def __init__(self):
        self.FilenameDB = "db/bombkick.db"
        self.Config = Config()
        self.Channel = self.Config.Channel
        
        x = file2obj(self.FilenameDB)
        self.BombDB = (x if x != False else {})
        
        self.Colors = ["schwarz","rot","gelb","blau","weiss","lila"]
    

    def handleInput(self,Matchlist):
        Source = Matchlist[0]
       
        if (Matchlist[2] == '') and (Matchlist[3] == '') and (Matchlist[4] == ''):
            self.setBomb(self.getUsername(Source),re.match("(.+?)!", Source).group(1))
        elif (Matchlist[3] != '') and (Matchlist[4] == ''):
            if (self.isInChannel(Matchlist[3])) and (Matchlist[3] != self.Config.cnick):
                self.setBomb(self.getUsername(Matchlist[3] + '!'),Matchlist[3])
        elif (Matchlist[2] != '') and (Matchlist[4] == ''):
            self.defuseBomb(self.getUsername(Source),Matchlist[2][1:])
        elif (Matchlist[4] == ".bombstats"):
            self.BombStats()

       
    def shutdown(self):
        obj2file(self.BombDB, self.FilenameDB)
        print ">> Bombstats saved!"
       
    
    def isInChannel(self,Nick):
        if (self.Config.Nicklist.has_key(Nick)):
            return True
        return False
            
       
    def getUsername(self,Source):
        n = re.match("(.+?)!", Source).group(1)
        if (self.Config.Nicklist[n][1] != ""):
            return self.Config.Nicklist[n][1]
        return self.Config.Nicklist[n][2]


    def getColors(self):
        x = random.randint(3,5)
        Colorlist = deepcopy(self.Colors)
        Colors = []
        
        y = 1
        while (y <= x):
            ColorID = random.randint(0,len(Colorlist)-1)
            Colors.append(Colorlist[ColorID])
            del Colorlist[ColorID]
            y += 1
        
        ID = random.randint(0,2)
        #print Colors[ID] + ' ' + str(Colors)
        
        return Colors[ID],Colors


    def setBomb(self,Auth,Nick):
        if ('@' in self.Config.Nicklist[self.Config.cnick][0]):
            if (self.BombDB.has_key(Auth) == False):
                #[Bombs defused,Failed defused,[Bombs in a row,'+' or '-'],[aktive timer,colors,color],nick]
                self.BombDB[Auth] = [0,0,[0,'+'],[None,[],""],'']
            
            if (self.BombDB[Auth][3][0] == None):
                Bombtimer = Timer(20,self.fireBomb,[Auth])
                Color, Colors = self.getColors()
                
                self.BombDB[Auth][3][0] = Bombtimer
                self.BombDB[Auth][3][1] = Colors
                self.BombDB[Auth][3][2] = Color
                self.BombDB[Auth][4] = Nick
            
                self.BombDB[Auth][3][0].start()
                
                PrivMsg(self.Channel,"ACTION gibt " + Auth + " eine Bombe in die Hand!" \
                        + " Versuch das richtige Kabel durchzuschneiden mit " + self.getColorString(Colors)\
                        + "!!! Schnell, du hast nur 20 Sekunden!")


    def fireBomb(self,Auth):
        self.BombDB[Auth][1] += 1
        if (self.BombDB[Auth][2][1] == '-'):
            self.BombDB[Auth][2][0] += 1
        else:
            self.BombDB[Auth][2][0] = 1
            self.BombDB[Auth][2][1] = '-'
        
        try:
            self.BombDB[Auth][3][0].cancel()
        except:
            pass
            
        self.BombDB[Auth][3][0] = None
        
        BOOMs = self.BombDB[Auth][1]
         
        ServerMsg("KICK " + self.Channel + " " + self.BombDB[Auth][4] \
                + " :Du bist zum " + str(BOOMs) + ". mal in die Luft geflogen.")
    
        
    def defuseBomb(self,Auth,Color):
        
        if (self.BombDB[Auth][3][2] != Color):
            self.fireBomb(Auth)
        else:
            self.BombDB[Auth][0] += 1
            if (self.BombDB[Auth][2][1] == '+'):
                self.BombDB[Auth][2][0] += 1
            else:
                self.BombDB[Auth][2][0] = 1
                self.BombDB[Auth][2][1] = '+'
            
            try:
                self.BombDB[Auth][3][0].cancel()
            except:
                pass
            
            self.BombDB[Auth][3][0] = None
            
            PrivMsg(self.Channel, Auth + " hats geschafft! Er hat zum " \
                    + str(self.BombDB[Auth][0]) + ". mal die Bombe entschärft!")
        
    
    
    def getColorString(self,Colors):
        String = ""
        x = 0
        while (x < len(Colors)):
            String += '.' + Colors[x] + (', ' if (x < len(Colors)-1) else '')
            x += 1

        return String
    
    def BombStats(self):
        DefuseKitUser = "" #+ in a row
        DefuseKitNum = 0
        
        LearningByDoing = "" #most bombs
        LearningNum = 0
        
        ChooseADiffJob = "" #most boooms
        JobNum = 0
        
        PassingLane = "" #- in a row
        LaneNum = 0
        
        Pro = "" #most defuse
        ProNum = 0
        
        for key,value in self.BombDB.iteritems():
            if (value[2][1] == '+'):
                if (value[2][0] > DefuseKitNum):
                    DefuseKitUser = key
                    DefuseKitNum = value[2][0]
            else:
                if (value[2][0] > LaneNum):
                    PassingLane = key
                    LaneNum = value[2][0]
            
            if (value[0]+value[1] > LearningNum):
                LearningByDoing = key
                LearningNum = value[0]+value[1]
                
            
            if (value[1] > JobNum):
                ChooseADiffJob = key
                JobNum = value[1]
            
            if (value[0] > ProNum):
                Pro = key
                ProNum = value[0]

        Timer(0,PrivMsg,[self.Channel,"'" + LearningByDoing + "' macht es nach dem 'learning by doing' Prinzip und hat sich schon " + str(LearningNum) + " mal zum Bombenentschärfen gemeldet."]).start()
        Timer(1,PrivMsg,[self.Channel,"'" + DefuseKitUser + "' benutzt anscheinend ein DefuseKit. Er hat " + str(DefuseKitNum) + " Bombe(n) hintereinander entschärft!"]).start()
        Timer(2,PrivMsg,[self.Channel,"'" + ChooseADiffJob + "' sollte sich besser einen anderen Job suchen. Bei ihm ist die Bombe " + str(JobNum) + " mal explodiert."]).start()
        Timer(3,PrivMsg,[self.Channel,"'" + PassingLane + "' ist auf einem guten Weg '" + ChooseADiffJob + "' zu überholen. Die letzten " + str(LaneNum) + " Bomben sind ihm explodiert."]).start()
        Timer(4,PrivMsg,[self.Channel,"Am besten nehmen alle Nachhilfe bei '" + Pro + "', denn er hat schon " + str(ProNum) + " Bomben entschärft!"]).start()

