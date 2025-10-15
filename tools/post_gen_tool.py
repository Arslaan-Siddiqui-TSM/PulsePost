"""post_gen_tool.py


Generate a LinkedIn-style post using Gemini (Google Generative AI)
via LangChain's Google chat wrapper. The function reads the prompt
template from prompts/post_prompt.txt and fills {article_text}.
"""


from typing import Optional
import os
import logging
from dotenv import load_dotenv
load_dotenv()


from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


logger = logging.getLogger(__name__)

def _load_prompt_template(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
    

def _init_llm():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError("GOOGLE_API_KEY is not set in environment")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
    return llm


def generate_linkedin_post(article_text: str, prompt_path: str = "../prompts/post_prompt.txt") -> str:
    """Return generated post text (string)."""
    if not article_text:
        raise ValueError("article_text must not be empty")

    template = _load_prompt_template(prompt_path)
    llm = _init_llm()

    prompt = PromptTemplate(template=template, input_variables=["article_text"])
    chain = prompt | llm | StrOutputParser()
    out = chain.invoke({"article_text": article_text})

    return str(out).strip()


if __name__ == "__main__":
    
    with open("../data/sample_article_text.txt", "r") as f:
        sample_text = f.read()
    print(generate_linkedin_post(sample_text))