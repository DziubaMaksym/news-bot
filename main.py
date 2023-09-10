import os
import json
import hashlib
import requests
import logging
from datetime import datetime
from mastodon import Mastodon
from google.cloud import storage

# Initialize logging
logging.basicConfig(level=logging.INFO)

# In-memory cache for the latest story ID
latest_story_id_cache = None

def hash_story_details(story_details):
    return hashlib.md5(json.dumps(story_details, sort_keys=True).encode()).hexdigest()

def get_latest_top_story_id(retry_count=3):
    global latest_story_id_cache
    if latest_story_id_cache:
        return latest_story_id_cache

    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    for _ in range(retry_count):
        try:
            response = requests.get(url)
            response.raise_for_status()
            latest_story_id_cache = json.loads(response.text)[0]
            return latest_story_id_cache
        except requests.RequestException as e:
            logging.error(f"HTTP request failed: {e}")
            continue
    return None

def get_story_details(story_id, retry_count=3):
    url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
    for _ in range(retry_count):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return json.loads(response.text)
        except requests.RequestException as e:
            logging.error(f"HTTP request failed: {e}")
            continue
    return None

def format_unix_time(unix_time):
    return datetime.utcfromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S UTC')

def post_to_mastodon(story_details, mastodon, hash_blob):
    story_id = story_details.get('id', 'N/A')
    current_hash = hash_story_details(story_details)
    if hash_blob.exists():
        last_hash = hash_blob.download_as_text()
        if current_hash == last_hash:
            return "Duplicate story. Not posting.", 202
    status = f"Latest Top Story on HackerNews: {story_details['title']}"
    status += f"🔗 URL: {story_details.get('url', 'N/A')}\n"
    status += f"👤 Author: {story_details.get('by', 'N/A')}\n"
    status += f"⭐ Score: {story_details.get('score', 'N/A')}\n"
    status += f"💬 Number of Comments: {len(story_details.get('kids', []))}\n"
    status += f"🕒 Posted At: {format_unix_time(story_details.get('time', 0))}\n"
    status += f"🔍 Original Story: https://news.ycombinator.com/item?id={story_id}\n"
    status += f"#News #Bot #HackerNews"
    mastodon.toot(status)
    hash_blob.upload_from_string(current_hash)
    return "Story posted successfully", 200

def hacker_news_function(request):
    global latest_story_id_cache

    try:
        mastodon = Mastodon(
            access_token=os.environ.get('MASTODON_ACCESS_TOKEN'),
            api_base_url=os.environ.get('MASTODON_API_BASE_URL')
        )

        storage_client = storage.Client()
        bucket_name = os.environ.get('GCS_BUCKET_NAME')
        bucket = storage_client.get_bucket(bucket_name)

        hash_blob = bucket.blob('latest_story_hash.txt')
        blob = bucket.blob('latest_story_id.txt')

        latest_top_story_id = get_latest_top_story_id()
        if latest_top_story_id is None:
            return "Could not fetch the latest story ID", 500

        last_posted_story_id = None
        if blob.exists():
            last_posted_story_id = int(blob.download_as_text())

        if last_posted_story_id is None or latest_top_story_id != last_posted_story_id:
            story_details = get_story_details(latest_top_story_id)
            if story_details:
                message, code = post_to_mastodon(story_details, mastodon, hash_blob)
                blob.upload_from_string(str(latest_top_story_id))
                return message, code
        else:
            return "Waiting for a new story...", 202

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return "Internal Server Error", 500
