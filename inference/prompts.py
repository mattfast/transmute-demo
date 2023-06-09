from langchain import LLMChain, OpenAI
from langchain.chains.constitutional_ai.base import ConstitutionalChain
from langchain.chains.constitutional_ai.models import ConstitutionalPrinciple
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

extract_interesting_tidbits = """List only the key parts of the article below that a {profession} would find interesting. Justify and phrase your response appropriately with examples from the article:

Article:
{article}

Output:
"""
gpt4_800_llm = ChatOpenAI(
    model_name="gpt-4",
    max_tokens=800,
)
gpt4_700_llm = ChatOpenAI(
    model_name="gpt-4",
    max_tokens=700,
)
gpt4_500_llm = ChatOpenAI(
    model_name="gpt-4",
    max_tokens=500,
)

tidbits_tmpl = PromptTemplate(
    input_variables=["article", "profession"],
    template=extract_interesting_tidbits,
)
tid_chain = LLMChain(llm=gpt4_800_llm, prompt=tidbits_tmpl, verbose=True)


extract_purpose_prompt = """Output the single most important point made in the article below that a {profession} would enjoy. Be specific to terms used in the article. Just output the point, don't explain it.

Article:
{article}

Output:
"""
purpose_tmpl = PromptTemplate(
    input_variables=["article", "profession"],
    template=extract_purpose_prompt,
)
purpose_chain = LLMChain(llm=gpt4_800_llm, prompt=purpose_tmpl, verbose=True)

group_prompt = """Group the following list of key points made in the article into a list of themes pertaining to the article below. Be specific in your choice of themes. 

Topics:
{points}

Article:
{article}

Output:
"""

group_temp = PromptTemplate(
    input_variables=["points", "article"],
    template=group_prompt,
)
group_chain = LLMChain(llm=gpt4_700_llm, prompt=group_temp, verbose=True)

new_summary_prompt = """Provide a summary of the article that touches primarily
on the following high level topics. Output your response in bullets:

Topics:
{points}

When writing the summary, focus on:
- {prof_purpose}

Be specific to the topics above and be sure to maintain the logical order of the article, but use the following themes to guide your summary response:
{themes}

Article:
{article}

Do not include a conclusion paragraph, just the content from above.

Guidelines for writing bullet points:
- each bullet point should be short. no longer than 15 words.
- do not output more than 4 bullet points

Use the following format:
- bullet 1
- bullet 2
....
- last bullet

Output:
"""
new_tmpl = PromptTemplate(
    input_variables=["article", "points", "prof_purpose", "themes"],
    template=new_summary_prompt,
)
new_sum_chain = LLMChain(llm=gpt4_500_llm, prompt=new_tmpl, verbose=True)


def get_style_critique_chain(persona: str, chain: LLMChain) -> ConstitutionalChain:
    """Get constitutional chain."""
    critique_req = """Identify specific ways the text is not suited by and for a {profession} and how it can be improved. Comment on writing style, tone, and use of vocabulary.
    """
    critique_req_str = critique_req.format(profession=persona)
    change_principle = ConstitutionalPrinciple(
        name="Change Principle",
        critique_request=critique_req_str,
        revision_request="""Rewrite the model's response. In particular, use recommendations from the critiques provided. Output in the same format.
        """,
    )
    constitutional_chain = ConstitutionalChain.from_llm(
        chain=chain,
        constitutional_principles=[change_principle],
        llm=gpt4_500_llm,
        verbose=True,
    )
    return constitutional_chain


extra_info_prompt = """Determine if the first text contains any meaningful extra information than what is already contained in the second text.

If so, output that extra information:

First Text:
{first}

Second Text:
{second}

Output format (JSON):
{{
    "extra_info_needed": NO if the first text does not contain information that is valuable in addition to the second. Only output YES if there is more than one specific piece of info that the first text contains that isn't in the second.
    "extra_info": a sentence containing the extra information. do not use the words "first text" in your response. just provide the additional information.
}}
Output:
"""
extra_info_tmpl = PromptTemplate(
    input_variables=["first", "second"],
    template=extra_info_prompt,
)
extra_info_chain = LLMChain(llm=gpt4_500_llm, prompt=extra_info_tmpl, verbose=True)


synthesis_prompt = """Connect the information from the first to information in the second piece.

You're synthesis can touch on a number of things, including but not limited to:
- how the meaning of the two are different
- how information presented in the first builds upon the second
- how assumptions in the first challenge those in the second
- how assumptions in the first are consistent with those in the second
- be specific to the content of both pieces
- make predictions based on the text of the two
- explain like you would to a {profession}

Be bold and unique. Be bold and adventurous in the connections you make and don't be overly specific about details from the first piece.


First Piece:
{first}

Second Piece:
{second}

Just output the synthesis of the content. Make sure the synthesis sentence is short.
Output:
"""
synth_tmpl = PromptTemplate(
    input_variables=["first", "second", "profession"],
    template=synthesis_prompt,
)
synth_chain = LLMChain(llm=gpt4_500_llm, prompt=synth_tmpl, verbose=True)

synth_combo_prompt = """Synthesize each of the bullet points below into unique ideas, each in the form of a short sentence bullet point. Maintain the information provided in each bullet. Make sure each bullet point outputted is unique and contains the essence of an idea:

Information:
{bullets}


Guidelines for synthesizing:
- be bold with the synthesis you are making from the information above
- make predictions
- draw interesting connections between disparate ideas
- ask questions designed to spur further thought about the connections between ideas
- postulate new ideas

Guidelines for writing bullet points:
- each bullet point should be short. no longer than 12 words
- do not output more than 3 bullet points
- write as a {personality} would speak

Use the following output format:
- bullet 1 
- bullet 2 
...
- last bullet 

Output:
"""
synth_combo_tmpl = PromptTemplate(
    input_variables=["bullets", "personality"],
    template=synth_combo_prompt,
)
synth_combo_chain = LLMChain(llm=gpt4_500_llm, prompt=synth_combo_tmpl, verbose=True)
