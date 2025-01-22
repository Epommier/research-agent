import getpass
import os
import uuid
import asyncio

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt.chat_agent_executor import AgentState

from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.utilities import BingSearchAPIWrapper
from langchain_core.tools import tool
from langchain.globals import set_verbose
from langchain.prompts import MessagesPlaceholder

from typing import Annotated
from feedParser import fetch_rss_feed, write_to_file, extract_message_content
from enum import Enum

from gpt_researcher import GPTResearcher

from slugify import slugify

# if not os.environ.get("AZURE_OPENAI_API_KEY"):
#     os.environ["AZURE_OPENAI_API_KEY"] = getpass.getpass("Enter API key for Azure: ")

class ArticleState(AgentState):
    content: str

class ReportType(Enum):
    research_report = "research_report"
    resource_report = "resource_report"
    outline_report = "outline_report"
    custom_report = "custom_report"
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
        return f"Search failed: {str(e)}"

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
).bind_tools(tools)

config = {"configurable": {"thread_id": str(uuid.uuid4())}}
graph = create_react_agent(llm, tools, state_modifier=prompt, state_schema=ArticleState, checkpointer=checkpointer, debug=True)

articles = fetch_rss_feed("http://www.financemagnates.com/cryptocurrency/feed/")

for article in articles:
    ai_messages = []
    for s in graph.stream({"messages": [], "content": article["content"]}, config, stream_mode="values"):
        if len(s["messages"]) == 0:
            continue

        message = s["messages"][-1]
        if isinstance(message, AIMessage):
            ai_messages.append(extract_message_content(message.pretty_repr()))
        else:
            ai_messages.append(extract_message_content(message))

        # if isinstance(message, tuple):
        #     print(message)
        # else:
        #     message.pretty_print()
    
    filename = slugify(article["title"])
    write_to_file(ai_messages, f"results\\{filename}_{config["configurable"]["thread_id"][:6]}.md")

# SEQUENTIAL CHAINS RUN
# analyze_chain = (PromptTemplate.from_template(open('prompt.txt', 'r').read()) | llm)
# market_impact_chain = (PromptTemplate(input_variables=['summary'], template='Analyze the potential market impact of the following summary :\n{summary}') | llm)
# composed_chain = (
#     {"summary": agent}
#     | StrOutputParser()
#     | RunnablePassthrough()
#     | {"analysis": market_impact_chain}
#     | StrOutputParser()
# )
# for article in fetch_rss_feed('http://www.financemagnates.com/cryptocurrency/feed/'):
#     print(composed_chain.invoke({"content": article['content']}))