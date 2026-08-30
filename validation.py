from logger import logger


def validate_posts(posts, clean_posts):

    valid = True

    if len(posts) == len(clean_posts):
        logger.info("Validation passed: all records transformed")
    else:
        logger.error("Validation failed: transformation count mismatch")
        valid = False

    if any(post["post_id"] is None for post in clean_posts):
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

    if any(not post["title"] for post in clean_posts):
        logger.error("Validation failed: missing titles")
        valid = False
    else:
        logger.info("Validation passed: no missing titles")

    return valid