from django.shortcuts import render
from .utils import scrape_and_process, generate_plots

def home(request):
    return render(request, 'home.html')

def dashboard(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        if not url:
            return render(request, 'home.html', {'error': 'Please enter a URL'})
        
        # Scrape and Process
        try:
            df = scrape_and_process(url)
            
            if df.empty:
                return render(request, 'home.html', {'error': 'No articles found or scraping failed. Try another URL.'})
            
            # Generate Plots
            plots, df = generate_plots(df)
            
            # Convert DF to list of dicts for template
            articles = df[['headline', 'url', 'sentiment_label', 'sentiment_score', 'Mapped_Category']].to_dict('records')
            
            context = {
                'url': url,
                'articles': articles,
                'plots': plots,
                'total_articles': len(df)
            }
            return render(request, 'dashboard.html', context)
            
        except Exception as e:
            return render(request, 'home.html', {'error': f"An error occurred: {str(e)}"})
            
    return render(request, 'home.html')
