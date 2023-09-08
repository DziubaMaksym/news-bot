import os
import requests
import json
from datetime import datetime
from mastodon import Mastodon
from google.cloud import storage

def get_latest_top_story_id():
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    response = requests.get(url)
    return json.loads(response.text)[0] if response.status_code == 200 else None

def get_story_details(story_id):
    url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
    response = requests.get(url)
    return json.loads(response.text) if response.status_code == 200 else None

def format_unix_time(unix_time):
    return datetime.utcfromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S UTC')

def post_to_mastodon(story_details, mastodon):
    story_id = story_details.get('id', 'N/A')
    status = f"📰 Latest Top Story on #HackerNews: {story_details['title']}\n"
    status += f"🔗 URL: {story_details.get('url', 'N/A')}\n"
    status += f"👤 Author: {story_details.get('by', 'N/A')}\n"
    status += f"⭐ Score: {story_details.get('score', 'N/A')}\n"
    status += f"💬 Number of Comments: {len(story_details.get('kids', []))}\n"
    status += f"🕒 Posted At: {format_unix_time(story_details.get('time', 0))}\n"
    status += f"🔍 Original Story: https://news.ycombinator.com/item?id={story_id}\n"
    status += f"#News #Bot #HackerNews"
    mastodon.toot(status)

def hacker_news_function(request):
    mastodon = Mastodon(
        access_token=os.environ.get('MASTODON_ACCESS_TOKEN'),
        api_base_url=os.environ.get('MASTODON_API_BASE_URL')
    )

    # Initialize GCS
    storage_client = storage.Client()
    bucket_name = os.environ.get('GCS_BUCKET_NAME')
    bucket = storage_client.get_bucket(bucket_name)

    # Fetch last printed story ID from GCS
    blob = bucket.blob('latest_story_id.txt')
    last_printed_story_id = None
    if blob.exists():
        last_printed_story_id = int(blob.download_as_text())

    latest_top_story_id = get_latest_top_story_id()
    if latest_top_story_id and (last_printed_story_id is None or latest_top_story_id != last_printed_story_id):
        story_details = get_story_details(latest_top_story_id)
        if story_details:
            post_to_mastodon(story_details, mastodon)
            blob.upload_from_string(str(latest_top_story_id))
    else:
        return "Waiting for a new story...", 200

    return "Function executed successfully", 200
