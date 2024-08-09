import requests,re
from bs4 import BeautifulSoup



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
                else:
                    logger.error(f"Failed to retrieve content. Status code: {response.status_code}")
           return data
    else:
           logger.error(f"Failed to retrieve content. Status code: {response.status_code}")




def extract_tamilblaster():
    url = 'https://1tamilblasters.mov'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    links_info = []
    for tag in soup.find_all(['span', 'strong'], recursive=True):
        for a in tag.find_all('a', href=True):
            if "topic" in a['href'] and "APK" not in tag.get_text() and "Collection" not in tag.get_text():
                links_info.append(a['href'])
    unique_links = set()
    for href in links_info[:100]:
        pattern = re.compile(r'https://1tamilblasters\.mov/applications/core/interface/file/attachment\.php\?.*')
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        result = [(a.get_text(strip=True), a['href']) for a in soup.find_all('a', href=True) if pattern.match(a['href'])]
        for text, link in result:
            if (text, link) not in unique_links:
                print(f"Text: {text}\nLink: {link}\n")
                unique_links.add((text, link))
    return unique_links
