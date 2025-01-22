import feedparser
import requests

from bs4 import BeautifulSoup

def fetch_article_content(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Modify the selector based on the website's structure
        article_text = ' '.join([p.get_text() for p in soup.find_all('p')])
        return article_text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return ""

def fetch_rss_feed(url: str) -> list:
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries:
        print("Title:", entry.title)
        article_text = fetch_article_content(entry.link)
        if article_text:
            articles.append({
                'title': entry.title,
                'content': article_text
            })

    return articles

def write_to_file(messages: list, filename: str):
    try:
        with open(filename, 'w') as file:
            file.write('\n'.join(messages))
            return
    except Exception as e:
        print(f"Error in writting file '{filename}': {e}")
        return
    
def extract_message_content(message: str) -> str:
    soup = BeautifulSoup(message, 'html.parser')

    contemplator = ' '.join([p.get_text() for p in soup.find_all('contemplator')])
    final_answer = ' '.join([p.get_text() for p in soup.find_all('final_answer')])

    if final_answer.length > 0:
        return contemplator + "\n" + "FINAL ANSWER" + "\n" + final_answer
    else:
        return contemplator