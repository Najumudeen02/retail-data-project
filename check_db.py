import sqlite3

connection = sqlite3.connect("retail_data.db")
cursor = connection.cursor()

cursor.execute("""
    SELECT user_id, post_id, title
    FROM posts
    WHERE post_id IN (1, 2, 3)
""")

rows = cursor.fetchall()

for row in rows:
    print(row)

connection.close()