import sys
from pathlib import Path
from typing import Callable, Optional, Dict, Any

# Ensure module directory is in path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain


def _extract_text(msg: Any) -> str:
    """Helper to safely extract string text from AIMessage, dict, or string."""
    if hasattr(msg, "content"):
        content = msg.content
    elif isinstance(msg, dict) and "content" in msg:
        content = msg["content"]
    else:
        content = str(msg)

    if isinstance(content, list):
        parts = []
        for p in content:
            if isinstance(p, dict) and "text" in p:
                parts.append(p["text"])
            elif isinstance(p, str):
                parts.append(p)
            else:
                parts.append(str(p))
        return "\n".join(parts)
    return str(content) if content is not None else ""


def run_search_step(topic: str) -> str:
    """Step 1: Search Agent searches the web for reliable information."""
    search_agent = build_search_agent()
    result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    return _extract_text(result["messages"][-1])


def run_reader_step(topic: str, search_results: str) -> str:
    """Step 2: Reader Agent scrapes top URL for in-depth content."""
    reader_agent = build_reader_agent()
    search_excerpt = search_results[:1200] if search_results else ""
    result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{search_excerpt}"
        )]
    })
    return _extract_text(result["messages"][-1])


def run_writer_step(topic: str, search_results: str, scraped_content: str) -> str:
    """Step 3: Writer Chain synthesizes findings into a full report."""
    research_combined = (
        f"SEARCH RESULTS:\n{search_results}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{scraped_content}"
    )
    return writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })


def run_critic_step(report: str) -> str:
    """Step 4: Critic Chain reviews and evaluates the report."""
    return critic_chain.invoke({
        "report": report
    })


def run_research_pipeline(
    topic: str,
    step_callback: Optional[Callable[[str, str, Any], None]] = None
) -> Dict[str, Any]:
    """
    Executes the full 4-agent research pipeline end-to-end.

    Parameters:
        topic: The research topic string.
        step_callback: Optional callback(step_name, status, data)
                       step_name: 'search', 'reader', 'writer', 'critic'
                       status: 'running', 'done'
    """
    state: Dict[str, Any] = {"topic": topic}

    # Step 1: Search Agent
    print("\n" + "=" * 50)
    print("Step 1 - Search Agent is working...")
    print("=" * 50)
    if step_callback:
        step_callback("search", "running", None)
    search_res = run_search_step(topic)
    state["search"] = search_res
    state["search_results"] = search_res
    print("\nSearch Result:\n", search_res)
    if step_callback:
        step_callback("search", "done", search_res)

    # Step 2: Reader Agent
    print("\n" + "=" * 50)
    print("Step 2 - Reader Agent is scraping top resources...")
    print("=" * 50)
    if step_callback:
        step_callback("reader", "running", None)
    scraped_res = run_reader_step(topic, search_res)
    state["reader"] = scraped_res
    state["scraped_content"] = scraped_res
    print("\nScraped Content:\n", scraped_res)
    if step_callback:
        step_callback("reader", "done", scraped_res)

    # Step 3: Writer Chain
    print("\n" + "=" * 50)
    print("Step 3 - Writer Chain is drafting the report...")
    print("=" * 50)
    if step_callback:
        step_callback("writer", "running", None)
    report_res = run_writer_step(topic, search_res, scraped_res)
    state["writer"] = report_res
    state["report"] = report_res
    print("\nFinal Report:\n", report_res)
    if step_callback:
        step_callback("writer", "done", report_res)

    # Step 4: Critic Chain
    print("\n" + "=" * 50)
    print("Step 4 - Critic Chain is reviewing the report...")
    print("=" * 50)
    if step_callback:
        step_callback("critic", "running", None)
    critic_res = run_critic_step(report_res)
    state["critic"] = critic_res
    state["feedback"] = critic_res
    print("\nCritic Feedback:\n", critic_res)
    if step_callback:
        step_callback("critic", "done", critic_res)

    return state


if __name__ == "__main__":
    topic_input = input("\nEnter a research topic: ")
    if topic_input.strip():
        run_research_pipeline(topic_input.strip())
