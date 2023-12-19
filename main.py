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

popular_hashtags = set([
    "technology", "science", "bigdata", "iphone", "ios",
    "android", "mobile", "video", "design", "innovation",
    "startups", "tech", "cloud", "gadget", "instatech",
    "electronic", "device", "techtrends", "technews", "engineering",
    "ai", "ml", "cybersecurity", "blockchain", "devops",
    "opensource", "datacenter", "automation", "software",
    "hardware", "networking", "virtualization", "iot", "robotics",
    "cybercrime", "programming", "coding", "computerscience",
    "privacy", "hacking", "hacker", "hackers", "hack", "hackathon",
    "opensourcecommunity", "pythonprogramming", "ansible", "terraform",
    "codinglife", "linux", "hashicorp", "systemadmin", "cloudcomputing",
    "dataprivacy", "datalove", "coderslife", "opensourcecode", "devopslife",
    "techtalks", "privacyadvocate", "technologytrends", "cybersecuritytips",
    "innovationnation", "developmentgoals", "codingjourney", "techworld",
    "privacyfirst", "hashistack","ethicaltech", "quantumcomputing", "infosec", 
    "networksecurity", "smartdevices", "futuretech", "machinelearning", "deeplearning",
    "cloudnative", "digitaltransformation", "microservices", "api",
    "datascience", "devsecops", "edtech", "fintech", "govtech",
    "5Gtechnology", "arvr", "wearables", "biometrics", "zerotrust",
    "securecoding", "kubernetes", "privacybydesign", "cryptography",
    "dataprotection", "smartcity", "agiledevelopment", "gitops",
    "datavisualization", "fullstack", "frontend", "backend",
    "sre", "continuousintegration", "continuousdelivery", "userexperience",
    "uxdesign", "servicemesh", "webdevelopment", "appdevelopment",
    "ethicalhacking", "threatintelligence", "surveillancecapitalism",
    "dataethics", "opensourceplatform", "greentech", "cleantech",
    "techtips", "codingbootcamp", "girlswhocode", "techforgood",
    "datagovernance", "internetfreedom", "techpolicy", "enterpriseit",
    "internetofthings", "riskmanagement", "devcommunity",
    "womenintech", "technologyrocks", "digitalprivacy",
    "techindustry", "codequality", "websecurity", "mobilesecurity",
    "datapipeline", "realtimeanalytics", "bigdataanalytics",
    "digitalidentity", "computervision", "naturallanguageprocessing",
    "humancomputerinteraction", "augmentedreality", "virtualreality",
    "amazonwebservices", "googlecloud", "microsoftazure", "ibmcloud",
    "oraclecloud", "salesforce", "adobe", "cisco", "dell", "hp",
    "intel", "nvidia", "vmware", "redhat", "samsung", "apple",
    "netflix", "facebook", "linkedin", "twitter", "slack",
    "github", "gitlab", "jfrog", "atlassian", "splunk", "elastic",
    "servicenow", "datadog", "newrelic", "palantir", "zoom",
    "dropbox", "qualcomm", "amd", "tesla", "spacex", "tencent",
    "alibaba", "huawei", "sony", "sap", "wework", "shopify",
    "unity", "epicgames", "zoho", "rackspace", "cloudera",
    "edgecomputing", "serverless", "containerization", "aiethics",
    "techinclusion", "cloudsecurity", "itmanagement", "virtualreality",
    "augmentedreality", "quantumai", "neuralnetworks", "cloudmigration",
    "datasecurity", "blockchaindevelopment", "internetofbehaviors", "5g",
    "greenit", "sustainabletech", "remotework", "techinnovation",
    "techleadership", "enterprisesoftware", "itconsulting", "itautomation",
    "techregulation", "dataprivacylaws", "techcompliance", "aiinhealthcare",
    "selfdrivingcars", "wearabletech", "smartinfrastructure", "techeducation",
    "digitalskills", "codingforkids", "womenwhotech", "techdiversity",
    "cloudstrategies", "techstartups", "iotsecurity", "web3",
    "blockchaintechnology", "cryptocurrency", "nft", "metaverse",
    "docker", "ansible", "jenkins", "grafana", "prometheus",
    "puppet", "chef", "circleci", "travisci", "git",
    "linode", "digitalocean", "heroku", "bitbucket", "confluence",
    "trello", "asana", "basecamp", "twilio", "stripe",
    "square", "paypal", "symantec", "fortinet", "fireeye",
    "cyberark", "f5networks", "juniper", "arista", "brocade",
    "checkpoin", "crowdstrike", "sophos", "trendmicro", "malwarebytes",
    "kaspersky", "mcafee", "eset", "avast", "avg",
    "symphony", "signal", "telegram", "wechat", "line",
    "kakao", "viber", "discord", "skype", "teams",
    "bluejeans", "gopro", "fitbit", "garmin", "polar",
    "suunto", "xiaomi", "oppo", "vivo", "oneplus",
    "lg", "panasonic", "sharp", "toshiba", "hitachi",
    "fujitsu", "asus", "lenovo", "msi", "razer",
    "corsair", "logitech", "steelseries", "hyperx", "alienware",
    "macbook", "gpt-4", "gpt", "openai", "tesla"
])


def hash_story_details(story_details):
    return hashlib.sha256(story_details['title'].encode()).hexdigest()

def get_latest_top_story_id():
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return json.loads(response.text)[0]
    except requests.RequestException as e:
        logging.error(f"HTTP request failed: {e}")
        return None

def get_story_details(story_id):
    url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return json.loads(response.text)
    except requests.RequestException as e:
        logging.error(f"HTTP request failed: {e}")
        return None

def format_unix_time(unix_time):
    return datetime.utcfromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S UTC')
    

def post_to_mastodon(story_details, mastodon, hash_blob):
    current_hash = hash_story_details(story_details)
    
    last_hash = None
    if hash_blob.exists():
        last_hash = hash_blob.download_as_text()

    if current_hash == last_hash:
        return "Duplicate story. Not posting.", 208

    # Extract words from the title and convert them to lowercase
    title_words = set(story_details['title'].lower().split())

    # Find matching hashtags
    matching_hashtags = {f"#{tag}" for tag in popular_hashtags if tag in title_words}
    standard_hashtags = {"#news", "#bot", "#hackernews", "#hackernewsbot"}

    # Construct the status message
    status = f"📜 Latest Top Story on #HackerNews: {story_details['title']}\n"
    status += f"🔍 Original Story: {story_details.get('url', 'N/A')}\n"
    status += f"👤 Author: {story_details.get('by', 'N/A')}\n"
    status += f"⭐ Score: {story_details.get('score', 'N/A')}\n"
    status += f"💬 Number of Comments: {len(story_details.get('kids', []))}\n"
    status += f"🕒 Posted At: {format_unix_time(story_details.get('time', 0))}\n"
    status += f"🔗 URL: https://news.ycombinator.com/item?id={story_details.get('id', 'N/A')}\n"
    status += " ".join(matching_hashtags | standard_hashtags)
    
    mastodon.toot(status)
    hash_blob.upload_from_string(current_hash)
    return "Story posted successfully", 200


def hacker_news_function(request):
    try:
        latest_top_story_id = get_latest_top_story_id()
        if latest_top_story_id is None:
            return "Could not fetch the latest story ID", 500
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
            return "Waiting for a new story...", 208

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return "Internal Server Error", 500
