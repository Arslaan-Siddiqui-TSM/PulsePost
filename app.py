"""streamlit_app.py


Streamlit frontend to test the LinkedIn automation MVP.
It allows you to:
- Search for trending topics
- Select one
- Fetch and display article content
- Generate a LinkedIn-style post
- Preview or publish to LinkedIn
"""


import os
import json
import streamlit as st
from dotenv import load_dotenv


from tools.search_tool import get_trending_topics
from tools.fetch_tool import fetch_article_content
from tools.post_gen_tool import generate_linkedin_post
from tools.linkedin_tool import post_to_linkedin

load_dotenv()

st.set_page_config(page_title="LinkedIn Auto MVP", layout="wide")
st.title("🤖 LinkedIn Auto MVP")

if not os.getenv("GOOGLE_API_KEY"):
    st.error("❌ Missing GOOGLE_API_KEY environment variable.")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)


def save_json(filepath, payload):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


# --- Step 1: Search Topics ---
st.sidebar.header("🔍 Step 1: Fetch Topics")
default_query = os.getenv("DEFAULT_SEARCH_QUERY", "latest tech news")
query = st.sidebar.text_input("Search query", default_query)
fetch_btn = st.sidebar.button("Get Trending Topics")

if fetch_btn:
    with st.spinner("Fetching trending topics..."):
        topics = get_trending_topics(query=query, web_limit=5, reddit_limit=5)
    if not topics:
        st.error("No topics found. Check your keys or connection.")
    else:
        st.session_state["topics"] = topics
        save_json(os.path.join(DATA_DIR, "trending_topics.json"), topics)

# --- Step 2: Display Topics ---
topics = st.session_state.get("topics", [])
if topics:
    st.subheader("📈 Trending Topics")
    for i, t in enumerate(topics, start=1):
        st.write(f"**{i}. {t['title']}** — *{t['source']}* ")

    idx = st.number_input("Select topic number", min_value=1, max_value=len(topics), value=1)
    selected = topics[idx - 1]

    if st.button("Fetch Content"):
        with st.spinner("Fetching content..."):
            content = fetch_article_content(selected["url"])
        save_json(os.path.join(DATA_DIR, "extracted_content.json"), content)
        st.session_state["content"] = content
        st.success("Article content fetched successfully!")

# --- Step 3: Generate LinkedIn Post ---
content = st.session_state.get("content")

if content:
    st.subheader("📰 Extracted Article Preview")
    st.write(f"### {content['title']}")
    st.text_area("Article Text (editable)", content["text"][:2000], key="article_text", height=600)

    if st.button("Generate LinkedIn Post"):
        with st.spinner("Generating post with Gemini..."):
            try:
                post_text = generate_linkedin_post(st.session_state["article_text"], prompt_path="prompts/post_prompt.txt")
            except Exception as e:
                st.error(f"⚠️ Error generating post: {e}")
                post_text = None

        if post_text:
            st.session_state["generated_post"] = post_text
            save_json(
                os.path.join(DATA_DIR, "generated_post_preview.json"),
                {"post": post_text, "topic": content.get("title")},
            )
            st.success("✅ Post generated successfully!")
        else:
            st.warning("⚠️ No post generated. Check your LLM setup or input content.")

# --- Step 4: Show and Publish ---
post_text = st.session_state.get("generated_post")

if post_text:
    st.subheader("✍️ Generated LinkedIn Post")
    st.text_area("Post Preview", post_text, height=400)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Save Locally"):
            post_to_linkedin(post_text, publish=False, metadata={"topic": content.get("title")})
            st.success("Saved locally to /data/generated_posts.json")

    with col2:
        if st.button("🚀 Publish to LinkedIn"):
            with st.spinner("Publishing to LinkedIn..."):
                resp = post_to_linkedin(post_text, publish=True, metadata={"topic": content.get("title")})
            if resp.get("published"):
                st.success("✅ Successfully posted to LinkedIn!")
            else:
                st.error(f"❌ Failed to post: {resp}")
else:
    st.info("❕ Generate a post first before saving or publishing.")


st.markdown("---")
st.caption("Built with ❤️ using LangChain + Streamlit + Gemini")