'''
Created on 05.08.2010

@author: rack
'''

import sqlite3

def main():
    conn = sqlite3.connect('db/kalender')
    c = conn.cursor()
    c.execute('''create table stocks (date text, trans text, symbol text, qty real, price real)''')
    c.execute("""insert into stocks values ('2006-01-05','BUY','RHAT',100,35.14)""")
    conn.commit()
    c.close()


    print "done"
        
if __name__ == '__main__':
    main()