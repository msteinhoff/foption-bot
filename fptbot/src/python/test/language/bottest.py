'''
Created on Jan 12, 2011

@author: msteinhoff
'''



test = {'abc': 'foobar', 'hitler': 'reich'}

print "plain"
for a in test:
    print a
    
print ""
print "items"
for a in test.items():
    print a
    
print ""
print "values"
for a in test.values():
    print a
    
