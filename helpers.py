import urllib.request
import pinecone
from typing import List, Dict, Tuple

from bs4 import BeautifulSoup
from langchain.text_splitter import TokenTextSplitter
from langchain.docstore.document import Document
from db.embeddings import find_docs, insert_docs
from inference.process import (
    generate_initial_bullets,
    separate_bullet_output,
    generate_extra_info_bullets,
    generate_synthesis_bullets
)


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


def process_new_link(link: str, persona: str, index: pinecone.Index) -> Tuple[str, str]:
    """Control flow for processing new link."""
    link_text = process_link_to_website_text(link)
    text_split = TokenTextSplitter()
    splits = text_split.split_text(link_text)
    news_article = splits[0]

    bullet_output = generate_initial_bullets(news_article, persona)
    print(f"Generated bullets.")
    initial_bullets = separate_bullet_output(bullet_output)
    metadatas = [{"link": link} for _ in range(len(initial_bullets))]
    print(f"Separated bullets.")

    fully_relevant_texts = find_docs(index, bullet_output, k=3)
    print("Found Docs.")

    bullets_to_synthesize = []
    docs_to_include_for_bullets = []

    # Create doc dictionary for accessing Documents by content
    doc_dict = {}
    for text in fully_relevant_texts:
        doc_dict[text.page_content] = text

    # Data structures for synthesizing bullets and relevant texts
    for bullet in initial_bullets:
        bullets_to_synthesize.append(bullet)
        docs_to_include_for_bullets.append(fully_relevant_texts)
    relation_dict = create_relation_dict(
        bullets_to_synthesize, docs_to_include_for_bullets
    )

    extra_info_bullets = generate_extra_info_bullets(
        bullets_to_synthesize, docs_to_include_for_bullets
    )
    print("Generated extra info.")

    synthesis_bullets = generate_synthesis_bullets(
        relation_dict, doc_dict
    )
    print("Generated Synthesis.")

    if len(extra_info_bullets) == 0:
        formatted_learned = ""
    else:
        formatted_learned = "\n".join(["- " + bullet for bullet in extra_info_bullets])

    if len(synthesis_bullets) == 0:
        format_synth = ""
    else:
        format_synth = "\n".join(synthesis_bullets)

    insert_docs(index, extra_info_bullets, metadatas)
    print("Finished Insertion.")

    return formatted_learned, format_synth


def create_relation_dict(
    bullets_to_synthesize: List[str],
    docs_to_include_for_bullets: List[List[Document]]
) -> Dict:
    """Create relation dict between docs and bullets."""
    relation_dict: Dict = {}
    for i, text in enumerate(bullets_to_synthesize):
        for doc in docs_to_include_for_bullets[i]:
            pc = doc.page_content
            if pc not in relation_dict:
                relation_dict[pc] = [text]
            else:
                val = relation_dict[pc]
                val.append(text)
                relation_dict[pc] = val
    return relation_dict


def format_summaries_for_text(summary: str, synthesis: str) -> str:
    """Format summaries for text message."""
    if summary == "":
        final_formatted_summary = "Looks like there's no new information in this article!"
    else:
        final_formatted_summary = \
    f"""
    What's new in the article:
    {summary}
    """

    if synthesis == "":
        final_formatted_synthesis = "There aren't any connections to previous articles you've sent!"
    else:
        final_formatted_synthesis = \
    f"""
    Insights to past links:
    {synthesis}
    """

    final_resp = f"""
    {final_formatted_summary}
    
    {final_formatted_synthesis}
    
    Send us another link to summarize and gain insights from!
    """

    return final_resp
