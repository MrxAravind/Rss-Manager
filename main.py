import asyncio
import logging
import re
from datetime import datetime
import uvicorn
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

rss_feed_content = ""



def get_url(url):
      response = requests.get(url)
      if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            result = [ a['src'] for a in soup.find_all('source', src=True)]
            return i[0]
      else:
           logger.error(f"Failed to retrieve content. Status code: {response.status_code}")


def extract_home():
    links = []
    url = 'https://hanimes.org/'
    response = requests.get(url)
    if response.status_code == 200:
           soup = BeautifulSoup(response.text, 'html.parser')
           ul_elements = soup.find_all('article', class_='TPost B')
           for ul in ul_elements:
                title = ul.find_all('h2', class_='Title')[0].get_text().strip()
                div_tags = ul.find_all('div', class_='TPMvCn')
                for div in div_tags:
                     link = div.find_all('a',href=True)[0]['href']
                     links.append([title,link])
           return links 
            
    else:
           logger.error(f"Failed to retrieve content. Status code: {response.status_code}")



def generate_rss_feed(data):
    rss_items = ""
    for text, link in data:
        rss_items += f"""
        <item>
            <title>{text}</title>
            <link>{link}</link>
        </item>
        """

    rss_feed = f"""
    <?xml version="1.0" encoding="UTF-8" ?>
    <rss version="2.0">
        <channel>
            <title>MrSpidy Hanimes.org Rss</title>
            <link>https://hanimes.org/</link>
            <description>This is A Unofficial RSS Feed for Hanimes.org by MrSpidy</description>
            {rss_items}
        </channel>
    </rss>
    """
    return rss_feed



  
async def update_rss_feed():
    global rss_feed_content
    while True:
        try:
            logger.info(f"Fetching latest links at {datetime.now()}")
            links = extract_home()
            data = [ [ title,get_url(link)] for title,link in links ]
            rss_feed_content = generate_rss_feed( data)
            logger.info("RSS feed updated successfully")
        except requests.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
        except Exception as e:
            logger.error(f"An error occurred: {e}")

        await asyncio.sleep(600) 



@app.on_event("startup")
async def startup_event():
     asyncio.create_task(update_rss_feed())


@app.get("/rss", response_class=HTMLResponse)
async def rss_feed():
    return Response(content=rss_feed_content, media_type="application/rss+xml")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6969, reload=True)
