from feed_aggregator import RSSFeedAggregator
from flask import Flask, send_file
import threading
import time
import os

app = Flask(__name__)

# Configuration
FEEDS = ['https://xxxclub.to/feed/MG.xml', 'https://www.torlock.com/adult/rss.xml','https://pornrips.to/feed/torrents']
UPDATE_INTERVAL = 4 * 60 * 60  # 4 hours
RSS_OUTPUT_FILE = 'public_aggregated_feed.xml'

def update_rss_periodically():
    """Background thread to update RSS feed periodically"""
    while True:
        try:
            aggregator = RSSFeedAggregator(
                feeds=FEEDS, 
                title='Spidy Feed',
                description='Periodically Updated RSS'
            )
            aggregator.generate_rss(RSS_OUTPUT_FILE)
            print(f"RSS Feed updated at {time.ctime()}")
        except Exception as e:
            print(f"RSS Update Error: {e}")
        
        time.sleep(UPDATE_INTERVAL)

@app.route('/')
def serve_rss():
    """Serve the aggregated RSS feed"""
    return send_file(
        RSS_OUTPUT_FILE, 
        mimetype='application/rss+xml'
    )

if __name__ == '__main__':
    # Create public directory if not exists
    os.makedirs('public', exist_ok=True)
    
    # Start background update thread
    update_thread = threading.Thread(
        target=update_rss_periodically, 
        daemon=True
    )
    update_thread.start()
    
    # Run Flask app
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)
