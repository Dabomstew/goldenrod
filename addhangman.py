import sqlite3
import time

conn = sqlite3.connect("contests.db", check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

while True:
    word = raw_input('Word (leave blank to finish for now): ').strip()
    if not word:
        break
    
    cursor.execute("SELECT * FROM hangman_words WHERE word = ? COLLATE NOCASE", (word,))
    possibleword = cursor.fetchone()
    if possibleword != None:
        print "Repeat word."
        continue
        
    cursor.execute("INSERT INTO hangman_words (word, whenAdded, used_in_cycle) VALUES(?, ?, ?)", (word.lower(), int(time.time()), 0))
    rowid = cursor.lastrowid
    conn.commit()
    print "Inserted word #%d" % rowid
    print ""
        
conn.close()
    