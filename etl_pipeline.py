import requests
import sqlite3
import logging

#Day 10 - Logger information
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     filename="etl_pipeline.log"
# )

# logger = logging.getLogger(__name__)

#Day 10 - logger in file and terminal
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("etl_pipeline.log")
file_handler.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.ERROR)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

url = "https://jsonplaceholder.typicode.com/posts"
#url = "https://this-domain-does-not-exist-123456.com/posts"

### Day 9 with etl piplene and functions
def extract_posts():

    try:
        response = requests.get(url)
        if response.status_code == 200:
            logger.info("Request is success")
            return response.json()
     
        else:
            logger.error ("Request failed")
            return None
    except requests.exceptions.RequestException:
        logger.exception("Request failed")
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
  
        logger.info("Posts table is ready")

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

        logger.info("Records processed: %s", processed)
        logger.info("Inserted records: %s", inserted)
        logger.info("Updated records: %s", updated)
        logger.info("Skipped records: %s", skipped)

        connection.commit()

        cursor.execute("SELECT COUNT(*) FROM posts")
        logger.info("Rows in database: %s", cursor.fetchone()[0])  
        
        connection.close()

    except sqlite3.Error:
        connection.rollback()
        logger.exception("DB records not updated due to upsert failure")

def validate_posts(posts,clean_posts):

    valid = True
    if len(posts) == len(clean_posts):
        logger.info("Validation passed: all records transformed")
    else:
        logger.error("Validation failed: transformation count mismatch")
        valid = False

    missing_ids = [
        post for post in clean_posts
        if post["post_id"] is None
    ]

    if missing_ids:
            logger.error("Validation failed: missing post ids")
            valid = False
    else:
            logger.info("Validation passed: no missing post ids")
            
    post_ids = [post["post_id"] for post in clean_posts]

    if len(post_ids) == len(set(post_ids)):
        logger.info("Validation passed: no duplicate post IDs")
    else:
        logger.error("Validation failed: duplicate post IDs found")
        valid = False

    missing_titles = [
        post for post in clean_posts
        if not post["title"]
    ]

    if missing_titles:
        logger.error("Validation failed: missing titles")
        valid = False
    else:
        logger.info("Validation passed: no missing titles")

    return valid

posts = extract_posts()

if posts is None:
    logger.warning("Extraction failed. Pipeline stopped.")
else:
    clean_posts = transform_posts(posts)
    if validate_posts(posts,clean_posts):
        load_posts(clean_posts)
    else:
        logger.error("Validation failed. Load stopped.")
