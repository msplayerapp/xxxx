import os
import requests
import json
import time
import urllib.parse

# === Load environment variables ===
STATIC_AUTH_TOKEN = os.getenv("AKASH_STATIC_TOKEN")
SUBSCRIBER_ID = os.getenv("AKASH_SUBSCRIBER_ID")
FUCK_B = os.getenv("FUCK_B")
BASE_URL = os.getenv("AKASH_API_URL")
USER_NAME = os.getenv("AKASH_USERNAME", "CoderBoyBD")
APP_ID = os.getenv("AKASH_APP_ID", "123456")
APP_KEY = os.getenv("AKASH_APP_KEY", "123456")
DEVICE_TYPE = os.getenv("AKASH_DEVICE_TYPE", "ANDROID")
DEVICE_PLATFORM = os.getenv("AKASH_DEVICE_PLATFORM", "PC")
USER_AGENT = os.getenv("AKASH_USER_AGENT", "okhttp/4.9.3")
SUBSCRIPTION_TYPE = os.getenv("AKASH_SUBSCRIPTION_TYPE", "FREEMIUM")
DTH_STATUS = os.getenv("AKASH_DTH_STATUS", "DTH With Binge")

DATA_FILE = "data.json"
OUTPUT_M3U = "playlist.m3u"

# === Fetch token for a content ID ===
def fetch_tokens(content_id):
    token_url = f"{BASE_URL}/auth/auth-service/v1/oauth/token-service/token"
    payload = {
        "action": "stream",
        "epids": [],
        "provider": "AkashGo",
        "contentId": content_id
    }
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "appversion": "1.0.34",
        "authorization": f"bearer {STATIC_AUTH_TOKEN}",
        "baid": FUCK_B,
        "subscriberid": SUBSCRIBER_ID,
        "subscriptiontype": SUBSCRIPTION_TYPE,
        "x-app-id": APP_ID,
        "x-app-key": APP_KEY,
        "x-authenticated-userid": SUBSCRIBER_ID,
        "x-device-id": str(int(time.time() * 1000)),
        "x-device-platform": DEVICE_PLATFORM,
        "x-device-type": DEVICE_TYPE,
        "x-subscriber-id": SUBSCRIBER_ID,
        "x-subscriber-name": USER_NAME,
        "user-agent": USER_AGENT
    }
    try:
        resp = requests.post(token_url, headers=headers, json=payload, timeout=10)
        data = resp.json()
        if data.get("code") != 0:
            print(f"[] Token error for {content_id}: {data.get('message')}")
            return None, None
        return data["data"]["token"], data["data"]["param2"]
    except Exception as e:
        print(f"[] Token fetch failed for {content_id}: {e}")
        return None, None

# === Fetch content info ===
def fetch_content(content_id, bearer_token, license_session):
    url = f"{BASE_URL}/content-subscriber-detail/api/content/info/vod/{content_id}"
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {bearer_token}",
        "user-agent": USER_AGENT
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        if data.get("code") != 0:
            print(f"[] Content error for {content_id}: {data.get('message')}")
            return None
        meta = data["data"]["meta"]
        detail = data["data"]["detail"]
        mpd = detail.get("dashWidewinePlayUrl")
        license_url = detail.get("dashWidewineLicenseUrl")
        poster = meta.get("posterImage")
        title = meta.get("vodTitle", f"Content_{content_id}")
        if not mpd or not license_url:
            print(f"[] Missing stream info for {content_id}")
            return None
        encoded_session = urllib.parse.quote(license_session, safe="")
        full_license = f"{license_url}&ls_session={encoded_session}"
        return {"title": title, "mpd": mpd, "license": full_license, "poster": poster}
    except Exception as e:
        print(f"[] Failed fetching content {content_id}: {e}")
        return None

# === Make M3U entry ===
def make_m3u_entry(info):
    return f'''#EXTINF:-1 group-title="AKASHGO" tvg-id="" tvg-logo="{info['poster']}", {info['title']}
#EXTVLCOPT:http-user-agent={USER_AGENT}
#KODIPROP:inputstream.adaptive.manifest_type=dash
#KODIPROP:inputstream.adaptive.license_type=com.widevine.alpha
#KODIPROP:inputstream.adaptive.license_key={info['license']}
{info['mpd']}

'''

# === Main ===
if __name__ == "__main__":
    print("=== Akash Go → Playlist Generator ===\n")
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        print("DATA LOADED:", data)
    except Exception as e:
        print(f"[] Failed to read {DATA_FILE}: {e}")
        exit()

    m3u_output = "#EXTM3U\n\n"

    if not data:
        print("[] WARNING: data.json is empty! No content to process.")
    for content_id in data.keys():
        print(f"[] Processing Content ID: {content_id}")
        bearer, ls_token = fetch_tokens(content_id)
        if not bearer or not ls_token:
            continue
        content_info = fetch_content(content_id, bearer, ls_token)
        if content_info:
            m3u_output += make_m3u_entry(content_info)
            print(f"[] Added: {content_info['title']}")
        else:
            print(f"[] Skipped Content ID {content_id}")

    try:
        with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
            f.write(m3u_output)
        print(f"\n Playlist generated successfully → {OUTPUT_M3U}")
    except Exception as e:
        print(f"[] Failed to save playlist: {e}")
