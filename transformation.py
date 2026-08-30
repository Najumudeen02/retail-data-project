from logger import logger

def transform_posts(posts):
    clean_posts = []

    for post in posts:
        clean_post = {
                "user_id": post["user_id"],
                "post_id": post["post_id"],
                "title": post["title"],
                "updated_at": post["updated_at"]
        }
        clean_posts.append(clean_post)
    return clean_posts

def filter_incremental_posts(posts, last_run):

    if last_run is None:
        logger.info("First run: all records selected")
        return posts

    incremental_posts = [
        post for post in posts
        if post["updated_at"] > last_run
    ]

    logger.info(
        "Incremental filtering: %s of %s records selected",
        len(incremental_posts),
        len(posts)
    )

    return incremental_posts
