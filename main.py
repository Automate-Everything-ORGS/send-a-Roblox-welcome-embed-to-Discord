import requests
import time
import os
import sys

# Get secrets from Replit environment variables
COOKIE = os.getenv("ROBLOSECURITY")
GROUP_ID = os.getenv("GROUP_ID")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")

if not COOKIE or not GROUP_ID or not WEBHOOK_URL:
    print("ERROR: Please set ROBLOSECURITY, GROUP_ID, and DISCORD_WEBHOOK in Replit Secrets.")
    sys.exit(1)

HEADERS = {
    "Cookie": f".ROBLOSECURITY={COOKIE}",
    "User-Agent": "RobloxBot (Replit)",
    "X-CSRF-TOKEN": ""
}

session = requests.Session()

def update_csrf_token():
    """Get and update the Roblox CSRF token needed for POST requests."""
    res = session.post("https://auth.roblox.com/v2/logout", headers=HEADERS)
    token = res.headers.get("x-csrf-token")
    if token:
        HEADERS["X-CSRF-TOKEN"] = token
        print("[INFO] CSRF token updated.")
    else:
        print("[WARN] Failed to update CSRF token.")

def get_group_members():
    url = f"https://groups.roblox.com/v1/groups/{GROUP_ID}/users?limit=100&sortOrder=Asc"
    res = session.get(url, headers=HEADERS)
    if res.status_code == 200:
        data = res.json()
        return set(user['user']['userId'] for user in data.get('data', []))
    else:
        print(f"[ERROR] Failed to fetch group members: {res.status_code}")
        return set()

def get_user_info(user_id):
    url = f"https://users.roblox.com/v1/users/{user_id}"
    res = session.get(url)
    if res.status_code == 200:
        return res.json()
    else:
        print(f"[WARN] Failed to get info for user {user_id}")
        return None

def send_discord_embed(user):
    embed = {
        "title": "🎉 New Group Member!",
        "description": f"**{user['name']}** (`{user['id']}`) has joined the Roblox group!",
        "color": 0x00FF00,
        "thumbnail": {
            "url": f"https://www.roblox.com/headshot-thumbnail/image?userId={user['id']}&width=420&height=420&format=png"
        },
        "footer": {
            "text": "Roblox Group Join Bot"
        }
    }
    payload = {"embeds": [embed]}
    res = requests.post(WEBHOOK_URL, json=payload)
    if res.status_code == 204:
        print(f"[INFO] Sent webhook for {user['name']}")
    else:
        print(f"[ERROR] Failed to send webhook: {res.status_code} {res.text}")

def main():
    update_csrf_token()
    known_users = get_group_members()
    print(f"[INFO] Tracking {len(known_users)} members.")

    while True:
        time.sleep(60)  # Wait 60 seconds between checks
        try:
            current_users = get_group_members()
            new_users = current_users - known_users

            for user_id in new_users:
                user = get_user_info(user_id)
                if user:
                    send_discord_embed(user)

            known_users = current_users
        except Exception as e:
            print(f"[ERROR] Exception: {e}")

if __name__ == "__main__":
    main()
