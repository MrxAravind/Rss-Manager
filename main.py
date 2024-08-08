import asyncio
import logging
import re
from datetime import datetime
import uvicorn
import requests
from bs4 import BeautifulSoup
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response, FileResponse
from fastapi import FastAPI, HTTPException
from feedgen.feed import FeedGenerator


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







def extract_hanime():
    links = []
    data = []
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
           for title,link in links:
                response = requests.get(link)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    result = [ a['src'] for a in soup.find_all('source', src=True)]
                    data.append([title,result[0]])         
           return data
      else:
           logger.error(f"Failed to retrieve content. Status code: {response.status_code}")


def generate_rss_feed():
    fg = FeedGenerator()
    fg.title('Spidy RSS Feed')
    fg.link(href='http://', rel='alternate')
    fg.description(f'This is a Custom RSS feed of {site_name}')
    fg.language('en')
    links = extract_hanime()
    for title, link in links:
        entry = fg.add_entry()
        entry.id(link)
        entry.title(title)
        entry.link(href=link)
        entry.description(f'This is an article titled {title}')
        now = datetime.datetime.now(pytz.utc)
        entry.pubDate(now)
    fg.rss_file("feed.xml")
    return True



  
async def update_rss_feed():
    while True:
        try:
            logger.info(f"Fetching latest links at {datetime.now()}")
            generate_rss_feed()
            logger.info("RSS feed updated successfully")
        except requests.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        await asyncio.sleep(600) 



@app.on_event("startup")
async def startup_event():
     asyncio.create_task(update_rss_feed())



@app.get("/rss/{feed_name}")
async def get_rss(feed_id: str):
    if os.path.exists(f"{feed_name}.xml"):
        return FileResponse(f"{feed_name}.xml")
    else:
        generate_rss_feed(feed_name)
        return FileResponse(f"{feed_name}.xml")
    
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6969, reload=True)
