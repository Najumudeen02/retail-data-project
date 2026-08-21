import requests
import sqlite3

url = "https://jsonplaceholder.typicode.com/posts"

def extract_posts():

    response = requests.get(url)
    if response.status_code == 200:
        print("Request is success")
        return response.json()
     
    else:
        print ("Request failed")
        return None

def transform_posts(posts):
    clean_posts = []
    for post in posts:
        clean_post = {
                "user_id": post["userId"],
                "post_id": post["id"],
                "title": post["title"]
                }
        clean_posts.append(clean_post)
    return clean_posts

def load_posts(clean_posts):

    inserted = 0
    updated = 0
    skipped =0
    existing = 0
    processed = 0

    connection = sqlite3.connect("retail_data.db")
    cursor = connection.cursor()
    #cursor.execute("DROP table posts")
    cursor.execute(""" CREATE TABLE IF NOT EXISTS posts(
        user_id INTEGER,
        post_id INTEGER PRIMARY KEY,
        title TEXT)
        """)
  
    print("Posts table is ready")
    
    for post in clean_posts:

        cursor.execute("""
                    SELECT title
                    FROM posts
                    WHERE post_id = ?
                    """, (post["post_id"],))
        
        existing = cursor.fetchone()

        if existing is None:
            inserted += 1
        elif existing[0] == post["title"]:
            skipped += 1
        else:
            updated += 1

        cursor.execute("""
            INSERT INTO posts (user_id, post_id, title)
            VALUES (?, ?, ?)
            ON CONFLICT(post_id)
            DO UPDATE SET
            user_id = excluded.user_id,
            title = excluded.title
            WHERE posts.title <> excluded.title
        """, (
            post["user_id"],
            post["post_id"],
            post["title"]
        ))

        processed += 1

    print("Records processed:", processed)
    print("Inserted:", inserted)
    print("Updated:", updated)
    print("Skipped:", skipped)

    connection.commit()

    cursor.execute("SELECT COUNT(*) FROM posts where post_id < 101")
    print("Rows in database:", cursor.fetchone()[0])  
    
    cursor.execute("""
            DELETE FROM posts
            WHERE post_id > 100
            """)
    
    connection.commit()
    
    cursor.execute("""
            SELECT user_id, post_id, title
            FROM posts
            WHERE post_id > 100 OR post_id IS NULL
            ORDER BY post_id
            """)
    
    rows = cursor.fetchall()
    
    for row in rows:
        print(row)

    connection.close()

def additional_posts(new_posts):

    connection = sqlite3.connect("retail_data.db")
    cursor = connection.cursor()

    cursor.execute("""
                        INSERT INTO posts (user_id, post_id, title)
                        VALUES (?, ?, ?)
                        ON CONFLICT(post_id)
                        DO UPDATE SET
                        user_id = excluded.user_id,
                        title = excluded.title
                        WHERE posts.title <> excluded.title
                    """, (
                        post["user_id"],
                        post["post_id"],
                        post["title"]
                    ))

    
    connection.commit()

    cursor.execute("""
        DELETE FROM posts
        WHERE post_id > 100
        """)

    connection.commit()

    cursor.execute("""
        SELECT user_id, post_id, title
        FROM posts
        WHERE post_id > 100 OR post_id IS NULL
        ORDER BY post_id
        """)

    rows = cursor.fetchall()

    for row in rows:
        print(row)

    connection.close()

new_posts = [
         {"user_id": 11, "post_id": 101, "title": "New post 101"},
         {"user_id": 11, "post_id": 102, "title": "New post 102"},
         {"user_id": 12, "post_id": 103, "title": "New post 103"},
         {"user_id": 13, "post_id": 104, "title": "Brand new post 104"},
    ]

def validate_posts(posts,clean_posts):

    valid = True
    if len(posts) == len(clean_posts):
        print("Validation passed: all records transformed")
    else:
        print("Validation failed")

    missing_ids = [
        post for post in clean_posts
        if post["post_id"] is None
    ]

    if missing_ids:
        valid = False

    print("Missing post IDs:", len(missing_ids))
            
    post_ids = [post["post_id"] for post in clean_posts]

    if len(post_ids) == len(set(post_ids)):
        print("Validation passed: no duplicate post IDs")
    else:
        print("Validation failed: duplicate post IDs found")

    missing_titles = [
        post for post in clean_posts
        if not post["title"]
    ]

    print("Missing titles:", len(missing_titles))

    if missing_titles:
        valid= False
    
    return valid

posts = extract_posts()
clean_posts = transform_posts(posts)
#clean_posts[1]["title"] = "Updated title for testing"
#clean_posts[0]["post_id"] = None

if validate_posts(posts,clean_posts):
    load_posts(clean_posts)
else:
    print("Validation failed. Load stopped.")

#additional_posts(new_posts)

#print(type(clean_posts))
#print(len(clean_posts))
#print(clean_posts[0])