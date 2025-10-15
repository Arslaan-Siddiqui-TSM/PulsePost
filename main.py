"""main.py - CLI runner for LinkedIn Auto MVP"""


import os
import json
import logging
from rich import print
from rich.prompt import Prompt
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


from tools.search_tool import get_trending_topics
from tools.fetch_tool import fetch_article_content
from tools.post_gen_tool import generate_linkedin_post
# from tools.linkedin_tool import post_to_linkedin


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def save_json(filepath, payload):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def main():
    print("[bold green]LinkedIn Auto MVP[/bold green]\n")

    query = os.getenv("DEFAULT_SEARCH_QUERY", "latest tech news")
    print(f"Searching for trending topics ([yellow]{query}[/yellow])...\n")

    topics = get_trending_topics(query=query, web_limit=3, reddit_limit=2)
    if not topics:
        print("[red]No topics found.[/red]")
        return

    save_json(os.path.join(DATA_DIR, "trending_topics.json"), topics)

    for i, t in enumerate(topics, start=1):
        print(f"{i}. [bold]{t['title']}[/bold] — [cyan]{t['source']}[/cyan]")

    choice = Prompt.ask("Select topic", choices=[str(i) for i in range(1, len(topics) + 1)])
    selected = topics[int(choice) - 1]

    print(f"\nFetching content for: [bold]{selected['title']}[/bold]\n")
    content = fetch_article_content(selected["url"])
    save_json(os.path.join(DATA_DIR, "extracted_content.json"), content)

    article_text = content.get("text") or content.get("title") 

    print("Generating LinkedIn post...\n")
    post_text = generate_linkedin_post(article_text=article_text, prompt_path="prompts/post_prompt.txt")    # type: ignore
    print("\n[bold green]--- POST PREVIEW ---[/bold green]\n")
    print(post_text)
    print("\n--- End ---\n")

    # if Prompt.ask("Publish to LinkedIn?", choices=["y", "n"], default="n") == "y":
    #     resp = post_to_linkedin(post_text, publish=True, metadata={"topic": selected})
    #     print(resp)
    # else:
    #     post_to_linkedin(post_text, publish=False, metadata={"topic": selected})
    #     print("Saved locally. Not posted.")


if __name__ == "__main__":
    main()