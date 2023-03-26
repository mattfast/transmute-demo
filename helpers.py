import urllib.request
from typing import Any, List

from bs4 import BeautifulSoup
from langchain.text_splitter import TokenTextSplitter


def process_link_to_website_text(link: str) -> str:
    """Get website text from link."""
    req = urllib.request.Request(
        link,
        data=None,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
        },
    )
    page_req = urllib.request.urlopen(req)
    html = page_req.read()
    soup = BeautifulSoup(html, features="html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()  # rip it out

    # get text
    text = soup.body.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = "\n".join(chunk for chunk in chunks if chunk)

    return text


def process_new_link(link: str, persona: str, index: Any) -> List[str]:
    """Control flow for processing new link."""
    link_text = process_link_to_website_text(link)
    text_split = TokenTextSplitter()
    splits = text_split.split_text(link_text)
    news_article = splits[0]


def format_summaries_for_text(summary: str, synthesis: str) -> List[str]:
    """Format summaries for text message."""
    final_formatted_summary = f"""
    What's relevant in the article:
    {summary}
    """

    final_formatted_synthesis = f"""
    Insights:
    {synthesis}
    """

    return [final_formatted_summary, final_formatted_synthesis]
