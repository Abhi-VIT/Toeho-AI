# News Dashboard with AI Analytics

A comprehensive Django-based News Dashboard that aggregates news articles, analyzes them using advanced NLP techniques, and presents insights through interactive visualizations.

## Features

- **News Aggregation**: Scrapes news articles (headlines, content, metadata) using Selenium and BeautifulSoup.
- **Sentiment Analysis**: Analyzes the sentiment of articles (Positive, Negative, Neutral) using TextBlob, with chunk-based processing for better accuracy on long texts.
- **Topic Modeling**: Automatically categorizes articles into topics using Latent Dirichlet Allocation (LDA) and Scikit-learn.
- **Named Entity Recognition (NER)**: Extracts and visualizes key people, organizations, and locations mentioned in the news using SpaCy.
- **Visual Analytics**:
    - Sentiment distribution pie charts and heatmaps.
    - Category-wise analytics.
    - Word frequency analysis.
    - Topic distribution plots.

## Tech Stack

- **Backend**: Django (Python)
- **Data Processing**: Pandas, NumPy
- **NLP**: SpaCy, TextBlob, Scikit-learn
- **Web Scraping**: Selenium, BeautifulSoup4
- **Visualization**: Matplotlib, Seaborn

## Setup Instructions

### Prerequisites

- Python 3.8+
- Google Chrome (for Selenium WebDriver)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd news_dashboard
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download SpaCy Model:**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Apply Migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Run the Server:**
   ```bash
   python manage.py runserver
   ```

   Access the dashboard at `http://127.0.0.1:8000/`.

## Usage

1. **Dashboard Home**: View the latest analytics and charts.
2. **Scraping**: The scraping function is integrated into the analytics view (or triggered via specific endpoints/management commands as configured).
3. **Interactive Plots**: Charts are generated dynamically based on the latest scraped data.

## Project Structure

- `news_dashboard/`: Main Django project configuration.
- `analytics/`: Application handling data scraping, processing, and visualization.
    - `utils.py`: Core logic for scraping, sentiment analysis, and plot generation.
    - `views.py`: Controls the flow of data to templates.
- `templates/`: HTML templates for the dashboard.
