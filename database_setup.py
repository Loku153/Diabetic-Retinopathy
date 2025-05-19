import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

print("Doctors:")
cursor.execute("SELECT * FROM doctors")
for row in cursor.fetchall():
    print(row)

print("\nPatients:")
cursor.execute("SELECT * FROM patients")
for row in cursor.fetchall():
    print(row)

print("\:forms")
for row in cursor.fetchall():
    print(row)

conn.close()

