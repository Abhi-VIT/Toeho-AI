import time
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from textblob import TextBlob
import matplotlib.pyplot as plt
import seaborn as sns

# Setup
sns.set_theme(style="whitegrid")

def get_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless') # Keep it visible for now or uncomment for headless
    driver = webdriver.Chrome(options=options)
    return driver

def get_soup(driver, url):
    try:
        driver.get(url)
        time.sleep(3)
        return BeautifulSoup(driver.page_source, 'html.parser')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def chunk_text(text, chunk_size=500, overlap=50):
    """
    Splits text into chunks of `chunk_size` characters with `overlap`.
    """
    if not text:
        return []
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunks.append(text[start:end])
        if end == text_len:
            break
        start += (chunk_size - overlap)
    return chunks

def analyze_sentiment_with_chunks(text):
    """
    Analyzes sentiment by averaging the polarity of text chunks.
    """
    if not text:
        return 0.0, 'Neutral'
    
    chunks = chunk_text(text)
    if not chunks:
        return 0.0, 'Neutral'
        
    chunk_polarities = []
    for chunk in chunks:
        blob = TextBlob(chunk)
        chunk_polarities.append(blob.sentiment.polarity)
    
    # Average polarity
    avg_polarity = sum(chunk_polarities) / len(chunk_polarities)
    
    if avg_polarity > 0.05:
        return avg_polarity, 'Positive'
    elif avg_polarity < -0.05:
        return avg_polarity, 'Negative'
    else:
        return avg_polarity, 'Neutral'

def main():
    # Scrape Homepage for Links
    url = "https://www.thehindu.com/"
    driver = get_driver()
    print("Fetching homepage...")
    soup = get_soup(driver, url)

    links = []
    seen_urls = set()

    if soup:
        # Gather more links
        for tag in soup.select('h3.title a, h2.title a, div.story-card a'):
            href = tag.get('href')
            if href and href not in seen_urls and 'thehindu.com' in href and '/article' in href:
                links.append(href)
                seen_urls.add(href)

    # Fetch top 5 articles for testing (limit to save time)
    links = links[:15]
    print(f"Found {len(links)} articles to process.")

    # Scrape Individual Articles
    articles_data = []

    for link in links:
        print(f"Scraping: {link}")
        try:
            art_soup = get_soup(driver, link)
            if not art_soup: continue
            
            # Headline
            title_tag = art_soup.select_one('h1.title')
            title = title_tag.get_text(strip=True) if title_tag else "N/A"
            
            # Category
            parts = link.split('/')
            category = "General"
            if 'news' in parts:
                 try:
                     idx = parts.index('news')
                     if idx + 1 < len(parts):
                         category = parts[idx+1].capitalize()
                 except:
                     pass
            elif 'sport' in parts:
                category = 'Sport'
            elif 'business' in parts:
                category = 'Business'
            elif 'entertainment' in parts:
                category = 'Entertainment'
                
            # Date Extraction
            pub_date = None
            meta_date = art_soup.find('meta', property='article:published_time')
            if meta_date:
                dt_str = meta_date.get('content')
                try:
                    pub_date = datetime.fromisoformat(dt_str).date()
                except:
                    pass
            
            if not pub_date:
                pub_date = datetime.now().date()

            # Content
            body_div = art_soup.select_one('div[id^="content-body-"]')
            content = body_div.get_text(strip=True) if body_div else ""
            if not content:
                 paras = art_soup.select('div.article-body p')
                 content = " ".join([p.get_text(strip=True) for p in paras])
            
            articles_data.append({
                'url': link,
                'headline': title,
                'category': category,
                'date': pub_date,
                'content': content
            })
            
        except Exception as e:
            print(f"Error scraping {link}: {e}")

    driver.quit()

    # Apply Sentiment Analysis
    df = pd.DataFrame(articles_data)
    if not df.empty:
        df[['sentiment_score', 'sentiment_label']] = df['content'].apply(
            lambda x: pd.Series(analyze_sentiment_with_chunks(x))
        )

        print("\nProcessed Data (with Chunking):")
        print(df[['headline', 'category', 'date', 'sentiment_label', 'sentiment_score']].head())
        
        # Save to CSV for verification
        df.to_csv('fetch_data_with_chunking.csv', index=False)
        print("\nData saved to 'fetch_data_with_chunking.csv'")
    else:
        print("No articles extracted.")

if __name__ == "__main__":
    main()
