# Hacker News to Mastodon Bot

## Overview

This Python script fetches the latest top story from Hacker News and posts it to a Mastodon account. It can operate in two modes:

1. **Console Mode**: Prints the latest top story details to the console.
2. **Mastodon Mode**: Posts the latest top story details to a Mastodon account.

The script is designed to work in a loop, with a configurable sleep time between each query to the Hacker News API. It also supports running in a Docker container and can store the last printed story ID in a Google Cloud Storage bucket to survive container restarts.

## Requirements

- Python 3.x
- `requests` library
- `mastodon.py` library
- Google Cloud Storage Python SDK

## Environment Variables

- `MASTODON_ACCESS_TOKEN`: Access token for Mastodon API
- `MASTODON_API_BASE_URL`: Base URL for Mastodon API
- `GCS_BUCKET_NAME`: Google Cloud Storage bucket name

## Installation

1. Clone the repository.
2. Create a Python virtual environment:

    ```bash
    python3 -m venv venv
    ```

3. Activate the virtual environment:

    ```bash
    source venv/bin/activate
    ```

4. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Console Mode

```bash
python main.py --mode console --sleep_time 300
```

### Mastodon Mode

```bash
python main.py --mode mastodon --sleep_time 300
```

## Deployment in Docker

1. Build the Docker image:

    ```bash
    docker build -t hn-to-mastodon-bot .
    ```

2. Run the Docker container:

    ```bash
    docker run -e MASTODON_ACCESS_TOKEN=<token> -e MASTODON_API_BASE_URL=<url> -e GCS_BUCKET_NAME=<bucket_name> hn-to-mastodon-bot
    ```

## Deployment in Google Cloud Function

1. Deploy the function:

    ```bash
    gcloud functions deploy hacker_news_function --runtime python39 --trigger-http --allow-unauthenticated
    ```

2. Set the environment variables in the Google Cloud Console.

## Google Cloud Storage (GCS) Requirement

The script uses a Google Cloud Storage bucket to store the ID of the last printed story. This is particularly useful in scenarios where the script is running in a Docker container and needs to survive container restarts without losing its state. By storing the last printed story ID in a GCS bucket, the script can continue from where it left off, ensuring that no stories are missed or duplicated.
