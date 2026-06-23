import time
import json
import configparser
import requests

config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")

TWITCH_CLIENT_ID = config["TWITCH"]["CLIENT_ID"]
TWITCH_CLIENT_SECRET = config["TWITCH"]["CLIENT_SECRET"]
TWITCH_CHANNELS = [c.strip() for c in config["TWITCH"]["CHANNELS"].split(",")]

YT_API_KEY = config["YOUTUBE"]["API_KEY"]
YT_CHANNEL_IDS = [c.strip() for c in config["YOUTUBE"]["CHANNEL_IDS"].split(",")]

POLL_INTERVAL = int(config["POLLING"]["INTERVAL"])


# ─── Twitch ───────────────────────────────────────────────────────

def get_twitch_token():
    r = requests.post("https://id.twitch.tv/oauth2/token", params={
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials",
    })
    r.raise_for_status()
    return r.json()["access_token"]


def get_twitch_users(token, logins):
    r = requests.get("https://api.twitch.tv/helix/users", headers={
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {token}",
    }, params={"login": logins})
    r.raise_for_status()
    return {u["login"]: u["id"] for u in r.json()["data"]}


def get_live_streams(token, user_ids):
    r = requests.get("https://api.twitch.tv/helix/streams", headers={
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {token}",
    }, params={"user_id": user_ids})
    r.raise_for_status()
    return {s["user_login"]: s for s in r.json()["data"]}


# ─── YouTube ──────────────────────────────────────────────────────

def get_latest_videos(channel_ids):
    videos = []
    for cid in channel_ids:
        r = requests.get("https://www.googleapis.com/youtube/v3/search", params={
            "part": "snippet",
            "channelId": cid,
            "order": "date",
            "maxResults": 3,
            "type": "video",
            "key": YT_API_KEY,
        })
        r.raise_for_status()
        for item in r.json().get("items", []):
            videos.append({
                "channel": item["snippet"]["channelTitle"],
                "title": item["snippet"]["title"],
                "video_id": item["id"]["videoId"],
                "published": item["snippet"]["publishedAt"],
            })
    return videos


# ─── Main loop ────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  Twitch & YouTube мониторинг бот запущен")
    print(f"  Twitch каналы: {', '.join(TWITCH_CHANNELS)}")
    print(f"  YouTube каналов: {len(YT_CHANNEL_IDS)}")
    print(f"  Интервал проверки: {POLL_INTERVAL} сек")
    print("=" * 55)

    twitch_token = get_twitch_token()
    twitch_users = get_twitch_users(twitch_token, TWITCH_CHANNELS)
    known_live = set()
    known_yt_videos = set()

    while True:
        try:
            # Twitch
            live = get_live_streams(twitch_token, list(twitch_users.values()))
            now_live = set(live.keys())
            new_live = now_live - known_live

            for login in new_live:
                s = live[login]
                print(f"\n[TWITCH] 🔴 {login} теперь в прямом эфире!")
                print(f"         Название: {s['title']}")
                print(f"         Игра:     {s['game_name']}")
                print(f"         Зрителей: {s['viewer_count']}")
                print(f"         https://twitch.tv/{login}")

            for login in (known_live - now_live):
                print(f"\n[TWITCH] {login} закончил стрим")

            known_live = now_live

            # YouTube
            yt_videos = get_latest_videos(YT_CHANNEL_IDS)
            for v in yt_videos:
                vid = v["video_id"]
                if vid not in known_yt_videos:
                    known_yt_videos.add(vid)
                    print(f"\n[YOUTUBE] 🎬 {v['channel']} выпустил новое видео!")
                    print(f"           Название: {v['title']}")
                    print(f"           https://youtu.be/{vid}")

            # Refresh token every hour
            twitch_token = get_twitch_token()

        except Exception as e:
            print(f"[ОШИБКА] {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
