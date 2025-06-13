# backend/curation/agent_tools.py
from langchain.tools import tool
from .models import Article, UserInterest, Interest
from django.contrib.auth.models import User
from django.db.models import Q
from datetime import datetime, timedelta

# Example of a tool that fetches summarized articles for a user's interests
@tool
def get_recent_summarized_articles_for_user_interests(user_id: int, days_back: int = 7) -> list:
    """
    Fetches recent summarized articles relevant to a specific user's interests from the database.
    Args:
        user_id (int): The ID of the user.
        days_back (int): How many days back to look for articles (default: 7).
    Returns:
        list: A list of dictionaries, each containing 'title', 'summary', and 'url' of relevant articles.
    """
    try:
        user = User.objects.get(id=user_id)
        user_interests = UserInterest.objects.filter(user=user).select_related('interest')
        interest_ids = [ui.interest.id for ui in user_interests]

        if not interest_ids:
            return []

        # Filter articles by interests and time
        cutoff_date = datetime.now() - timedelta(days=days_back)
        articles = Article.objects.filter(
            topics__id__in=interest_ids,
            published_date__gte=cutoff_date,
            summary__isnull=False # Only get articles that have been summarized
        ).distinct().order_by('-published_date')[:10] # Limit for practical purposes

        return [
            {
                "title": article.title,
                "summary": article.summary,
                "url": article.url
            }
            for article in articles
        ]
    except User.DoesNotExist:
        return f"User with ID {user_id} not found."
    except Exception as e:
        return f"Error fetching articles for user {user_id}: {e}"

# Add more tools as needed, e.g., a tool to look up a specific interest's details
@tool
def get_interest_details(interest_name: str) -> str:
    """
    Retrieves the description of a specific interest.
    Args:
        interest_name (str): The name of the interest (e.g., "Artificial Intelligence").
    Returns:
        str: The description of the interest or a "not found" message.
    """
    try:
        interest = Interest.objects.get(name__iexact=interest_name)
        return interest.description or f"No specific description for {interest_name}."
    except Interest.DoesNotExist:
        return f"Interest '{interest_name}' not found."