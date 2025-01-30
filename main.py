import os
import uuid
import asyncio

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt.chat_agent_executor import AgentState

from langchain_openai import AzureChatOpenAI
from langchain_core.messages import AIMessage, ToolMessage, AIMessageChunk, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.utilities import BingSearchAPIWrapper
from langchain_core.tools import tool
from langchain.globals import set_verbose
from langchain.prompts import MessagesPlaceholder

from typing import Annotated
from feedParser import fetch_article_content, fetch_rss_feed, write_to_file, extract_message_content
from enum import Enum
from gpt_researcher import GPTResearcher
from slugify import slugify


class ArticleState(AgentState):
    content: str

class ReportType(Enum):
    research_report = "research_report"
    resource_report = "resource_report"
    outline_report = "outline_report"
    subtopic_report = "subtopic_report"

set_verbose(True)

@tool
def search_on_bing(terms: Annotated[str, "The terms to search for"]) -> str:
    """Searches Bing for the input terms and returns the top 5 results."""
    try:
        results = BingSearchAPIWrapper(k=5).run(terms)
        print(f"Bing Search Results for '{terms}': {results[:200]}...")
        return results
    except Exception as e:
        print(f"Error in Bing search: {e}")
        return f"Search failed: {str(e)}"

@tool
def research_assistant(
        subject: Annotated[str, "The subject to research"],
        report_type: Annotated[ReportType, "The type of report to generate"]):
    """Ask the assistant to perform searches on a subject, and generate a search report as output."""
    try:
        researcher = GPTResearcher(query=subject, report_type=report_type.name)
        asyncio.run(researcher.conduct_research())
        report =  asyncio.run(researcher.write_report())
        return report
    except Exception as e:
        print(f"Error in ResearchAssistant search: {e}")
        return f"Research assistant failed: {str(e)}"

tools = [search_on_bing, research_assistant]
checkpointer = MemorySaver()
prompt = ChatPromptTemplate.from_messages([
    ("system", open("prompt.txt", "r").read()),
    MessagesPlaceholder(variable_name="messages", optional=True)
])

llm = AzureChatOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    request_timeout=None,
    timeout=None,
    max_retries=3
)
tool_llm = llm.bind_tools(tools)

url = input("Enter RSS feed URL or article URL:")
if "rss" in url.lower() or "feed" in url.lower():
    articles = fetch_rss_feed(url)
else:
    article_content = fetch_article_content(url)
    title_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Generate a concise and informative title for the following article content." +
            "Your answer should only be the title, no other text. See article content below:\n\n{content}"
        )
    ])
    chain = title_prompt | llm
    try:
        response = chain.invoke({"content": article_content })
        if response:
            article_title = response.content
        else:
            article_title = "Untitled Article"
    except Exception as e:
        print(f"Error generating title: {e}")
        article_title = "Untitled Article"

    articles = [{"title": article_title, "content": article_content}]

config = {
    "configurable": {
        "thread_id": str(uuid.uuid4()),
        "timeout": None,
        "recursion_limit": 10
    }
}

agent_executor = create_react_agent(tool_llm, tools, state_modifier=prompt, state_schema=ArticleState, checkpointer=checkpointer, debug=True)

for article in articles:
    ai_messages = []
    state = {
        "messages": [HumanMessage(content=article["content"])]
    }
    
    for s in agent_executor.stream(state, config, stream_mode="values"):
        if s["messages"]:
            message = s["messages"][-1]
            if isinstance(message, AIMessage):
                ai_messages.append(f"## AI Message\n\n{extract_message_content(message.content)}\n")
            elif isinstance(message, ToolMessage) and message.status == "success" and message.content:
                ai_messages.append(f"## Tool '{message.name}' Message\n\n{message.content}\n")

    if ai_messages:
        filename = slugify(article["title"])
        write_to_file([x for x in ai_messages if x], f"results\\{filename}_{config["configurable"]["thread_id"][:6]}.md")