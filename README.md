# 🤖 PulsePost 

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/downloads/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**An intelligent content automation system that discovers trending topics, extracts article content, and generates engaging LinkedIn posts using AI.**

[Features](#-features) • [Architecture](#-architecture) • [Setup](#-installation--setup) • [Usage](#-usage) • [Configuration](#-configuration)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [System Flow](#-system-flow)
- [Installation & Setup](#-installation--setup)
  - [Option 1: Using UV (Recommended)](#option-1-using-uv-recommended)
  - [Option 2: Using Pip](#option-2-using-pip)
- [Configuration](#-configuration)
- [Usage](#-usage)
  - [CLI Mode](#1-cli-mode-mainpy)
  - [Web Interface](#2-web-interface-apppy)
- [Tool Modules](#-tool-modules)
- [API Integration](#-api-integration)
- [Data Storage](#-data-storage)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

**LinkedIn Automation MVP (PulsePost v2)** is an intelligent content automation system designed to streamline your LinkedIn content creation workflow. It leverages multiple data sources (Google Search, DuckDuckGo, Reddit) to discover trending topics, extracts high-quality article content, and uses Google's Gemini AI to generate professional, engaging LinkedIn posts that resonate with your audience.

The system provides both a **CLI interface** for quick automation and a **Streamlit web interface** for interactive content management, making it flexible for different use cases and user preferences.

---

## ✨ Features

### 🔍 **Multi-Source Topic Discovery**

- **SerpAPI Integration**: Fetch trending topics from Google search results
- **DuckDuckGo Fallback**: Alternative search engine for topic discovery
- **Reddit Integration**: Pull hot topics from tech-focused subreddits (r/technews, r/tech)
- **Intelligent Deduplication**: Automatically removes duplicate topics across sources

### 📰 **Advanced Content Extraction**

- **Primary Method**: Uses Trafilatura for high-quality article extraction
- **Fallback Mechanism**: BeautifulSoup-based extraction when Trafilatura fails
- **Smart Content Detection**: Identifies main content containers and filters noise
- **Clean Text Processing**: Removes excessive whitespace and formatting artifacts

### 🤖 **AI-Powered Post Generation**

- **Google Gemini Integration**: Uses Gemini 2.5 Flash model for content generation
- **Customizable Prompts**: Template-based system for consistent post style
- **Professional Tone**: Generates posts optimized for LinkedIn's professional audience
- **Engagement-Focused**: Creates content designed to spark conversation and engagement

### 📤 **LinkedIn Publishing**

- **Direct API Integration**: Post directly to LinkedIn using OAuth2
- **Preview Mode**: Review posts before publishing
- **Local Backup**: Automatically saves all generated posts as JSON
- **Error Handling**: Graceful fallbacks when API credentials are unavailable

### 🖥️ **Dual Interface**

- **CLI Mode**: Fast, scriptable automation for power users
- **Web Interface**: Beautiful Streamlit UI for interactive content management
- **Rich Formatting**: Enhanced terminal output with syntax highlighting

---

## 🏗️ Architecture

The system follows a **modular architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                     │
│  ┌────────────────────┐      ┌─────────────────────────┐  │
│  │   CLI (main.py)    │      │ Web UI (app.py)         │  │
│  │   - Rich Terminal  │      │ - Streamlit Dashboard   │  │
│  └────────────────────┘      └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     Tool/Service Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ search_tool  │  │ fetch_tool   │  │ post_gen_tool│     │
│  │ - SerpAPI    │  │ - Trafilatura│  │ - LangChain  │     │
│  │ - DuckDuckGo │  │ - BS4        │  │ - Gemini AI  │     │
│  │ - Reddit     │  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              linkedin_tool                            │  │
│  │              - OAuth2 Authentication                  │  │
│  │              - UGC Posts API                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    External APIs Layer                       │
│  ┌─────────┐  ┌──────────┐  ┌────────┐  ┌──────────────┐  │
│  │ Google  │  │ DuckDuck │  │ Reddit │  │   LinkedIn   │  │
│  │ (Serp)  │  │   Go     │  │  API   │  │     API      │  │
│  └─────────┘  └──────────┘  └────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Persistence Layer                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   data/ directory                     │  │
│  │  - trending_topics.json                               │  │
│  │  - extracted_content.json                             │  │
│  │  - generated_post_preview.json                        │  │
│  │  - generated_posts.json                               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### **Design Principles**

1. **Modularity**: Each tool is independent and can be used standalone
2. **Fail-Safe**: Multiple fallback mechanisms ensure system reliability
3. **Data Persistence**: All intermediate results are saved for debugging and audit
4. **API Abstraction**: External APIs are wrapped in clean interfaces
5. **Error Handling**: Comprehensive logging and graceful error recovery

---

## 📂 Project Structure

```
linkedin_automation/
├── main.py                      # CLI entry point
├── app.py                       # Streamlit web interface
├── pyproject.toml              # UV/Python project configuration
├── requirements.txt            # Pip dependencies
├── uv.lock                     # UV lock file (dependency resolution)
├── README.md                   # This file
│
├── tools/                      # Core functionality modules
│   ├── search_tool.py         # Topic discovery (SerpAPI/DuckDuckGo/Reddit)
│   ├── fetch_tool.py          # Article content extraction
│   ├── post_gen_tool.py       # AI post generation (LangChain + Gemini)
│   └── linkedin_tool.py       # LinkedIn API integration
│
├── utils/                      # Helper utilities
│   └── helper.py              # LinkedIn OAuth helper and API utilities
│
├── prompts/                    # AI prompt templates
│   └── post_prompt.txt        # LinkedIn post generation template
│
├── data/                       # Generated data storage
│   ├── trending_topics.json
│   ├── extracted_content.json
│   ├── generated_post_preview.json
│   ├── generated_posts.json
│   └── sample_article_text.txt
│
└── docs/                       # Documentation
    └── plan.md                # Development plan (internal)
```

---

## 🔄 System Flow

### **Complete Workflow**

```
1. TOPIC DISCOVERY
   ├── Query Reddit for hot topics in tech subreddits
   ├── Use first Reddit result as search query for SerpAPI/DuckDuckGo
   ├── Merge and deduplicate results
   └── Save to: data/trending_topics.json

2. USER SELECTION
   ├── Display topics with source attribution
   └── User selects topic of interest

3. CONTENT EXTRACTION
   ├── Fetch URL using Trafilatura (primary)
   ├── Fallback to Requests + BeautifulSoup if needed
   ├── Extract: title, main text, URL
   └── Save to: data/extracted_content.json

4. POST GENERATION
   ├── Load prompt template from prompts/post_prompt.txt
   ├── Initialize Gemini AI (via LangChain)
   ├── Generate LinkedIn post with article context
   └── Preview post to user

5. PUBLISHING (Optional)
   ├── Option A: Save locally to data/generated_posts.json
   └── Option B: Publish directly to LinkedIn via API

6. DATA PERSISTENCE
   └── All steps save intermediate results for auditing
```

### **Data Flow Diagram**

```
User Input → Search APIs → Topic Selection → Content Extraction
                                                     ↓
                                              Article Text
                                                     ↓
                                    Gemini AI (via LangChain)
                                                     ↓
                                           Generated Post
                                                     ↓
                                    ┌────────────────┴────────────────┐
                                    ↓                                  ↓
                            LinkedIn API                      Local JSON Storage
                         (if credentials exist)              (data/generated_posts.json)
```

---

## 🚀 Installation & Setup

### **Prerequisites**

- **Python 3.13+** (Required)
- **Google API Key** (For Gemini AI)
- **Optional**: SerpAPI key, Reddit API credentials, LinkedIn API credentials

### **Option 1: Using UV (Recommended)**

#### **1. Install UV**

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
If your system does not have ```curl```, you can use ```wget```

```bash
wget -qO- https://astral.sh/uv/install.sh | sh
```

#### **2. Clone the Repository**

```bash
git clone https://github.com/Arslaan-Siddiqui-TSM/PulsePost
cd PulsePost
```

#### **3. Create Virtual Environment**

```bash
uv venv
```

#### **4. Activate Virtual Environment**

**Windows (cmd):**

```cmd
.venv\Scripts\activate
```

**Windows (PowerShell):**

```powershell
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

#### **5. Install Dependencies**

```bash
uv sync
```

This will install all dependencies from `pyproject.toml`.

---

### **Option 2: Using Pip**

#### **1. Clone the Repository**

```bash
git clone https://github.com/Arslaan-Siddiqui-TSM/PulsePost
cd PulsePost
```

#### **2. Create Virtual Environment**

**Windows:**

```cmd
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### **3. Install Dependencies**

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### **1. Create Environment File**

Create a `.env` file in the project root:

```bash
# Required: Google Gemini API Key
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Search Configuration
DEFAULT_SEARCH_QUERY=latest tech news

# Optional: SerpAPI (for Google Search)
SERPAPI_API_KEY=your_serpapi_key

# Optional: Reddit API
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=linkedin_auto_mvp

# Optional: LinkedIn API (for publishing)
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token
LINKEDIN_AUTHOR_URN=urn:li:person:your_person_id
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
```

### **2. Obtain API Keys**

#### **Google Gemini API Key (Required)**

1. Visit [Google AI Studio](https://aistudio.google.com/api-keys)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy and add to `.env` as `GOOGLE_API_KEY`

#### **SerpAPI Key (Optional)**

1. Sign up at [SerpAPI](https://serpapi.com/)
2. Get your API key from the dashboard
3. Add to `.env` as `SERPAPI_API_KEY`

#### **Reddit API (Optional)**

1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Click "Create App" → Select "script"
3. Note your `client_id` and `client_secret`
4. Add to `.env`

#### **LinkedIn API (Optional)**

1. Create a LinkedIn App at [LinkedIn Developers](https://www.linkedin.com/developers/apps)
2. Request OAuth scopes: `openid`, `profile`, `email`, `w_member_social`
3. Run the helper utility:
   ```bash
   python utils/helper.py
   ```
4. Follow the prompts to get your access token and author URN
5. Add credentials to `.env`

---

## 💻 Usage

### **1. CLI Mode (main.py)**

The command-line interface provides a fast, scriptable way to generate posts.

```bash
python main.py
```

**Workflow:**

1. System fetches trending topics based on `DEFAULT_SEARCH_QUERY`
2. Displays numbered list of topics with sources
3. User selects topic by number
4. System extracts article content
5. Generates LinkedIn post using AI
6. Displays preview
7. _(Optional)_ Prompts to publish to LinkedIn

**Example Output:**

```
LinkedIn Auto MVP

Searching for trending topics (latest tech news)...

1. New AI Framework Released by Google — [web] SerpAPI search
2. Meta Announces VR Headset — reddit
3. Tesla's Latest Autopilot Update — [web] DuckDuckGo search

Select topic: 1

Fetching content for: New AI Framework Released by Google

Generating LinkedIn post...

--- POST PREVIEW ---

🚀 Google just dropped a game-changing AI framework...

[Generated post content]

--- End ---
```

---

### **2. Web Interface (app.py)**

The Streamlit interface provides a visual, interactive experience.

```bash
streamlit run app.py
```

**Features:**

- 🔍 **Step 1**: Search for trending topics with custom query
- 📈 **Step 2**: Browse and select topics
- 📰 **Step 3**: Preview extracted article content (editable)
- ✍️ **Step 4**: Generate LinkedIn post with AI
- 💾 **Step 5**: Save locally or publish to LinkedIn

**Interface Highlights:**

- Live content editing before post generation
- Side-by-side preview of article and generated post
- One-click save/publish buttons
- Real-time status updates and error handling

**Access:** Once started, open your browser to `http://localhost:8501`

---

## 🛠️ Tool Modules

### **1. search_tool.py**

**Purpose**: Multi-source topic discovery

**Functions:**

- `get_trending_topics(query, web_limit, reddit_limit)` → List[Dict]

**Sources** (in priority order):

1. Reddit (r/technews, r/tech)
2. SerpAPI (Google Search)
3. DuckDuckGo (fallback)

**Output Format:**

```python
[
  {
    "title": "Article Title",
    "url": "https://example.com/article",
    "source": "[web] SerpAPI search" | "reddit" | "[web] DuckDuckGo search"
  }
]
```

**Key Features:**

- Automatic deduplication by URL and title
- Intelligent fallback chain
- Uses first Reddit result as search query seed

---

### **2. fetch_tool.py**

**Purpose**: Article content extraction

**Functions:**

- `fetch_article_content(url)` → Dict

**Methods:**

1. **Primary**: Trafilatura (high-quality extraction)
2. **Fallback**: Requests + BeautifulSoup (robust extraction)

**Output Format:**

```python
{
  "title": "Article Title",
  "text": "Full article text...",
  "url": "https://example.com/article"
}
```

**Extraction Strategy:**

- Identifies main content containers (`<main>`, `<article>`, etc.)
- Extracts text from semantic elements (`<p>`, `<h1>`, `<li>`)
- Cleans excessive whitespace and formatting
- Returns placeholders if all methods fail

---

### **3. post_gen_tool.py**

**Purpose**: AI-powered LinkedIn post generation

**Functions:**

- `generate_linkedin_post(article_text, prompt_path)` → str

**Architecture:**

```
Article Text → Prompt Template → LangChain → Gemini AI → Generated Post
```

**Configuration:**

- **Model**: Gemini 2.5 Flash
- **Temperature**: 0.7 (balanced creativity)
- **Prompt**: Loaded from `prompts/post_prompt.txt`

**Output Characteristics:**

- 150-word limit
- Professional yet conversational tone
- Includes hook, body, CTA
- 3-5 relevant hashtags
- Emoji usage for engagement

---

### **4. linkedin_tool.py**

**Purpose**: LinkedIn API integration

**Functions:**

- `post_to_linkedin(post_text, publish, metadata)` → Dict
- `get_linkedin_author_urn(token)` → str

**Modes:**

1. **Preview Mode** (`publish=False`): Saves to JSON only
2. **Publish Mode** (`publish=True`): Posts to LinkedIn + saves locally

**API Details:**

- **Endpoint**: `https://api.linkedin.com/v2/ugcPosts`
- **Method**: POST
- **Auth**: Bearer token (OAuth2)
- **Protocol**: RestLI 2.0.0

**Error Handling:**

- Gracefully handles missing credentials
- Auto-saves locally on API failures
- Provides detailed error messages

---


## 💾 Data Storage

All generated data is stored in the `data/` directory:

### **File Descriptions**

| File                          | Purpose               | Format                       |
| ----------------------------- | --------------------- | ---------------------------- |
| `trending_topics.json`        | Search results        | Array of topic objects       |
| `extracted_content.json`      | Article content       | Object with title, text, url |
| `generated_post_preview.json` | Latest generated post | Object with post and topic   |
| `generated_posts.json`        | All published posts   | Array with timestamps        |

### **Example: generated_posts.json**

```json
[
  {
    "timestamp": "2025-10-15T10:30:00.000Z",
    "post": "🚀 Here's the generated LinkedIn post...",
    "metadata": {
      "topic": "Article Title"
    }
  }
]
```

---

## 🐛 Troubleshooting

### **Common Issues**

#### **1. "GOOGLE_API_KEY not found"**

- **Solution**: Create `.env` file and add your Google API key
- **Check**: Ensure `.env` is in project root, not subdirectory

#### **2. "No topics found"**

- **Cause**: All search APIs failed (network issue or invalid keys)
- **Solution**:
  - Check internet connection
  - Verify SerpAPI/Reddit credentials
  - System will fallback to DuckDuckGo if others fail

#### **3. "Article extraction failed"**

- **Cause**: Website blocks scrapers or has complex structure
- **Solution**: Try a different article URL
- **Note**: System has two fallback extraction methods

#### **4. "LinkedIn token expired"**

- **Symptom**: 401/403 errors when publishing
- **Solution**: Re-run `python utils/helper.py` to get new token
- **Note**: Posts are always saved locally even if publishing fails

#### **5. Streamlit not found**

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or with UV
uv add streamlit
```

---

## 🎯 Customization

### **Modify Post Generation Prompt**

Edit `prompts/post_prompt.txt` to customize:

- Writing style and tone
- Post structure
- Target audience
- Word limits
- Hashtag strategy

### **Change AI Model**

In `tools/post_gen_tool.py`, modify:

```python
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # Change model here
    temperature=0.7            # Adjust creativity
)
```

### **Adjust Search Limits**

Modify function calls:

```python
# In main.py or app.py
topics = get_trending_topics(
    query="your query",
    web_limit=5,      # Number of web results
    reddit_limit=5    # Number of Reddit results
)
```

---

## 📊 Workflow Examples

### **Example 1: Quick Daily Post (CLI)**

```bash
# Uses default search query from .env
python main.py
# Select topic → Generate post → Save locally
```

### **Example 2: Custom Topic Search (Web UI)**

```bash
streamlit run app.py
# Change query to "AI agents" → Search → Generate
```

### **Example 3: Batch Processing (Script)**

```python
from tools.search_tool import get_trending_topics
from tools.fetch_tool import fetch_article_content
from tools.post_gen_tool import generate_linkedin_post

topics = get_trending_topics(web_limit=10)
for topic in topics[:3]:  # Process top 3
    content = fetch_article_content(topic['url'])
    post = generate_linkedin_post(content['text'])
    print(f"Generated post for: {topic['title']}")
```

---

## 🚦 Rate Limiting

### **API Limits (Approximate)**

| Service       | Free Tier Limit    | Notes                |
| ------------- | ------------------ | -------------------- |
| Google Gemini 2.5 flash | 15 requests/minute | Check current limits |
| SerpAPI       | 1000 searches/month | Paid plans available |
| Reddit        | 60 requests/minute | OAuth required       |
| LinkedIn      | Varies by app      | Monitor usage        |

**Recommendation**: Implement delays between requests for production use.

---

## 📈 Future Enhancements

- [ ] Image generation and attachment

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 👤 Author

**Arslaan Siddiqui**

- GitHub: [@arslaan5](https://github.com/arslaan5)
- LinkedIn: [@arslaan365](https://www.linkedin.com/in/arslaan365/)

---

## 🙏 Acknowledgments

- **LangChain** - For the LLM orchestration framework
- **Google Gemini** - For the powerful AI model
- **Streamlit** - For the beautiful web interface
- **Trafilatura** - For robust article extraction
- **Reddit PRAW** - For Reddit API integration

---

## 📞 Support

If you have questions or need help:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Open an [Issue](https://github.com/Arslaan-Siddiqui-TSM/PulsePost/issues)
3. Contact me on [LinkedIn](https://www.linkedin.com/in/arslaan365/)

---

<div align="center">

⭐ Star this repo if you find it helpful!

</div>
