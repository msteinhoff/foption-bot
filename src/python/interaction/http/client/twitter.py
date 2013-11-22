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

import socket
import base64
import urllib

class Twitter():
    """
    This module posts tweets on twitter.
    """

    def __init__(self,User,Password):
        self.User = User
        self.Password = Password

    def sendTweet(self,Tweet):
        Tweet = Tweet.decode("iso-8859-1")
        Tweet = Tweet.encode("utf-8")
        Tweet = urllib.quote(Tweet)
        
        encoded = base64.b64encode(self.User + ":" + self.Password)
            
        postdata = "status=" + Tweet
        strhead  = "POST /statuses/update.xml HTTP/1.1\r\n"
        strhead += "Host: twitter.com\r\n"
        strhead += "Content-Length: " + str(len(postdata)) + "\r\n"
        strhead += "Authorization: Basic " + encoded + "\r\n\r\n"
        strhead += postdata + "\r\n\r\n"

        TwitterSocket = socket.socket()
        TwitterSocket.connect(("www.twitter.com", 80))

        TwitterSocket.send(strhead)
        
        TwitterSocket.close()
