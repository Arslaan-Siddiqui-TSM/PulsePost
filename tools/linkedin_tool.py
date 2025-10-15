import os
import json
import datetime
from dotenv import load_dotenv
import requests

load_dotenv()

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)


def _save_local_post(post_text: str, metadata: dict | None = None):
    """Save the generated post locally in JSON for backup."""
    filepath = os.path.join(DATA_DIR, "generated_posts.json")
    data = []

    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []

    entry = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "post": post_text,
        "metadata": metadata or {},
    }

    data.append(entry)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return filepath


def get_linkedin_author_urn(token: str):
    """Fetch the LinkedIn URN for the authenticated user."""
    url = "https://api.linkedin.com/v2/me"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)

    if resp.status_code == 200:
        profile = resp.json()
        return f"urn:li:person:{profile.get('id')}"
    else:
        raise Exception(f"Failed to get author URN: {resp.status_code} - {resp.text}")


def post_to_linkedin(post_text: str, publish: bool = False, metadata: dict | None = None):
    """
    Posts text to LinkedIn if credentials exist, otherwise saves locally.
    publish=False => local save only (safe for MVP)
    """
    token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    author_urn = os.getenv("LINKEDIN_AUTHOR_URN")

    # If not publishing, just save locally
    if not publish:
        path = _save_local_post(post_text, metadata)
        return {
            "published": False,
            "saved_to": path,
            "message": "Post saved locally (not published)."
        }

    # Check credentials
    if not token:
        path = _save_local_post(post_text, metadata)
        return {
            "published": False,
            "saved_to": path,
            "error": "Missing LINKEDIN_ACCESS_TOKEN. Saved locally."
        }

    # Auto-fetch author URN if not set
    if not author_urn:
        try:
            author_urn = get_linkedin_author_urn(token)
        except Exception as e:
            path = _save_local_post(post_text, metadata)
            return {"published": False, "saved_to": path, "error": str(e)}

    # Prepare API call
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": post_text},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }

    try:
        resp = requests.post(url, headers=headers, json=payload)
        if resp.status_code == 201:
            _save_local_post(post_text, metadata)
            return {
                "published": True,
                "response": resp.json(),
                "message": "Successfully posted to LinkedIn."
            }
        elif resp.status_code in (401, 403):
            # Token expired or invalid
            path = _save_local_post(post_text, metadata)
            return {
                "published": False,
                "saved_to": path,
                "error": "Authentication failed. Token may have expired.",
                "status_code": resp.status_code,
            }
        else:
            path = _save_local_post(post_text, metadata)
            return {
                "published": False,
                "saved_to": path,
                "status_code": resp.status_code,
                "error": resp.text,
            }
    except Exception as e:
        path = _save_local_post(post_text, metadata)
        return {"published": False, "saved_to": path, "error": str(e)}


if __name__ == "__main__":
    # Example usage
    result = post_to_linkedin("🚀 Hello LinkedIn world! This is an automated post.", publish=True)
    print(result)

