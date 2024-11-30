import { feedparser } from 'feedparser-node';

export default {
  async fetch(request, env, ctx) {
    // Configuration
    const FEEDS = [
      'https://example1.com/rss',
      'https://example2.com/rss',
      'https://example3.com/rss'
    ];

    try {
      // Fetch and aggregate feeds
      const aggregatedItems = await aggregateFeeds(FEEDS);
      
      // Generate RSS XML
      const rssXml = generateRSS(aggregatedItems, {
        title: 'Aggregated RSS Feed',
        description: 'Combined RSS from Multiple Sources',
        link: request.url
      });

      // Return RSS response
      return new Response(rssXml, {
        headers: {
          'Content-Type': 'application/rss+xml',
          'Cache-Control': 'public, max-age=3600', // 1-hour cache
          'Access-Control-Allow-Origin': '*'
        }
      });
    } catch (error) {
      return new Response(`Error generating feed: ${error.message}`, { 
        status: 500 
      });
    }
  }
};

// Helper function to fetch and parse RSS feeds
async function fetchFeed(url) {
  try {
    const response = await fetch(url);
    const xmlText = await response.text();
    
    return new Promise((resolve, reject) => {
      const items = [];
      
      feedparser(xmlText)
        .on('error', reject)
        .on('data', (item) => {
          items.push({
            title: item.title || 'Untitled',
            link: item.link || '',
            description: item.description || '',
            pubDate: item.pubdate || new Date(),
            guid: item.guid || item.link
          });
        })
        .on('end', () => resolve(items));
    });
  } catch (error) {
    console.error(`Error fetching ${url}: ${error}`);
    return [];
  }
}

// Aggregate feeds from multiple sources
async function aggregateFeeds(feedUrls, maxItems = 100) {
  // Fetch all feeds concurrently
  const feedResults = await Promise.all(
    feedUrls.map(url => fetchFeed(url))
  );

  // Flatten and sort items
  const allItems = feedResults.flat()
    .sort((a, b) => new Date(b.pubDate) - new Date(a.pubDate))
    .slice(0, maxItems);

  return allItems;
}

// Generate RSS XML
function generateRSS(items, metadata) {
  const { title, description, link } = metadata;
  const pubDate = new Date().toUTCString();

  // RSS 2.0 XML generation
  const xmlItems = items.map(item => `
    <item>
      <title><![CDATA[${escapeXML(item.title)}]]></title>
      <link>${escapeXML(item.link)}</link>
      <description><![CDATA[${escapeXML(item.description)}]]></description>
      <pubDate>${new Date(item.pubDate).toUTCString()}</pubDate>
      <guid>${escapeXML(item.guid)}</guid>
    </item>
  `).join('\n');

  return `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" 
  xmlns:atom="http://www.w3.org/2005/Atom"
  xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>${escapeXML(title)}</title>
    <link>${escapeXML(link)}</link>
    <description>${escapeXML(description)}</description>
    <pubDate>${pubDate}</pubDate>
    <atom:link 
      href="${escapeXML(link)}" 
      rel="self" 
      type="application/rss+xml" />
    ${xmlItems}
  </channel>
</rss>`;
}

// XML escaping utility
function escapeXML(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
           }
