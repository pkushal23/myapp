import google.generativeai as genai
from django.conf import settings # To access GOOGLE_API_KEY from settings

# Configure Google Gemini API (ensure settings.GOOGLE_API_KEY is loaded)
if hasattr(settings, 'GOOGLE_API_KEY') and settings.GOOGLE_API_KEY:
    genai.configure(api_key=settings.GOOGLE_API_KEY)
else:
    print("Warning: GOOGLE_API_KEY not found in settings. Gemini API calls will fail.")

def summarize_text_gemini(text, max_tokens=150):
    """Summarizes the given text using Google Gemini."""
    if not text:
        return ""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash') # Or 'gemini-1.5-flash', 'gemini-1.5-pro'
        # Prompt engineering is crucial here!
        prompt = f"Summarize the following article concisely, focusing on key information, in about {max_tokens} words. Avoid jargon. If the text is empty or irrelevant, return 'No relevant content to summarize.':\n\n{text}"
        response = model.generate_content(prompt)
        if response.candidates:
            summary = response.candidates[0].content.parts[0].text
            return summary.strip()
        return "No summary generated."
    except Exception as e:
        print(f"Error summarizing with Gemini: {e}")
        # You might want to log the error more robustly
        return "Error generating summary."

def generate_newsletter_section_gemini(topic, articles_summaries, max_tokens=300):
    """Generates a newsletter section based on a topic and article summaries."""
    if not articles_summaries:
        return f"No new updates on {topic} for this newsletter period."

    summaries_text = "\n\n".join(articles_summaries)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Generate a concise and engaging newsletter section about the topic: "{topic}".
    Integrate insights from the following article summaries.
    Focus on recent developments and key takeaways.
    Keep it professional but easy to understand.
    Aim for about {max_tokens} words.

    Article Summaries:
    {summaries_text}
    """
    try:
        response = model.generate_content(prompt)
        if response.candidates:
            return response.candidates[0].content.parts[0].text.strip()
        return "Could not generate content for this section."
    except Exception as e:
        print(f"Error generating newsletter section with Gemini: {e}")
        return "Error generating newsletter content."