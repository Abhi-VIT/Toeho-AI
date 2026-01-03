import requests
from bs4 import BeautifulSoup
import time

def scrape_twitter_demo():
    """
    Demonstrates why scraping Twitter with just requests/bs4 fails.
    """
    print("--- Attempting to scrape Twitter (X) ---")
    url = "https://twitter.com/search?q=python"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Twitter is heavily JavaScript based. The static HTML usually doesn't contain tweets.
            # We check for a common container or just print the title.
            print(f"Page Title: {soup.title.string.strip() if soup.title else 'No Title'}")
            
            # This class is often used for tweets, but likely won't be found in static HTML
            tweets = soup.find_all('div', {'data-testid': 'tweet'})
            if not tweets:
                print("Result: No tweets found. Twitter requires JavaScript (Selenium/Playwright) to load content.")
                print("Explanation: BeautifulSoup only parses the initial HTML response, which for Twitter is mostly empty scaffolding.")
            else:
                print(f"Result: Found {len(tweets)} tweets (Unexpected for static scraping!).")
        else:
            print(f"Failed to access Twitter. Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error scraping Twitter: {e}")
    print("\n")

def scrape_hacker_news():
    """
    Scrapes Hacker News (YCombinator) for top stories.
    This site works well with static scraping.
    """
    print("--- Scraping Hacker News (Social Media Fallback) ---")
    url = "https://news.ycombinator.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Hacker News stories are in 'tr' with class 'athing'
            # The subtext (points/author) is in the next row
            story_links = soup.select('.titleline > a')
            subtexts = soup.select('.subtext')
            
            print(f"Found {len(story_links)} stories. Showing top 5:\n")
            
            for i, (link, subtext) in enumerate(zip(story_links, subtexts)):
                if i >= 5: break
                
                title = link.get_text()
                href = link.get('href')
                
                # Extract points if available
                score_span = subtext.select_one('.score')
                points = score_span.get_text() if score_span else "0 points"
                
                print(f"{i+1}. {title}")
                print(f"   Link: {href}")
                print(f"   Stats: {points}")
                print("-" * 40)
                
            print("\nSuccess! BeautifulSoup works great for static content sites like Hacker News.")
            
        else:
            print(f"Failed to access Hacker News. Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error scraping Hacker News: {e}")

if __name__ == "__main__":
    print("Beginning Web Scraping Demo...\n")
    scrape_twitter_demo()
    time.sleep(1)
    scrape_hacker_news()
