import sqlite3
import csv

def database_connection():

    connection = sqlite3.connect("retail_data.db")
    cursor = connection.cursor()

    #Table creation Day 7
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts(
            user_id INTEGER,
            post_id INTEGER PRIMARY KEY,
            title TEXT
        )
    """)

    cursor.execute("DELETE FROM posts")

    #Read csv and insert into table
    with open("clean_posts.csv", "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
    
        csv_posts = list(reader)
    
        for post in csv_posts:
            post["user_id"] = int(post["user_id"])
            post["post_id"] = int(post["post_id"])
            cursor.execute("""
                insert into posts (user_id, post_id, title)
                values( ?,?,?)
            """,(post["user_id"],post["post_id"], post["title"]))

        #print("Insert completed")
        
    connection.commit()

    #Fetch records from the table
    cursor.execute("""SELECT user_id,MAX(post_id) FROM posts
                    group by user_id
                    order by user_id""")

    rows = cursor.fetchall()

    #result = cursor.fetchone()

    for row in rows:
        print(row)

    #print("Rows in database:", result[0])
    #print("Posts table created")

    connection.close()
        
database_connection()