import sqlite3

from config import DATABASE_PATH
from logger import logger

def initialize_database():

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts(
                user_id INTEGER,
                post_id INTEGER PRIMARY KEY,
                title TEXT,
                updated_at TEXT
            )
        """)

        connection.commit()
        logger.info("Posts table is ready")

    except sqlite3.Error:
        connection.rollback()
        logger.exception("Failed to initialize posts table")
        raise

    finally:
       connection.close()

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

    except sqlite3.Error:
        connection.rollback()
        logger.exception("Failed to initialize pipeline metadata table")
        raise

    finally:
       connection.close()

def get_last_successful_run():

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT last_successful_run
            FROM pipeline_metadata
            WHERE pipeline_name = ?
        """, ("posts_pipeline",))

        result = cursor.fetchone()

        if result:
            return result[0]

        return None

    finally:
        connection.close()

def load_posts(clean_posts,connection):

    inserted = 0
    updated = 0
    skipped =0
    processed = 0

    cursor = connection.cursor()

    try:
       
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
                INSERT INTO posts (user_id, post_id, title, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(post_id)
                DO UPDATE SET
                user_id = excluded.user_id,
                title = excluded.title,
                updated_at = excluded.updated_at
                WHERE posts.title <> excluded.title
            """, (
                post["user_id"],
                post["post_id"],
                post["title"],
                post["updated_at"]
            ))

            processed += 1

        return {
            "processed": processed,
            "inserted": inserted,
            "updated": updated,
            "skipped": skipped
        }
        
    except sqlite3.Error:
        logger.exception("DB records not updated due to upsert failure")
        raise

def update_last_successful_run(connection, clean_posts):

    cursor = connection.cursor()

    try:
        latest_updated_at = max(
            post["updated_at"]
            for post in clean_posts
        )

        cursor.execute("""
            INSERT INTO pipeline_metadata (
                pipeline_name,
                last_successful_run
            )
            VALUES (?, ?)
            ON CONFLICT(pipeline_name)
            DO UPDATE SET
                last_successful_run = excluded.last_successful_run
        """, ("posts_pipeline", latest_updated_at))

        
        logger.info(
             "Pipeline watermark updated: %s",
            latest_updated_at
               )

    except sqlite3.Error:
        logger.exception("Failed to update pipeline watermark")
        raise

def run_database_transaction(clean_posts):

    connection = None
    try:

       connection = sqlite3.connect(DATABASE_PATH)

       if not clean_posts:
            logger.info("No records processed. Watermark not updated.")
            return

       load_result = load_posts(clean_posts, connection)

       update_last_successful_run(connection, clean_posts)

       connection.commit()

       logger.info("Records processed: %s", load_result["processed"])
       logger.info("Inserted records: %s", load_result["inserted"])
       logger.info("Updated records: %s", load_result["updated"])
       logger.info("Skipped records: %s", load_result["skipped"])
       
       logger.info("Pipeline database transaction committed successfully")
   
    except sqlite3.Error:
        if connection:
            connection.rollback()

        logger.exception("Pipeline database transaction failed")
        raise
   
    finally:
        if connection:
            connection.close()