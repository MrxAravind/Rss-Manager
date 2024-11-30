from feed_aggregator import RSSFeedAggregator

feeds = ['https://xxxclub.to/feed/MG.xml', 'https://www.torlock.com/adult/rss.xml','https://pornrips.to/feed/torrents']
aggregator = RSSFeedAggregator(feeds)
aggregator.generate_rss('feed.xml')
