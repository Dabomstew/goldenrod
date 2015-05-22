import sqlite3
import datetime

conn = sqlite3.connect("contests.db", check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
lastGroup = -1

while True:
    question = raw_input('Question (leave blank to finish for now): ').strip()
    if not question:
        break
    
    difficulty = 1
    diffinput = raw_input('Difficulty easy/medium/hard: ').strip().lower()
    if diffinput == 'easy':
        difficulty = 0
    elif diffinput == 'hard':
        difficulty = 2
    answers = []
    sameAsLast = False
    sameinput = raw_input('Group with last question y/n (blank = no): ').strip().lower()
    if (sameinput == 'y' or sameinput == 'yes') and lastGroup > 0:
        sameAsLast = True
    
    if sameAsLast:
        questionGroup = lastGroup
    else:
        cursor.execute("SELECT MAX(question_grouping) AS \"maxGroup\" FROM trivia_questions")
        qgRow = cursor.fetchone()
        questionGroup = qgRow["maxGroup"]+1
        lastGroup = questionGroup
        
    while True:
        newAnswer = raw_input('Enter a possible answer (leave blank to finish): ').strip().lower()
        if not newAnswer:
            break
        answers.append(newAnswer)
    
    if len(answers) == 0:
        print "Not allowed to have no answers, try again."
        continue
    
    cursor.execute("INSERT INTO trivia_questions (question, difficulty, whenAdded, question_grouping) VALUES(?, ?, ?, ?)", (question, difficulty, datetime.datetime.now(), questionGroup))
    rowid = cursor.lastrowid
    for answer in answers:
        cursor.execute("INSERT INTO trivia_answers (question_id, answer) VALUES(?, ?)", (rowid, answer))
    
    conn.commit()
    print "Inserted question #%d" % rowid
    print ""
        
conn.close()
    