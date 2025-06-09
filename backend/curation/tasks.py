# backend/curation/tasks.py
from celery import shared_task
from .services import fetch_articles_from_newsapi, save_articles_to_db
from .models import Interest
from datetime import datetime, timedelta

@shared_task
def fetch_and_save_articles_task():
    """
    Celery task to fetch articles from NewsAPI and save them to the database.
    This task runs periodically.
    """
    print("Starting fetch_and_save_articles_task...")

    # Fetch all existing interests to use as keywords
    all_interests = Interest.objects.all()
    if not all_interests.exists():
        print("No interests defined in the database. Skipping article fetch.")
        return 0

    # Get unique interest names to use as keywords for the API
    keywords = list(set([interest.name for interest in all_interests]))

    # Create a map for efficient linking later
    interests_map = {interest.name.lower(): interest for interest in all_interests}

    # Fetch articles from the last 24 hours
    # You can adjust this window based on your needs and API limits
    from_date = datetime.now() - timedelta(days=1)
    to_date = datetime.now()

    fetched_articles_data = fetch_articles_from_newsapi(
        keywords=keywords,
        from_date=from_date,
        to_date=to_date,
        page_size=100 # Max for NewsAPI free tier
    )

    if fetched_articles_data:
        saved_count = save_articles_to_db(fetched_articles_data, interests_map)
        print(f"fetch_and_save_articles_task completed. Saved {saved_count} new articles.")
        return saved_count
    else:
        print("No articles fetched or an error occurred.")
        return 0