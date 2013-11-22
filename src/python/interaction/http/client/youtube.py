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

@since Jan 6, 2011
@author Rack
"""

__version__ = '$Rev$'

import re
import urllib

from system import PrivMsg

class YouTube():
    regexpattern = r':(.+) (?:PRIVMSG) ([\S]+) :(?:.+)youtube.com/(?:.+)v=([-_\w]+)'

    '''
    If a user posts a YouTube link, this module will post the video title in the channel
    '''

    #Texthandling
    def handleInput(self,Matchlist):
        #Source = Matchlist[0]
        Target = Matchlist[1]
        Text = Matchlist[2]
        
        PrivMsg(Target, "14Titel: 3[ " + self.getInfo(Text) + " 3]")


    #Details zum Link abrufen
    def getInfo(self,VideoID):
        url = urllib.urlopen("http://www.youtube.com/watch?v=" + VideoID)
        gdata = url.read()
        
        Titel = ''
        
        try:
            Titel = (re.search("<meta name=\"title\" content=\"(.+)\">", gdata)).group(1)
        except:
            pass
         
        return Titel