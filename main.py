import asyncio
import logging
import re,os,pytz
from datetime import datetime
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response, FileResponse
from fastapi import FastAPI, HTTPException
from feedgen.feed import FeedGenerator
from sites import *

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






def update_sites():
    site_extractors = {
        "tb": extract_tamilblaster,
        "hanime": extract_hanime,
        "yts": mirror_yts,
        "onejav": extract_jav
    }
    for site_name, extractor_function in site_extractors.items():
        links = extractor_function()
        generate_rss_feed(site_name, links)


def site_check(name):
     if name == "tb":
           links = extract_tamilblaster()
           return name,links
     
     elif name == "hanime":
          links = extract_hanime()
          return name,links
     
     elif name == "yts":
           links = mirror_yts()
           return name,links
     
     elif name == "onejav":
          links = extract_jav()
          return name,links
     
     else:
         return name,[]


def generate_rss_feed(name,links):
    fg = FeedGenerator()
    fg.title('Spidy RSS Feed')
    fg.link(href='http://', rel='alternate')
    fg.description(f'This is a Custom RSS feed')
    fg.language('en')
    for thumb,title, link in links:
        entry = fg.add_entry()
        entry.id(link)
        entry.title(title)
        entry.link(href=link)
        entry.description(f'This is an article titled {title}')
        now = datetime.now(pytz.utc)
        entry.pubDate(now)
    fg.rss_file(f"{name}.xml")
    return True

  
async def update_rss_feed():
    while True:
        try:
            logger.info(f"Fetching latest links at {datetime.now()}")
            update_sites()
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
async def get_rss(feed_name: str):
    if os.path.exists(f"{feed_name}.xml"):
        return FileResponse(f"{feed_name}.xml")
    else:
        generate_rss_feed(site_check(feed_name))
        return FileResponse(f"{feed_name}.xml")
    
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80, reload=True)
