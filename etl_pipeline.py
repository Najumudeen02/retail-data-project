import requests
import sqlite3
import logging
import datetime
from dotenv import load_dotenv
import os

load_dotenv()

#Day 10 - Logger information
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     filename="etl_pipeline.log"
# )

# logger = logging.getLogger(__name__)

API_URL = os.getenv("API_URL")
DATABASE_PATH = os.getenv("DATABASE_PATH")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "10"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
LOG_FILE = "etl_pipeline.log"


#Day 10 - logger in file and terminal
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(LOG_FILE)
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


#url = "https://this-domain-does-not-exist-123456.com/posts"

### Day 9 with etl piplene and functions
def extract_posts():

    try:
        response = requests.get(API_URL)
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

def get_last_successful_run():

    conn = sqlite3.connect(DATABASE_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT last_successful_run
        FROM pipeline_metadata
        WHERE pipeline_name = ?
    """, ("posts_pipeline",))

    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]

    return None


def initialize_pipeline_metadata():

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_metadata (
                pipeline_name TEXT PRIMARY KEY,
                last_successful_run TEXT
            )
        """)

        connection.commit()
        logger.info("Pipeline metadata table is ready")

    except sqlite3.Error:
        connection.rollback()
        logger.exception("Failed to initialize pipeline metadata table")
        raise

    finally:
        connection.close()

def load_posts(clean_posts,connection):

    inserted = 0
    updated = 0
    skipped =0
    processed = 0

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

        cursor.execute("SELECT COUNT(*) FROM posts")
        logger.info("Rows in database: %s", cursor.fetchone()[0])  

        return True

    except sqlite3.Error:
        logger.exception("DB records not updated due to upsert failure")
        raise

def update_last_successful_run(connection):

    run_time = datetime.datetime.now().isoformat()
    cursor = connection .cursor()
    
    try:
        cursor.execute("""
            INSERT INTO pipeline_metadata (pipeline_name,last_successful_run)
            VALUES (?, ?)
            ON CONFLICT(pipeline_name)
            DO UPDATE SET last_successful_run = excluded.last_successful_run
            """, ("posts_pipeline",run_time))
    
        logger.info("Pipeline watermark updated: %s", run_time)

    except sqlite3.Error:
        logger.exception("Failed to update pipeline watermark")
        raise


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

initialize_pipeline_metadata()

last_run = get_last_successful_run()

if last_run is None:
    logger.info("First pipeline run detected")
else:
    logger.info(
        "Incremental pipeline run. Last successful run: %s",
        last_run
    )

posts = extract_posts()

if posts is None:

    logger.warning("Extraction failed. Pipeline stopped.")

else:

    clean_posts = transform_posts(posts)

    if validate_posts(posts, clean_posts):

        connection = sqlite3.connect(DATABASE_PATH)

        try:
            load_posts(clean_posts, connection)

            update_last_successful_run(connection)

            connection.commit()
            logger.info("Pipeline database transaction committed successfully")

        except sqlite3.Error:

            connection.rollback()
            logger.exception("Pipeline database transaction failed")

        finally:

            connection.close()

    else:

        logger.error("Validation failed. Load stopped.")
