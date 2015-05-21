import sqlite3

conn = sqlite3.connect("goldenrod.db", check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT \"sql\" FROM sqlite_master WHERE \"sql\" IS NOT NULL")
allRows = cursor.fetchall()

for row in allRows:
    if u"sqlite_sequence" not in row["sql"]:
        print "cursor.execute(\"\"\""+row["sql"]+"\"\"\")"