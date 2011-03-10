'''
Created on Jan 12, 2011

@author: msteinhoff
'''


class Test():
    def __init__(self):
        self.test = "ads"
    
    def __str__(self):
        return self.test

abc = {}

abc['asd'] = (Test(), None)

print abc['asd'][0]