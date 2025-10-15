## 🎯 MVP Objective

> A LangChain-based Python app that:
>
> 1. Searches the web / Reddit / X for trending topics.
> 2. Lists 5–10 topics for you to pick from.
> 3. Fetches the content from the chosen topic’s URL.
> 4. Generates a LinkedIn-style post using an LLM.
> 5. Uploads it to your LinkedIn account (automatically).

All done locally or in a simple script — no workers, DBs, or vector stores unless absolutely needed.

---

## 🧱 Architecture Overview

| Layer                | Purpose                                                                         | Tech                                        |
| -------------------- | ------------------------------------------------------------------------------- | ------------------------------------------- |
| **LangChain Agent**  | Central controller coordinating the flow                                        | LangChain                                   |
| **Tools**            | Fetching search results, fetching webpage, generating post, posting to LinkedIn | Python functions wrapped as LangChain tools |
| **Orchestration**    | Just one main script that sequentially runs each step                           | Python script                               |
| **Storage**          | Temporary local files (JSON) for logs & saved posts                             | JSON files                                  |
| **Frontend (later)** | Streamlit UI to show topics & preview post                                      | Will come after MVP                         |

---

## ⚙️ MVP Component Breakdown

### 1. **LangChain Agent (Main Controller)**

The agent coordinates all tools:

* Calls search tool to find trending topics.
* Presents results to the user (CLI or Streamlit later).
* After selection, calls the content fetcher → post generator → LinkedIn poster.

**LangChain agent type:**
Use `initialize_agent` with tools and an Gemini API LLM (function-calling agent is fine).

---

### 2. **Tool 1: Trending Topic Finder**

**Goal:** Fetch ~10 trending topics (title + URL).

**Sources (choose what’s easiest):**

* **Web:** Use `SerpAPI` from LangChain.
* **Reddit:** Use `praw` (Reddit API) to fetch `popular` posts..


**Output format:**

```python
[
  {"title": "AI Hiring Surges in 2025", "url": "https://example.com/article1"},
  {"title": "Remote Work Burnout Discussion on Reddit", "url": "https://reddit.com/..."},
  ...
]
```

**Simplification:** Just fetch text and URLs, no clustering or embeddings.

---

### 3. **Tool 2: Webpage Fetcher & Content Extractor**

**Goal:** Get the text from the selected URL.

**Implementation:**

* Use `trafilatura` for article extraction.
* Return clean text (title + main content).
* If extraction fails, just use the meta description.

**Output:**

```python
{
  "title": "AI Hiring Surges in 2025",
  "text": "As the global tech market rebounds, companies are ramping up AI roles..."
}
```

---

### 4. **Tool 3: LinkedIn Post Generator**

**Goal:** Generate a LinkedIn-style post from extracted content.

**Implementation:**

* Use a simple LangChain `create_agent`:

  ```
  You are a professional LinkedIn content writer.
  Create a post about the following article, summarizing it in a conversational,
  engaging tone for professionals.
  Include relevant hashtags and a brief call to action.
  Article:
  {article_text}
  ```
* Output just plain text (post).

**No need for complex structured output parsing.**

---

### 5. **Tool 4: LinkedIn Poster**

**Goal:** Upload post text to LinkedIn.

**Options:**

* Use **LinkedIn API (via access token)** — minimal OAuth setup.
* Or, if you want simpler/no OAuth print post text to console first for manual posting (safe MVP option).

**Simplify for MVP:**
✅ For now, just print the generated post text to the console.
Later, you can add API upload once everything else works.

---

## 🧩 Data Flow 

```
User runs app →
  Agent: call TrendingTopicTool →
    list topics →
      User selects topic →
        Agent: call ContentExtractorTool(url) →
          get text →
            Agent: call PostGeneratorTool(text) →
              generate post →
                print post (or upload to LinkedIn)
```

No background tasks, no DBs, no vector stores — everything sequential.

---

## 📂 Folder Structure

```
linkedin_auto/
│
├── main.py                 # Main orchestrator / entry point
├── tools/
│   ├── search_tool.py      # Fetch trending topics
│   ├── fetch_tool.py       # Fetch webpage content
│   ├── post_gen_tool.py    # Generate LinkedIn post
│   ├── linkedin_tool.py    # (Optional) Post to LinkedIn
│
├── prompts/
│   └── post_prompt.txt     # Template for LinkedIn post generation
│
├── data/
│   ├── trending_topics.json
│   ├── extracted_content.json
│   └── generated_posts.json
│
└── requirements.txt
```

---

## 🧠 Simplified LangChain Setup

* Use Gemini API for LLM.
* Use `initialize_agent` with 3–4 tools.
* Keep temperature low (0.7) for structured output.
* Memory: none needed (stateless run).

---

## 🚀 Step-by-Step Development Plan (MVP)

| Step  | Task                           | Description                                                                   |
| ----- | ------------------------------ | ----------------------------------------------------------------------------- |
| **1** | Setup environment              | Install LangChain, trafilatura, serpapi/duckduckgo_search, openai |
| **2** | Create `search_tool`           | Query trending topics from web or Reddit                                      |
| **3** | Create `fetch_tool`            | Extract text content from chosen article                                      |
| **4** | Create `post_gen_tool`         | Generate LinkedIn post text                                                   |
| **5** | Integrate with LangChain Agent | Compose all tools into one agent pipeline                                     |
| **6** | CLI interface                  | Print topic list, let user pick (input index)                                 |
| **7** | Generate post                  | Print to console for review                                                   |
| **8** | (Optional) LinkedIn upload     | Integrate API or placeholder function                                         |
| **9** | Final polish                   | Save results to `data/` folder                                                |

---

## 💡 Optional MVP Enhancements (still lightweight)

1. **Simple ranking:** Sort trending results by recency or engagement.
2. **Post variations:** Ask LLM to generate 2 versions of the post.
3. **Basic caching:** Save fetched article text in local JSON (avoid re-fetching).
4. **Scheduling (manual):** Add a timestamped queue for posts.
5. **CLI preview/confirmation:** Let user confirm before posting.

---

## 🪄 Example User Flow (CLI MVP)

```
> python main.py

Fetching trending topics...
1. "AI Hiring Surges in 2025"
2. "Apple’s Quantum Chip Announcement"
3. "Remote Work Burnout Discussion on Reddit"

Select a topic number: 2

Fetching content...
Generating LinkedIn post...

Here’s your generated LinkedIn post:
------------------------------------------------
🚀 Big news in tech: Apple is diving into quantum computing!

Yesterday, Apple unveiled their prototype quantum chip, promising a new era of performance breakthroughs for AI and encryption. The move could redefine the competitive landscape for silicon innovation.

What do you think — hype or real leap?

#Apple #QuantumComputing #Innovation
------------------------------------------------
Do you want to post this to LinkedIn? (y/n)
```

---

## 🔒 No heavy infra needed

* Run locally on your laptop.
* No DB, no queues, no secrets manager.
* Store LinkedIn token (if used) in `.env`.
* Logs & outputs saved in `/data`.

---

## ⚠️ Important Considerations

* LinkedIn automation (via API) may require developer account approval. If that’s annoying, just print post text and manually paste it.
* Avoid scraping disallowed websites; use public APIs or `serpapi`.
* Respect Gemini API usage policies: don’t generate false or misleading claims.
* Rate limits: handle gently with small sleeps between API calls.

---

## ✅ Summary: MVP Tech Stack

| Component          | Tech                                           |
| ------------------ | ---------------------------------------------- |
| Core Orchestration | LangChain                                      |
| LLM                | Gemini API                                     |
| Search             | SerpAPI / DuckDuckGoSearchResults / Reddit API |
| Content Extraction | Trafilatura                                    |
| Post Generation    | from langchain.agents import                    create_agent                                                          |
| Posting            | Manual / LinkedIn API (optional)               |
| Storage            | JSON files                                     |
| UI                 | CLI (later Streamlit)                          |
