
import time
import base64
import io
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import spacy
import re
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from textblob import TextBlob
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# Set Matplotlib backend to Agg for web server usage
plt.switch_backend('Agg')
sns.set_theme(style="whitegrid")

# Load Spacy Model (Lazy loading or global)
try:
    nlp = spacy.load("en_core_web_sm")
except:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    # Suppress logging
    options.add_argument('log-level=3') 
    driver = webdriver.Chrome(options=options)
    return driver

def get_soup(driver, url):
    try:
        driver.get(url)
        time.sleep(2) # reduced wait for speed
        return BeautifulSoup(driver.page_source, 'html.parser')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def chunk_text(text, chunk_size=500, overlap=50):
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
    if not text:
        return 0.0, 'Neutral'
    
    chunks = chunk_text(text)
    if not chunks:
        return 0.0, 'Neutral'
        
    chunk_polarities = []
    for chunk in chunks:
        blob = TextBlob(chunk)
        chunk_polarities.append(blob.sentiment.polarity)
    
    avg_polarity = sum(chunk_polarities) / len(chunk_polarities)
    
    if avg_polarity > 0.05:
        return avg_polarity, 'Positive'
    elif avg_polarity < -0.05:
        return avg_polarity, 'Negative'
    else:
        return avg_polarity, 'Neutral'

def map_category(row):
    url = str(row['url']).lower()
    content = str(row['content']).lower()
    headline = str(row['headline']).lower()
    
    # Priority Mapping
    if 'sport' in url or 'cricket' in url or 'football' in url:
        return 'Sports'
    elif 'business' in url or 'economy' in url or 'market' in url:
        return 'Business'
    elif 'tech' in url or 'technology' in url or 'science' in url:
        return 'Tech'
    elif 'entertainment' in url or 'movie' in url or 'film' in url:
        return 'Entertainment'
    elif 'politics' in url or 'election' in url or 'government' in url:
        return 'Politics'
    
    # Content Fallback
    if 'politics' in content or 'election' in content: return 'Politics'
    if 'sport' in content or 'match' in content: return 'Sports'
    if 'business' in content or 'stock' in content: return 'Business'
    if 'movie' in content or 'cinema' in content: return 'Entertainment'
    if 'technology' in content or 'software' in content: return 'Tech'
    
    return 'General' # Changed from 'Other' to ensure we have a category

def extract_entities(text):
    doc = nlp(text)
    people = []
    orgs = []
    locs = []
    
    for ent in doc.ents:
        clean_text = ent.text.replace("'s", "").strip()
        if len(clean_text) > 1:
            if ent.label_ == "PERSON":
                people.append(clean_text)
            elif ent.label_ == "ORG":
                orgs.append(clean_text)
            elif ent.label_ in ["GPE", "LOC"]:
                locs.append(clean_text)
    return people, orgs, locs

def clean_text_for_topic(text):
    text = str(text).lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text

def scrape_and_process(base_url):
    driver = get_driver()
    articles_data = []
    try:
        soup = get_soup(driver, base_url)
        links = []
        seen_urls = set()
        
        if soup:
            # Gather links similar to the notebook
            for tag in soup.select('h3.title a, h2.title a, div.story-card a'):
                href = tag.get('href')
                if href and href not in seen_urls and 'http' in href and '/article' in href:
                    links.append(href)
                    seen_urls.add(href)
        
        # Limit to 15 articles as per requirement
        links = links[:50]
        
        for link in links:
            try:
                art_soup = get_soup(driver, link)
                if not art_soup: continue
                
                title_tag = art_soup.select_one('h1.title')
                title = title_tag.get_text(strip=True) if title_tag else "N/A"
                
                # Basic Category
                parts = link.split('/')
                category = "General"
                # (Simplified extraction, map_category will do better job)
                
                # Date
                pub_date = str(datetime.now().date())
                meta_date = art_soup.find('meta', property='article:published_time')
                if meta_date:
                    pub_date = meta_date.get('content', pub_date)

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
                print(f"Skipping {link}: {e}")
                
    finally:
        driver.quit()
        
    df = pd.DataFrame(articles_data)
    if df.empty:
        return df

    # Sentiment
    df[['sentiment_score', 'sentiment_label']] = df['content'].apply(
        lambda x: pd.Series(analyze_sentiment_with_chunks(x))
    )
    
    # Categories
    df['Mapped_Category'] = df.apply(map_category, axis=1)
    
    # NER
    df['full_text'] = df['headline'] + ". " + df['content']
    df['People'], df['Orgs'], df['Locations'] = zip(*df['full_text'].apply(extract_entities))
    
    return df

def generate_plots(df):
    plots = {}
    
    # 1. Category Distribution
    plt.figure(figsize=(10, 6))
    cat_counts = df['Mapped_Category'].value_counts()
    sns.barplot(x=cat_counts.index, y=cat_counts.values, palette='viridis')
    plt.title("Articles by Category")
    plt.xlabel("Category")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plots['category_dist'] = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    
    # 2. Sentiment by Category (Stacked)
    plt.figure(figsize=(10, 6))
    sentiment_counts = df.groupby(['Mapped_Category', 'sentiment_label']).size().unstack(fill_value=0)
    sentiment_counts.plot(kind='bar', stacked=True, figsize=(10, 6), colormap='viridis')
    plt.title("Sentiment Distribution by Category")
    plt.xlabel("Category")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plots['sentiment_cat'] = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close() 
    
    # 3. Top NER Entities (People, Orgs, Locs)
    all_people = [p for sub in df['People'] for p in sub]
    all_orgs = [o for sub in df['Orgs'] for o in sub]
    all_locs = [l for sub in df['Locations'] for l in sub]
    
    # Helper to plot top 10
    def plot_top10(data, title):
        if not data: return None
        plt.figure(figsize=(10, 6))
        counts = Counter(data).most_common(10)
        labels, values = zip(*counts)
        sns.barplot(x=list(values), y=list(labels), palette='magma')
        plt.title(title)
        plt.xlabel("Count")
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()
        return b64

    plots['top_people'] = plot_top10(all_people, "Top 10 People Mentioned")
    plots['top_orgs'] = plot_top10(all_orgs, "Top 10 Organizations Mentioned")
    plots['top_locs'] = plot_top10(all_locs, "Top 10 Locations Mentioned")

    # --- ADVANCED / NEW PLOTS ---

    # 4. Top 20 Frequent Words
    try:
        text_data = df['headline'] + " " + df['content']
        cv = CountVectorizer(stop_words='english', max_features=20)
        word_counts = cv.fit_transform(text_data)
        sum_words = word_counts.sum(axis=0)
        words_freq = [(word, sum_words[0, idx]) for word, idx in cv.vocabulary_.items()]
        words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
        
        if words_freq:
            words, counts = zip(*words_freq)
            plt.figure(figsize=(12, 6))
            sns.barplot(x=list(words), y=list(counts), palette='GnBu_r')
            plt.title("Top 20 Frequent Words")
            plt.xticks(rotation=45, ha='right')
            plt.ylabel("Frequency")
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plots['word_freq'] = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
    except Exception as e:
        print(f"Word Freq Error: {e}")

    # 5. Overall Sentiment Pie Chart
    try:
        plt.figure(figsize=(6, 6))
        sent_counts = df['sentiment_label'].value_counts()
        if not sent_counts.empty:
            plt.pie(sent_counts, labels=sent_counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
            plt.title("Overall Sentiment Distribution")
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plots['sentiment_pie'] = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
    except Exception as e:
        print(f"Pie Chart Error: {e}")

    # 6. Sentiment Heatmap
    try:
        plt.figure(figsize=(8, 6))
        heatmap_data = df.groupby(['Mapped_Category', 'sentiment_label']).size().unstack(fill_value=0)
        if not heatmap_data.empty:
            sns.heatmap(heatmap_data, annot=True, fmt='d', cmap='YlGnBu')
            plt.title("Sentiment Count per Category")
            plt.ylabel("Category")
            plt.xlabel("Sentiment")
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plots['sentiment_heatmap'] = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
    except Exception as e:
        print(f"Heatmap Error: {e}")

    # 7. Topic Modeling
    try:
        df['cleaned_topic_text'] = df['content'].apply(clean_text_for_topic)
        # Handle small datasets
        n_topics = 5 if len(df) >= 7 else min(len(df), 3) 
        
        # Need at least a few articles and words
        if len(df) > 2:
            vectorizer = CountVectorizer(max_df=0.95, min_df=1, stop_words='english')
            dtm = vectorizer.fit_transform(df['cleaned_topic_text'])
            
            lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
            lda.fit(dtm)
            
            # Assign Topics
            topic_results = lda.transform(dtm)
            df['Topic'] = topic_results.argmax(axis=1) + 1
            
            # Plot
            plt.figure(figsize=(8, 5))
            topic_counts = df['Topic'].value_counts().sort_index()
            sns.barplot(x=topic_counts.index, y=topic_counts.values, palette='viridis')
            plt.title("Number of Articles per Topic")
            plt.xlabel("Topic ID")
            plt.ylabel("Count")
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plots['topic_dist'] = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
    except Exception as e:
        print(f"LDA Error: {e}")
    
    return plots, df
