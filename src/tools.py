"""Tool definitions for the agent.

Two tools, each with a name, a description (shown to the LLM), and a callable:
- web_search: live web search via DuckDuckGo (no API key needed)
- summarize: condenses long text into bullet points using the chat model
"""
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

_search_tool = DuckDuckGoSearchRun()


def web_search(query: str) -> str:
    """Search the web and return the top results as text."""
    try:
        result = _search_tool.invoke(query)
        result = (result or "").strip()
        if not result:
            return "No results found for this query."
        return result[:4000]
    except Exception as exc:  # network hiccups become observations, not crashes
        return f"Search failed with error: {exc}. Try a different query."


_summarize_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Summarize the following text in 5-8 concise bullet points. "
            "Keep key facts, numbers, names, and dates. Do not add information "
            "that is not in the text.",
        ),
        ("human", "{text}"),
    ]
)


def build_tools(llm: ChatOpenAI) -> dict:
    """Return {name: {"description": ..., "run": callable}} bound to the given LLM."""

    def summarize(text: str) -> str:
        messages = _summarize_prompt.format_messages(text=text[:12000])
        return llm.invoke(messages).content

    return {
        "web_search": {
            "description": (
                "Search the web for current information, facts, comparisons, or news. "
                "Input must be a single search query string."
            ),
            "run": web_search,
        },
        "summarize": {
            "description": (
                "Condense a long piece of text into 5-8 bullet points. "
                "Input must be the full text to summarize."
            ),
            "run": summarize,
        },
    }
