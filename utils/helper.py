import os
import requests
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("LINKEDIN_CLIENT_ID")
client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
token = os.getenv("LINKEDIN_ACCESS_TOKEN")


def get_token():
    """
    Step 1: Get authorization URL with proper scopes
    """
    # Required scopes for basic profile access and posting
    scopes = [
        "openid",
        "profile",
        "email",
        "w_member_social"  # For posting content
    ]
    
    redirect_uri = "http://localhost:8000/callback"
    scope_string = "%20".join(scopes)
    
    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization?"
        f"response_type=code&"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope_string}"
    )
    
    print("🔗 Open this URL in your browser to authorize:")
    print(auth_url)
    print("\n")
    
    auth_code = input("Paste the authorization code from the URL: ")

    # Step 2: Exchange code for token
    url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }

    response = requests.post(url, data=data)
    token_data = response.json()
    
    if response.status_code == 200:
        print("\n✅ Token obtained successfully!")
        print(f"Access Token: {token_data.get('access_token')}")
        print(f"\nAdd this to your .env file:")
        print(f"LINKEDIN_ACCESS_TOKEN={token_data.get('access_token')}")
    else:
        print("❌ Error getting token:", token_data)
    
    return token_data


def get_user_info():
    """
    Get user info using OpenID Connect userinfo endpoint (recommended)
    """
    url = "https://api.linkedin.com/v2/userinfo"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("✅ Success!")
        print("Response:", data)
        print("\nYour LinkedIn sub (ID):", data.get("sub"))
        print("Name:", data.get("name"))
        print("Email:", data.get("email"))
        
        # Extract person ID from sub field
        if "sub" in data:
            person_id = data["sub"]
            print(f"\nYour author URN: urn:li:person:{person_id}")
        
        return data
    else:
        print("❌ Error:", response.status_code, response.text)
        return None


if __name__ == "__main__":
    print("LinkedIn API Helper")
    print("=" * 50)
    print("\nOptions:")
    print("1. Get new token (run this first if you don't have a token)")
    print("2. Get user info (using OpenID Connect - recommended)")
    print("3. Get author URN (using legacy /v2/me endpoint)")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        get_token()
    elif choice == "2":
        get_user_info()
    else:
        print("Invalid choice")