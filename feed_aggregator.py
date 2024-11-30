import feedparser
import PyRSS2Gen
from datetime import datetime
import urllib.request
import xml.etree.ElementTree as ET
import argparse
import logging
from typing import List, Dict, Optional

class RSSFeedAggregator:
    def __init__(self, feeds: List[str], max_items: int = 100, 
                 title: str = "Aggregated RSS Feed", 
                 description: str = "Consolidated RSS Feed"):
        """
        Initialize RSS Feed Aggregator
        
        :param feeds: List of RSS feed URLs to aggregate
        :param max_items: Maximum number of items to include in final feed
        :param title: Title of the aggregated feed
        :param description: Description of the aggregated feed
        """
        self.feeds = feeds
        self.max_items = max_items
        self.title = title
        self.description = description
        
        # Configure logging
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def fetch_feed(self, url: str) -> List[Dict]:
        """
        Fetch and parse an individual RSS feed
        
        :param url: URL of the RSS feed
        :return: List of parsed feed items
        """
        try:
            self.logger.info(f"Fetching feed from {url}")
            feed = feedparser.parse(url)
            
            # Extract relevant item information
            items = []
            for entry in feed.entries:
                item = {
                    'title': entry.get('title', 'Untitled'),
                    'link': entry.get('link', ''),
                    'description': entry.get('description', ''),
                    'pubDate': entry.get('published_parsed', datetime.now()),
                    'source_url': url
                }
                items.append(item)
            
            return items
        
        except Exception as e:
            self.logger.error(f"Error fetching feed from {url}: {e}")
            return []

    def aggregate_feeds(self) -> List[Dict]:
        """
        Aggregate items from all feeds
        
        :return: Sorted list of aggregated feed items
        """
        all_items = []
        
        for feed_url in self.feeds:
            feed_items = self.fetch_feed(feed_url)
            all_items.extend(feed_items)
        
        # Sort items by publication date (most recent first)
        all_items.sort(key=lambda x: x['pubDate'], reverse=True)
        
        # Limit to max_items
        return all_items[:self.max_items]

    def generate_rss(self, output_file: str = 'aggregated_feed.xml') -> None:
        """
        Generate combined RSS feed
        
        :param output_file: Path to save the aggregated RSS feed
        """
        aggregated_items = self.aggregate_feeds()
        
        # Create RSS 2.0 feed
        rss_items = []
        for item in aggregated_items:
            rss_item = PyRSS2Gen.RSSItem(
                title=item['title'],
                link=item['link'],
                description=item['description'],
                pubDate=item['pubDate']
            )
            rss_items.append(rss_item)
        
        rss = PyRSS2Gen.RSS2(
            title=self.title,
            link='',
            description=self.description,
            lastBuildDate=datetime.now(),
            items=rss_items
        )
        
        # Write to file
        rss.write_xml(open(output_file, 'w'), encoding='utf-8')
        self.logger.info(f"Aggregated RSS feed saved to {output_file}")

def main():
    """
    Command-line interface for RSS Feed Aggregator
    """
    parser = argparse.ArgumentParser(description='Aggregate Multiple RSS Feeds')
    parser.add_argument('feeds', nargs='+', help='URLs of RSS feeds to aggregate')
    parser.add_argument('--max-items', type=int, default=100, 
                        help='Maximum number of items in aggregated feed')
    parser.add_argument('--output', default='aggregated_feed.xml', 
                        help='Output file for aggregated RSS feed')
    parser.add_argument('--title', default='Aggregated RSS Feed', 
                        help='Title of the aggregated feed')
    parser.add_argument('--description', 
                        default='Consolidated RSS Feed from Multiple Sources', 
                        help='Description of the aggregated feed')
    
    args = parser.parse_args()
    
    aggregator = RSSFeedAggregator(
        feeds=args.feeds, 
        max_items=args.max_items,
        title=args.title,
        description=args.description
    )
    
    aggregator.generate_rss(args.output)

if __name__ == '__main__':
    main()
