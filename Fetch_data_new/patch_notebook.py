
import json
import os

notebook_path = r"c:\Users\abhis\OneDrive\Desktop\abhigit\Toeho-AI\Fetch_data_new\Fetch_data_from_news_website_Sentiment.ipynb"

new_code = [
    "# Sentiment Analysis Functions with Chunking\n",
    "def chunk_text(text, chunk_size=500, overlap=50):\n",
    "    \"\"\"\n",
    "    Splits text into chunks of `chunk_size` characters with `overlap`.\n",
    "    \"\"\"\n",
    "    if not text:\n",
    "        return []\n",
    "    chunks = []\n",
    "    start = 0\n",
    "    text_len = len(text)\n",
    "    \n",
    "    while start < text_len:\n",
    "        end = min(start + chunk_size, text_len)\n",
    "        chunks.append(text[start:end])\n",
    "        if end == text_len:\n",
    "            break\n",
    "        start += (chunk_size - overlap)\n",
    "    return chunks\n",
    "\n",
    "def analyze_sentiment_with_chunks(text):\n",
    "    \"\"\"\n",
    "    Analyzes sentiment by averaging the polarity of text chunks.\n",
    "    \"\"\"\n",
    "    if not text:\n",
    "        return 0.0, 'Neutral'\n",
    "    \n",
    "    chunks = chunk_text(text)\n",
    "    if not chunks:\n",
    "        return 0.0, 'Neutral'\n",
    "        \n",
    "    chunk_polarities = []\n",
    "    for chunk in chunks:\n",
    "        blob = TextBlob(chunk)\n",
    "        chunk_polarities.append(blob.sentiment.polarity)\n",
    "    \n",
    "    # Average polarity\n",
    "    avg_polarity = sum(chunk_polarities) / len(chunk_polarities)\n",
    "    \n",
    "    if avg_polarity > 0.05:\n",
    "        return avg_polarity, 'Positive'\n",
    "    elif avg_polarity < -0.05:\n",
    "        return avg_polarity, 'Negative'\n",
    "    else:\n",
    "        return avg_polarity, 'Neutral'\n",
    "\n",
    "# Apply Sentiment Analysis\n",
    "df = pd.DataFrame(articles_data)\n",
    "if not df.empty:\n",
    "    df[['sentiment_score', 'sentiment_label']] = df['content'].apply(\n",
    "        lambda x: pd.Series(analyze_sentiment_with_chunks(x))\n",
    "    )\n",
    "\n",
    "    print(\"Processed Data (with Chunking):\")\n",
    "    print(df[['headline', 'category', 'date', 'sentiment_label', 'sentiment_score']].head())\n",
    "else:\n",
    "    print(\"No articles to process.\")"
]

try:
    with open(notebook_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Find the cell to replace
    # We look for the cell containing "def get_sentiment(text):"
    replaced = False
    for cell in data['cells']:
        if cell['cell_type'] == 'code':
            source = cell.get('source', [])
            # Join source to check content easily
            source_text = "".join(source)
            if "def get_sentiment(text):" in source_text:
                cell['source'] = new_code
                replaced = True
                print("Found and replaced the sentiment analysis cell.")
                break
    
    if replaced:
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print("Notebook updated successfully.")
    else:
        print("Target cell not found.")

except Exception as e:
    print(f"Error: {e}")
