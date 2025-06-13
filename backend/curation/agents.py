# backend/curation/agents.py
from langchain.agents import AgentExecutor, create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI # For Gemini
# OR from langchain_openai import OpenAI, ChatOpenAI # For OpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Import your custom tools
from .agent_tools import get_recent_summarized_articles_for_user_interests, get_interest_details
from django.conf import settings
from .models import UserInterest # For getting user's interest names

# Define the LLM (Large Language Model)
# For Google Gemini:
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7, google_api_key=settings.GOOGLE_API_KEY)
# For OpenAI:
# llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, openai_api_key=settings.OPENAI_API_KEY)

# List of tools available to the agent
tools = [
    get_recent_summarized_articles_for_user_interests,
    get_interest_details,
    # You can add the summarize_text_gemini/openai as a tool if the agent needs to summarize on demand,
    # but for this flow, we're assuming articles are pre-summarized.
]

def get_user_interest_names(user_id):
    """Helper to get a list of interest names for a user."""
    try:
        user_interests = UserInterest.objects.filter(user_id=user_id).select_related('interest')
        return [ui.interest.name for ui in user_interests]
    except Exception as e:
        print(f"Error getting interests for user {user_id}: {e}")
        return []

def get_newsletter_generation_agent_executor(user_id):
    """
    Creates and returns an AgentExecutor configured to generate newsletters.
    """
    user_interest_names = get_user_interest_names(user_id)
    if not user_interest_names:
        return None # Or raise an error, or return a basic agent without specific interests

    # The Agent's instruction or persona
    agent_instructions = f"""
    You are an expert AI newsletter generator assistant for a user named '{user_id}'.
    Your goal is to create a concise, informative, and engaging daily newsletter based on the user's selected interests.
    The user is interested in: {', '.join(user_interest_names)}.
    You have access to tools to find recent summarized articles relevant to these interests.

    Follow these steps:
    1. Use the 'get_recent_summarized_articles_for_user_interests' tool to find relevant articles for the user.
    2. If articles are found, categorize them by the user's interests.
    3. For each interest with relevant articles, draft a short, engaging section summarizing the key takeaways from those articles.
    4. If no articles are found for a particular interest, simply state that there are no new updates.
    5. Combine all sections into a single, cohesive newsletter.
    6. Ensure the newsletter is well-formatted and easy to read. Start with a greeting.
    7. Conclude with a polite closing.
    """

    # This is the prompt for the ReAct agent
    # You can build this using PromptTemplate for more control if needed
    base_prompt = PromptTemplate.from_template(
        """Answer the following questions as best you can. You have access to the following tools:
        {tools}

        Use the following format:

        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question

        Begin!

        Question: {input}
        Thought:{agent_scratchpad}
        """
    )

    # Create the ReAct agent
    agent = create_react_agent(llm, tools, base_prompt)

    # Create the AgentExecutor
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

    return agent_executor


# --- Direct Chain for Newsletter Generation (Simpler alternative if agent is too complex initially) ---
def get_newsletter_generation_chain(user_id):
    """
    Creates a simpler LLMChain for newsletter generation without full agent reasoning.
    """
    user_interest_names = get_user_interest_names(user_id)
    if not user_interest_names:
        return None

    # 1. Fetch relevant articles (this step is done outside the LLM call for simplicity)
    # You would call get_recent_summarized_articles_for_user_interests directly here.

    # 2. Define the prompt for the LLM
    prompt = PromptTemplate.from_template(
        """
        Generate a personalized newsletter for the user interested in: {user_interests}.
        Here are recent article summaries relevant to these topics:
        {articles_summaries}

        Combine these summaries into an engaging and concise newsletter.
        Start with a friendly greeting.
        For each interest, provide a brief section with key takeaways.
        If there are no new articles for an interest, state 'No new updates'.
        Conclude with a polite closing.
        """
    )

    # Create a simple chain
    chain = (
        {
            "user_interests": lambda x: ", ".join(x["user_interests"]),
            "articles_summaries": RunnablePassthrough() # This expects pre-fetched summaries
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain