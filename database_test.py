import sqlite3
import csv


#Incremental loading - Day 8
def incremental_load(new_posts, cursor):

    inserted = 0
    updated = 0
    skipped = 0

    cursor.execute (""" select post_id from posts order by post_id""")
    existing_ids = cursor.fetchall()
    existing_ids = [row[0] for row in existing_ids]
    
    print("Existing IDs:", existing_ids[:10])

    #Loop to convert the varchar to int and insert into DB - Day 8
    for post in new_posts:
        
        post["user_id"] = int(post["user_id"])
        post["post_id"] = int(post["post_id"])

        if post["post_id"] in existing_ids:
            print("Record already exists in DB")
        else:
            cursor.execute("""
                insert into posts (user_id, post_id, title)
                values( ?,?,?)""",
               (post["user_id"],post["post_id"], post["title"]))
            inserted+=1


        cursor.execute("""
                   SELECT title
                    FROM posts
                     WHERE post_id = ?
                        """, (post["post_id"],))
                    
        row = cursor.fetchone()
        existing_title = row[0]
        
        if existing_title == post["title"]:
            print("No change")
            skipped+=1
        else:
            print("Title has changed")
            print("Updating record ...")
            cursor.execute("""update posts set title = ? where post_id = ? """,(post["title"],post["post_id"]))
            updated +=1
            print("Updated title")    

            cursor.execute("""select title from posts where post_id = ?""" , (post["post_id"],))
        
            row = cursor.fetchone()
            print(row)  

    # print("Inserted:", inserted)
    # print("Updated:", updated)
    # print("Skipped:", skipped)
    return inserted, updated, skipped

def database_connection():

    connection = sqlite3.connect("retail_data.db")
    cursor = connection.cursor()

    new_posts = [
    {"user_id": 11, "post_id": 101, "title": "New post 101"},
    {"user_id": 11, "post_id": 102, "title": "Title changed for 102 & user 11"},
    {"user_id": 12, "post_id": 103, "title": "New post 103"},
    ]
    #Table drop Day 8
    #cursor.execute("DROP table posts")
    #connection.commit()
    
    #Table creation Day 7
    # cursor.execute("""
    #     CREATE TABLE IF NOT EXISTS posts(
    #         user_id INTEGER,
    #         post_id INTEGER PRIMARY KEY,
    #         title TEXT
    #     )
    # """)

    #Get table column structure - Day 8
    # cursor.execute("PRAGMA table_info(posts)")
    # columns = cursor.fetchall()

    # for column in columns:
    #     print(column)

    #Delete rows from table posts - Day 7
    #cursor.execute("DELETE FROM posts")

    #Read csv and insert into table
    with open("clean_posts.csv", "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
    
        csv_posts = list(reader)
        inserted, updated, skipped = incremental_load(new_posts, cursor)
        print("Inserted:", inserted)
        print("Updated:", updated)
        print("Skipped:", skipped)
        connection.commit()


        # 👇 UPSERT TEST HERE - day 8

        test_post = {
            "user_id": 13,
            "post_id": 104,
            "title": "Brand new post 104"
            }

        cursor.execute("""
            INSERT INTO posts (user_id, post_id, title)
            VALUES (?, ?, ?)
            ON CONFLICT(post_id)
            DO UPDATE SET
            user_id = excluded.user_id,
            title = excluded.title
            where posts.title <> excluded.title
            """, (
            test_post["user_id"],
            test_post["post_id"],
            test_post["title"]
            ))

        connection.commit()

        # verify the upsert - day 8
        cursor.execute("""
            SELECT user_id, post_id, title
            FROM posts
            WHERE post_id = ?
        """, (102,))

        print(cursor.fetchone())
 

        #Duplicate insert records with try and catch - Day 8

        # try:
        #     #Duplicate insert records check - Day 8
        #     cursor.execute("""
        #           insert into posts (user_id, post_id, title)
        #           values (?,?,?) """,
        #           (1,1,"Duplicate test"))

        #     connection.commit()

        # except sqlite3.IntegrityError:
        #     print("Duplicate post_id detected")
            
        #print("Insert completed")
        
    #Update 1 record and fetch 1 record- Day 8
    # cursor.execute(""" update posts 
    # set title=? where post_id = ?""", ("Updated title for testing",1))

    # connection.commit()

    # cursor.execute(""" select user_id,post_id,title from posts where post_id = ?""", (1,))

    # row = cursor.fetchone()

    #print(row)
    #Fetch records from the table - Day
    cursor.execute("""SELECT user_id,MAX(post_id) FROM posts
                    group by user_id
                    order by user_id""")

    rows = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM posts")
    print("Rows currently in database:", cursor.fetchone()[0])

    #result = cursor.fetchone()

    #Delete 1 row exercise and try to fetch that record- Day 8 
    # cursor.execute ("""Delete from posts where post_id= ? """,(1,))
    # connection.commit()

    # cursor.execute(""" select user_id,post_id,title from posts where post_id = ?""", (1,))
    
    # row = cursor.fetchone()

    # if row is None: - Learning from chatgpt
    #     print("Post 1 was successfully deleted")
    # else:
    #     print("Post 1 still exists")


    # for row in rows:
    #     print(row)

    #print("Rows in database:", result[0])
    #print("Posts table created")

    connection.close()
        
database_connection()
