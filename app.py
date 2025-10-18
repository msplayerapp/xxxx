import os
import requests
import json
import time
import urllib.parse

STATIC_AUTH_TOKEN = os.getenv("AKASH_STATIC_TOKEN")
SUBSCRIBER_ID = os.getenv("AKASH_SUBSCRIBER_ID")
fuck = os.getenv("fuck_b")
BASE_URL = os.getenv("AKASH_API_URL")
USER_NAME = os.getenv("AKASH_USERNAME", "CoderBoyBD")

DATA_FILE = "data.json"
OUTPUT_M3U = "playlist.m3u"

def fetch_tokens(content_id):
    token_url = f"{BASE_URL}/auth/auth-service/v1/oauth/token-service/token"
    token_payload = {
        "action": "stream",
        "epids": [],
        "provider": "AkashGo",
        "contentId": content_id
    }

    token_headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "appversion": "1.0.34",
        "authorization": f"bearer {STATIC_AUTH_TOKEN}",
        "baid": fuck,
        "subscriberid": SUBSCRIBER_ID,
        "subscriptiontype": "FREEMIUM",
        "x-app-id": "123456",
        "x-app-key": "123456",
        "x-authenticated-userid": SUBSCRIBER_ID,
        "x-device-id": str(int(time.time() * 1000)),
        "x-subscriber-id": SUBSCRIBER_ID,
        "x-subscriber-name": USER_NAME,
        "user-agent": "okhttp/4.9.3"
    }

    try:
        response = requests.post(token_url, headers=token_headers, json=token_payload, timeout=10)
        data = response.json()
        if data.get("code") != 0:
            print(f"[] Token error for {content_id}: {data.get('message')}")
            return None, None
        return data["data"]["token"], data["data"]["param2"]
    except Exception as e:
        print(f"[] Token fetch failed for {content_id}: {e}")
        return None, None
