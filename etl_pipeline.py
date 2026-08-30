from extraction import extract_posts, extract_posts_from_file
from transformation import transform_posts,filter_incremental_posts
from validation import validate_posts
from database import (
    initialize_database,
    get_last_successful_run,
    initialize_pipeline_metadata,
    run_database_transaction
    )
from logger import logger

def main():

    initialize_database()
    initialize_pipeline_metadata()
    last_run = get_last_successful_run()

    if last_run is None:
        logger.info("First pipeline run detected")
    else:
        logger.info(
            "Incremental pipeline run. Last successful run: %s",
            last_run
        )

    #posts = extract_posts()
    posts = extract_posts_from_file()

    if posts is None:

        logger.warning("Extraction failed. Pipeline stopped.")

    else:

        incremental_posts = filter_incremental_posts(posts, last_run)

        clean_posts = transform_posts(incremental_posts)

        if validate_posts(incremental_posts, clean_posts):

            run_database_transaction(clean_posts)

        else:

            logger.error("Validation failed. Load stopped.")

if __name__ == "__main__":
    main()