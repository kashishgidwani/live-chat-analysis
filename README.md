# Live Chat NLP Pipeline
Real-time sentiment and toxicity analysis for YouTube Live chats using Kafka, Spark, and NLP transformers.

## Architecture
![diagram](<ChatGPT Image Sep 16, 2025, 10_32_50 PM.png>)

The system consists of four main components:
1. **Ingestion Service**: Fetches live chats from YouTube API and publishes to Kafka
2. **Processing Service**: Consumes chats, runs NLP models, publishes enriched data
3. **Sinks Service**: Writes to MongoDB and sends email alerts
4. **Dashboard**: Streamlit app for real-time visualization

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/kashishgidwani/live-chat-analysis.git
   cd live-chat-analysis

