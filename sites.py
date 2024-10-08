import requests,re
from bs4 import BeautifulSoup
from urllib.parse import urljoin



def extract_hanime():
    links = []
    data = []
    category = ["new-hanime","tsundere","harem","reverse","milf","romance","school","fantasy","ahegao","public","ntr","gb","incest","uncensored","ugly-bastard"]
    url = 'https://hanimes.org/category/'
    for cate in category:
         response = requests.get(url+cate)
         if response.status_code == 200:
              soup = BeautifulSoup(response.text, 'html.parser')
              ul_elements = soup.find_all('article', class_='TPost B')
              for ul in ul_elements:
                   title = ul.find_all('h2', class_='Title')[0].get_text().strip()
                   div_tags = ul.find_all('div', class_='TPMvCn')
                   for div in div_tags:
                        link = div.find_all('a',href=True)[0]['href']
                        imgs = ul.find_all('img',src=True)
                        img = [ img['src'] for img in imgs][0]
                        links.append([title,img,link])
              for title,img,link in links:
                  response = requests.get(link)
                  if response.status_code == 200:
                      soup = BeautifulSoup(response.content, 'html.parser')
                      result = [ a['src'] for a in soup.find_all('source', src=True)]
                      print([title,img,result[0]])
                      d = [title,result[0]]
                      if d not in data:
                         data.append(d)         
                  else:
                    logger.error(f"Failed to retrieve content. Status code: {response.status_code}")
              return data
         else:
                logger.error(f"Failed to retrieve content. Status code: {response.status_code}")
                return []



def extract_tamilblaster():
    url = 'https://1tamilblasters.mov'
    def extract_tb(url):
          pattern = re.compile(r'https://1tamilblasters\.mov/applications/core/interface/file/attachment\.php\?.*')
          response = requests.get(url)
          response.raise_for_status()
          soup = BeautifulSoup(response.content, 'html.parser')
          return [(a.get_text(strip=True), a['href']) for a in soup.find_all('a', href=True) if pattern.match(a['href'])]
    def extract_thumb(url):
          pattern = re.compile(r'https://picsxtra.com/images/*')
          response = requests.get(url)
          response.raise_for_status()
          soup = BeautifulSoup(response.content, 'html.parser')
          links = [ L.find_all('a', href=True) for L in [ a for a in soup.find_all('p')]]
          return links[4][0].find_all('img')[0]["data-src"]
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    links_info = []
    for tag in soup.find_all(['span', 'strong'], recursive=True):
        for a in tag.find_all('a', href=True):
            if "topic" in a['href'] and "APK" not in tag.get_text() and "Collection" not in tag.get_text():
                links_info.append(a['href'])
    unique_links = set()
    for href in links_info:
        for text, link in extract_tb(href):
            thumb = extract_thumb(href)
            text = text.replace(".torrent","")
            if (text, link) not in unique_links:
                unique_links.add((text, link))
    return unique_links


def extract_jav():
    return []

def extract_onejav_actress():
    base_url='https://onejav.com'
    torrent_links=[]
    try:
        response=requests.get(f'{base_url}/actress/')
        response.raise_for_status()
        soup=BeautifulSoup(response.content,'html.parser')
    except requests.RequestException as e:
        print(f"Error fetching the initial page: {e}")
        return []
    a_tags=soup.find_all('a')
    for tag in a_tags:
        href=tag.get('href')
        if href and "/actress/" in href and href!="/actress/":
            full_url=urljoin(base_url,href)
            try:
                response=requests.get(full_url)
                response.raise_for_status()
                soup=BeautifulSoup(response.content,'html.parser')
            except requests.RequestException as e:
                print(f"Error fetching {full_url}: {e}")
                continue
            a_tags=soup.find_all('a')
            torrent_links.extend(base_url+href for tag in a_tags if (href:=tag.get('href')) and ".torrent" in href)
    return torrent_links





def mirror_yts():
   return []

