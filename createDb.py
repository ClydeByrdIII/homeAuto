import sqlite3

# creates db if not already made
conn=sqlite3.connect('HAB.db')

conn.execute('''pragma foreign_keys=ON''')

conn.execute('''CREATE TABLE devices
             (DID text PRIMARY KEY, NAME text, CIP text)''')

conn.execute('''CREATE TABLE events
             (DID text, NAME text, MSG text, TIME text,FOREIGN KEY(DID) REFERENCES devices(DID) ON DELETE CASCADE)''')

# Save (commit) the changes
conn.commit()

conn.close()

print "Database created and opened succesfully"