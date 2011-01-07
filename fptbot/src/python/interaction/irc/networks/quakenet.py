'''
Created on Jan 6, 2011

@author: msteinhoff

Implementiert QuakeNet-spezifische funktionen

'''

class Quakenet(object):
    
    ' moved auth data to config.py '

    def __init__(self):
        ServerMsg("PRIVMSG Q@CServe.quakenet.org :AUTH " + self.Auth + " " + self.Password)
        pass
    