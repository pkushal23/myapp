# backend/curation/tasks.py
from celery import shared_task
from .services import fetch_articles_from_newsapi, save_articles_to_db
from .models import Interest, Article
from datetime import datetime, timedelta
from .agents import get_newsletter_generation_agent_executor, get_newsletter_generation_chain
from django.contrib.auth.models import User
from .models import Newsletter
from django.db import transaction




# backend/curation/tasks.py (add to existing imports)
from .ai_utils import summarize_text_gemini 

@shared_task(bind=True, max_retries=3, default_retry_delay=60) # Add retry logic for API calls
def summarize_article_task(self, article_id):
    """
    Celery task to summarize a single article using AI.
    """
    try:
        article = Article.objects.get(id=article_id)
        if article.summary:
            print(f"Article {article.id} already summarized. Skipping.")
            return "Already summarized."

        # Prioritize full_text if available, otherwise use existing summary/title
        text_to_summarize = article.full_text or article.summary or article.title

        if not text_to_summarize:
            print(f"No text to summarize for article {article.id}. Skipping.")
            return "No text available."

        # Choose your AI summary function (Gemini or OpenAI)
        summary = summarize_text_gemini(text_to_summarize, max_tokens=200)

        if summary and summary != "Error generating summary.": # Basic check for valid summary
            article.summary = summary
            article.save(update_fields=['summary'])
            print(f"Successfully summarized article {article.id}: {article.title}")
            return "Summarized successfully."
        else:
            print(f"Failed to summarize article {article.id}.")
            # If AI returns error, you might want to log it and retry
            self.retry(exc=ValueError("AI summary failed."), countdown=self.request.retries * 300) # Exponential backoff
    except Article.DoesNotExist:
        print(f"Article with ID {article_id} not found.")
        return "Article not found."
    except Exception as e:
        print(f"Unhandled error summarizing article {article_id}: {e}")
        self.retry(exc=e, countdown=self.request.retries * 300) # Retry on other errors


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
    

@shared_task
def generate_user_newsletter_task(user_id):
    """
    Celery task to generate a personalized newsletter for a given user.
    """
    try:
        user = User.objects.get(id=user_id)
        print(f"Generating newsletter for user: {user.username}")

        # --- Option 1: Use the LangChain Agent (more complex but powerful) ---
        # agent_executor = get_newsletter_generation_agent_executor(user_id)
        # if agent_executor:
        #     # The agent will use its tools to find articles and generate
        #     # You might need to refine the input/output of the agent here
        #     agent_input = f"Generate a daily newsletter for me based on my interests: {', '.join(get_user_interest_names(user_id))}"
        #     ai_generated_content = agent_executor.invoke({"input": agent_input})['output']
        # else:
        #     ai_generated_content = "No interests found for user. Cannot generate personalized newsletter."

        # --- Option 2: Use the simpler LangChain Chain (recommended to start with) ---
        # First, gather articles relevant to the user's current interests
        from .agent_tools import get_recent_summarized_articles_for_user_interests # Import tool here
        relevant_articles_data = get_recent_summarized_articles_for_user_interests.invoke({
    "user_id": user.id,
    "days_back": 7
})


        if not relevant_articles_data:
            ai_generated_content = f"Hello {user.username},\n\nThere are no new articles relevant to your interests in the past 7 days. Please check back later or update your interests!"
            # You might want to skip saving a newsletter if no content
        else:
            articles_summaries = [f"Title: {a['title']}\nSummary: {a['summary']}\nURL: {a['url']}" for a in relevant_articles_data]
            user_interest_names = [ui.interest.name for ui in user.user_interests.all()] # Get actual names

            newsletter_chain = get_newsletter_generation_chain(user.id)
            if newsletter_chain:
                ai_generated_content = newsletter_chain.invoke({
                    "user_interests": user_interest_names,
                    "articles_summaries": "\n\n---\n\n".join(articles_summaries)
                })
            else:
                ai_generated_content = "Failed to initialize newsletter generation chain."


        if ai_generated_content:
            with transaction.atomic():
                newsletter = Newsletter.objects.create(
                    user=user,
                    content=ai_generated_content
                )
                # Link the articles that were actually used
                for article_data in relevant_articles_data:
                    try:
                        article_obj = Article.objects.get(url=article_data['url'])
                        newsletter.articles_included.add(article_obj)
                    except Article.DoesNotExist:
                        pass # Should not happen if fetched from DB

                print(f"Successfully generated and saved newsletter for {user.username}.")
        else:
            print(f"No content generated for newsletter for {user.username}.")

    except User.DoesNotExist:
        print(f"User with ID {user_id} not found for newsletter generation.")
    except Exception as e:
        print(f"Error generating newsletter for user {user_id}: {e}")
        # Log the full traceback for debugging

@shared_task
def generate_all_newsletters_task():
    """
    Celery task to trigger newsletter generation for all active users.
    This will be scheduled by Celery Beat.
    """
    print("Starting generate_all_newsletters_task...")
    users = User.objects.filter(is_active=True) # Or filter users with interests
    for user in users:
        # You can add logic here to only generate if user has interests
        if user.user_interests.exists():
            generate_user_newsletter_task.delay(user.id) # Queue each user's newsletter generation
        else:
            print(f"User {user.username} has no interests. Skipping newsletter generation.")
    print("Queued newsletter generation for active users.")