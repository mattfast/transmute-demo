from langchain import LLMChain, OpenAI
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

group_prompt = """Group the following list of key points made in the article into a list of themes pertaining to the article below. Be specific in your choice of themes and tailor your choice to a {profession}. 

Topics:
{points}

Article:
{article}

Output:
"""

group_temp = PromptTemplate(
    input_variables=["points", "article", "profession"],
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
- each bullet point should be short. no longer than 12 words
- do not output more than 4 bullet points
- tailor the style of your response to a {profession} 

Use the following format:
- bullet 1
- bullet 2
....
- last bullet

Output:
"""
new_tmpl = PromptTemplate(
    input_variables=["article", "points", "prof_purpose", "themes", "profession"],
    template=new_summary_prompt,
)
new_sum_chain = LLMChain(llm=gpt4_500_llm, prompt=new_tmpl, verbose=True)


extra_info_prompt = """Determine if the first text contains any meaningful extra information than what is already contained in the second text.

If so, just explain that extra information:

First Text:
{first}

Second Text:
{second}

Output format (JSON):
{{
    "extra_info_needed": NO if the first text does not contain information that is valuable in addition to the second. Only output YES if there is more than one specific piece of info that the first text contains that isn't in the second.
    "extra_info": a sentence explaining the extra information in the first text that is not contained in the second. do not use the words "first text" in your response. just explain the additional information.
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
- tailor the style of your response to a {profession}

Be bold and unique. Be general in the connections you make and don't be overly specific about details from the first piece.


First Piece:
{first}

Second Piece:
{second}

Just output the synthesis. Make sure the synthesis sentence is short.
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
- make predictions whenever possible
- draw interesting connections between disparate ideas
- postulate new ideas

Guidelines for writing bullet points:
- each bullet point should be short. no longer than 12 words
- do not output more than 3 bullet points
- tailor the style of your response to a {profession}

Use the following output format:
- bullet 1 
- bullet 2 
...
- last bullet 

Sources:
- source 1 used in bullet 1
...
- last source used in last bullet

Include sources verbatim from links above

Output:
"""
synth_combo_tmpl = PromptTemplate(
    input_variables=["bullets", "profession"],
    template=synth_combo_prompt,
)
synth_combo_chain = LLMChain(llm=gpt4_500_llm, prompt=synth_combo_tmpl, verbose=True)
