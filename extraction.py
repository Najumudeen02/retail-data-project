
import json

import requests

from config import API_URL, API_TIMEOUT
from logger import logger

def extract_posts_from_file():

    try:
        with open("source_posts.json", "r", encoding="utf-8") as file:
            posts = json.load(file)

        logger.info("Source file extraction successful")
        return posts

    except (OSError, json.JSONDecodeError):
        logger.exception("Source file extraction failed")
        return None


def extract_posts():

    try:
        response = requests.get(
            API_URL,
            timeout=API_TIMEOUT
        )

        if response.status_code == 200:
            logger.info("Request succeeded")
            return response.json()

        logger.error(
            "Request failed with status code: %s",
            response.status_code
        )
        return None

    except requests.exceptions.RequestException:
        logger.exception("Request failed")
        return None