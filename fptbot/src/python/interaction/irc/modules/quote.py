# -*- coding: UTF-8 -*-

import random
import cgi

from htmlentitydefs import name2codepoint
from system import txtfile2list,list2txtfile,PrivMsg

class Quote():
    regexpattern = r':(.+) (?:PRIVMSG) ([\S]+) :(.quote|.addquote|.searchquote)(?: (.+)|$)'
    
    def __init__(self):
        self.FilenameDB = "db/quote.db"
        self.HTMLFile = "../public_html/quote.html"
        
        DB = txtfile2list(self.FilenameDB)
        self.QuoteDB = (DB if DB != False else [])


    def handleInput(self,Matchlist):
        #Source = Matchlist[0]
        Target = Matchlist[1]
        Keyword = Matchlist[2]
        Text = Matchlist[3].split()
        
        if (Keyword == ".quote"):
            if (len(Text) == 0):
                self.PostMultiLine(Target, self.getQuote(""))
            elif (len(Text) == 1):
                try:
                    #Falls 1tes Wort in int umwandelbar ist, wird nach ID gesucht
                    self.PostMultiLine(Target, self.getQuote(int(Text[0])))
                except:
                    #Falls nicht, nach einem String (nick) suchen
                    self.PostMultiLine(Target, self.rndQuote(Text[0]))
        
        elif (Keyword == ".addquote") and (len(Text) > 0):
            PrivMsg(Target, self.addQuote(" ".join(Text[0:])))
            
        elif (Keyword == ".searchquote") and (len(Text) > 0):
            String = " ".join(Text[0:])
            PrivMsg(Target, "15[QUOTE]: 7Der gesuchte String '" \
            + String + "' befindet sich in folgenden Zitaten: "  
            + str(self.searchQuote(String)))
                
    
    def addQuote(self,String):
        self.QuoteDB.append(String + "\n")
        list2txtfile(self.QuoteDB, self.FilenameDB)

        self.createHTML()

        return "Das Zitat wurde in die Datenbank aufgenommen. Es hat die ID 15 " \
        + str(len(self.QuoteDB))


    def getQuote(self,String):
        """
        String = "" -> Zufälliges Zitat
        String = int -> Zitat mit der ID
        """
        
        MaxNum = len(self.QuoteDB)
        if (String == ''):
            Line = random.randint(0,MaxNum)
        else:
            Line = int(String) -1
            if (Line > MaxNum) or (Line < 0):
                return "Die ID gibt es nicht! Versuche eine Zahl zwischen 1 und " \
                + str(MaxNum+1)
        
        return self.QuoteDB[Line].strip() + " - 15Quote(" + str(Line+1) + "/" \
        + str(MaxNum) + ")" 


    def searchQuote(self,String):
        IDs = ""
        Line = 0
        while (Line < len(self.QuoteDB)):
            if (String in self.QuoteDB[Line]):
                IDs += ("" if IDs == "" else ", ") + str(Line +1)
            Line += 1

        return (None if IDs == "" else IDs)


    def rndQuote(self,String):
        IDs = self.searchQuote(String)
        if (IDs == None):
            return "15[QUOTE]: 7Kein Zitat gefunden mit '" + String + "'."
        else:
            ID = IDs.split(",")
            QuoteNr = random.randint(1,len(ID)) - 1 #weil Array bei 0 anfängt
            return self.getQuote(ID[QuoteNr].strip())
        
        
    def createHTML(self):
        name2codepoint['#39'] = 39

        HTMLKopf = "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 3.2//EN\">\n"
        HTMLKopf += "<HTML><HEAD><META HTTP-EQUIV=\"CONTENT-TYPE\" CONTENT=\"text/html; charset=windows-1252\"><TITLE></TITLE>\n"
        HTMLKopf += "<link rel=\"stylesheet\" href=\"fptdb.css\" type=\"text/css\"></HEAD><BODY TEXT=\"#000000\"><center>\n"
        HTMLKopf += "<table cellpadding=\"2\" cellspacing=\"0\" width=\"80%\"><TBODY><TR><TD HEIGHT=18 ALIGN=LEFT BGCOLOR=\"#990100\"><B><FONT class=\"title\"></FONT></B></TD>\n"
        HTMLKopf += "</TR><TR><TD HEIGHT=18 ALIGN=LEFT BGCOLOR=\"#e5e3e0\"><B><FONT class=\"subtitle\"> Quote database</FONT></B></TD></TR>\n"

        Slot = len(self.QuoteDB)-1
        while (Slot >= 0):
            HTMLKopf += "<TR><TD HEIGHT=18></TD></TR><tr><td valign=\"top\">"
            HTMLKopf += "<p class=\"quote\"><b>#" + str(Slot) + "</b></a></p>"
            HTMLKopf += "<p class=\"qt\">" + cgi.escape(self.QuoteDB[Slot].strip()) + "</p>"

            Slot -= 1

        HTMLKopf += "</TBODY></TABLE></center></BODY></HTML>"

        File = open(self.HTMLFile, 'w')
        File.write(HTMLKopf)
        File.close()
            

    def PostMultiLine(self,Target,Msg):
        Line = "7 "
        Array = Msg.split()
        for i in Array:
            if ((len(Line) + len(i) + 3) <= 425):
                Line += i + " "
            else:
                PrivMsg(Target,"7 " + Line)
                Line = i

        PrivMsg(Target,"7 " + Line.rstrip())
