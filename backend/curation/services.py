import os
import requests
from datetime import datetime, timedelta
from django.conf import settings
from .models import Article, Interest



NEWS_API_BASE_URL = "https://newsapi.org/v2/everything"

def fetch_articles_from_newsapi(keywords, from_date=None, to_date=None, language='en', page_size=100):
    """
    Fetches articles from NewsAPI.org for each keyword individually.
    :return: List of unique article dictionaries.
    """
    if not settings.NEWS_API_KEY:
        print("❌ NEWS_API_KEY not found in settings. Please set it in your .env file.")
        return []

    # Clean keywords
    keywords = [kw.strip() for kw in keywords if kw.strip()]
    if not keywords:
        print("❌ No valid keywords provided.")
        return []

    from_date = (datetime.now() - timedelta(days=7)).isoformat()
    to_date = datetime.now().isoformat()

    all_articles = []
    seen_urls = set()  # To prevent duplicates

    for keyword in keywords:
        quoted_keyword = f'"{keyword}"' if ' ' in keyword else keyword
        params = {
            'q': quoted_keyword,
            'from': from_date,
            'to': to_date,
            'language': language,
            'sortBy': 'relevancy',
            'pageSize': min(page_size, 100),
            'apiKey': settings.NEWS_API_KEY,
        }

        try:
            response = requests.get(NEWS_API_BASE_URL, params=params)
            print(f"📤 Request for '{keyword}' → {response.url}")
            response.raise_for_status()

            data = response.json()
            if data.get('status') == 'ok':
                articles = data.get('articles', [])
                print(f"✅ Found {len(articles)} articles for keyword: {keyword}")
                for article in articles:
                    url = article.get('url')
                    if url and url not in seen_urls:
                        all_articles.append(article)
                        seen_urls.add(url)
            else:
                print(f"⚠️ NewsAPI error for keyword '{keyword}': {data.get('message', 'Unknown error')}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Request error for keyword '{keyword}': {e}")
        except ValueError as e:
            print(f"❌ JSON error for keyword '{keyword}': {e}")

    print(f"🔄 Total unique articles fetched: {len(all_articles)}")
    return all_articles



def save_articles_to_db(articles_data, interests_map=None):
    from .models import Article, Interest
    from datetime import datetime

    if interests_map is None:
        interests_map = {interest.name.lower(): interest for interest in Interest.objects.all()}

    saved_count = 0

    for article_data in articles_data:
        url = article_data.get('url')
        if not url or Article.objects.filter(url=url).exists():
            continue

        try:
            published_at_str = article_data.get('publishedAt')
            if not published_at_str:
                continue

            try:
                published_date = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
            except ValueError:
                print(f"Could not parse date: {published_at_str}")
                continue

            article = Article(
                title=article_data.get('title', 'No Title'),
                url=url,
                source=article_data.get('source', {}).get('name', 'Unknown Source'),
                published_date=published_date,
                summary=article_data.get('description', ''),
                full_text=article_data.get('content', '')
            )
            article.save()

            # Match interests
            article_text = (article.title + " " + (article.summary or "") + " " + (article.full_text or "")).lower()
            article_topics = [
                interest_obj
                for interest_name, interest_obj in interests_map.items()
                if interest_name in article_text
            ]
            article.topics.set(article_topics)

            # ✅ DEFERRED IMPORT to avoid circular import issue
            from .tasks import summarize_article_task
            summarize_article_task.delay(article.id)

            saved_count += 1
            print(f"Saved new article: {article.title} and queued for summarization.")

        except Exception as e:
            print(f"Error saving article {url}: {e}")
            continue

    print(f"Finished saving articles. Total new articles saved: {saved_count}")
    return saved_count


