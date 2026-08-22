import requests
import sqlite3

url = "https://jsonplaceholder.typicode.com/posts"
#url = "https://jsonplaceholder.typicode.com/does-not-exist"
#url = "https://this-domain-does-not-exist-123456.com/posts"

### Day 9 with etl piplene and functions
def extract_posts():

    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Request is success")
            return response.json()
     
        else:
            print ("Request failed")
            return None
    except requests.exceptions.RequestException:
        print("Request failed with time out or connection error")
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
    processed = 0

    connection = sqlite3.connect("retail_data.db")
    cursor = connection.cursor()
    
    try:
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

        cursor.execute("SELECT COUNT(*) FROM posts")
        print("Rows in database:", cursor.fetchone()[0])  
        
        connection.close()

    except sqlite3.Error:
        connection.rollback()
        print("DB records not updated due to upsert failure")

def validate_posts(posts,clean_posts):

    valid = True
    if len(posts) == len(clean_posts):
        print("Validation passed: all records transformed")
    else:
        print("Validation failed: transformation count mismatch")
        valid = False

    missing_ids = [
        post for post in clean_posts
        if post["post_id"] is None
    ]

    if missing_ids:
            print("Validation failed: missing post ids")
            valid = False
    else:
            print("Validation passed: no missing post ids")
            
    post_ids = [post["post_id"] for post in clean_posts]

    if len(post_ids) == len(set(post_ids)):
        print("Validation passed: no duplicate post IDs")
    else:
        print("Validation failed: duplicate post IDs found")
        valid = False

    missing_titles = [
        post for post in clean_posts
        if not post["title"]
    ]

    if missing_titles:
        print("Validation failed: missing titles")
        valid = False
    else:
        print("Validation passed: no missing titles")

    return valid

posts = extract_posts()

if posts is None:
    print("Extraction failed. Pipeline stopped.")
else:
    clean_posts = transform_posts(posts)
    if validate_posts(posts,clean_posts):
        load_posts(clean_posts)
    else:
        print("Validation failed. Load stopped.")
