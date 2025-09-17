# src/ingestion/producer.py

import os
import time
import json
import logging
from dotenv import load_dotenv
from kafka import KafkaProducer
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- Basic Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# --- Load Credentials & Settings from Environment ---
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
VIDEO_ID = os.getenv("YOUTUBE_VIDEO_ID")
KAFKA_BROKER = "localhost:29092"
KAFKA_TOPIC = "chat_raw"

if not all([YOUTUBE_API_KEY, VIDEO_ID]):
    raise ValueError("Please set YOUTUBE_API_KEY and YOUTUBE_VIDEO_ID in your .env file")

# --- Initialize Kafka Producer ---
try:
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        api_version=(0, 11, 5) # Explicitly set for compatibility
    )
    logging.info("✅ Kafka Producer initialized successfully.")
except Exception as e:
    logging.error(f"❌ Failed to initialize Kafka Producer: {e}")
    exit()

# --- Initialize YouTube API Client ---
try:
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    logging.info("✅ YouTube API client initialized successfully.")
except Exception as e:
    logging.error(f"❌ Failed to initialize YouTube API client: {e}")
    exit()

def get_live_chat_id(video_id):
    """Fetches the liveChatId for a given YouTube video ID."""
    request = youtube.videos().list(part="liveStreamingDetails", id=video_id)
    response = request.execute()
    
    items = response.get("items", [])
    if not items:
        logging.error(f"❌ Video with ID '{video_id}' not found.")
        return None
        
    live_streaming_details = items[0].get("liveStreamingDetails")
    if live_streaming_details and "activeLiveChatId" in live_streaming_details:
        return live_streaming_details["activeLiveChatId"]
    else:
        logging.warning(f"⚠️ Video '{video_id}' is not an active live stream or has chat disabled.")
        return None

def fetch_chat_messages(live_chat_id, page_token=None):
    """Fetches a page of live chat messages."""
    request = youtube.liveChatMessages().list(
        liveChatId=live_chat_id,
        part="snippet,authorDetails",
        pageToken=page_token
    )
    return request.execute()

def main():
    """Main function to fetch and produce messages."""
    live_chat_id = get_live_chat_id(VIDEO_ID)
    if not live_chat_id:
        return

    logging.info(f"🚀 Starting to fetch messages for Live Chat ID: {live_chat_id}")
    next_page_token = None

    while True:
        try:
            response = fetch_chat_messages(live_chat_id, next_page_token)
            
            for item in response.get("items", []):
                message_data = {
                    "author": item["authorDetails"]["displayName"],
                    "timestamp": item["snippet"]["publishedAt"],
                    "message": item["snippet"]["displayMessage"],
                    "videoId": VIDEO_ID,
                    "messageId": item["id"]
                }
                
                # Send message to Kafka
                producer.send(KAFKA_TOPIC, value=message_data)
                logging.info(f"📨 Sent message to Kafka: {message_data['message']}")

            # The API provides the next token and polling interval
            next_page_token = response.get("nextPageToken")
            polling_interval = response.get("pollingIntervalMillis", 10000) / 1000
            
            # Wait for the recommended interval before the next poll
            time.sleep(polling_interval)

        except HttpError as e:
            logging.error(f"❌ An HTTP error occurred: {e}")
            # If the chat ends or an error occurs, wait longer before retrying
            time.sleep(30)
        except Exception as e:
            logging.error(f"❌ An unexpected error occurred: {e}")
            time.sleep(30)

# Main method
if __name__ == "__main__":
    main()