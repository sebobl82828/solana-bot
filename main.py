import re
import tweepy
import requests
import time
from telegram import Bot

# 🟢 Hämta API-nycklar från Render (via Environment Variables)
import os
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 🟢 MÖNSTER FÖR SOLANA CONTRACT ADDRESSES (Base58, 32-44 tecken)
SOLANA_CA_REGEX = r"\b[1-9A-HJ-NP-Za-km-z]{32,44}\b"

# 🟢 TELEGRAM BOT
telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN)

def send_telegram_message(message):
    """Skicka ett Telegram-meddelande."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=payload)

def get_latest_tweets(client, usernames, last_tweet_ids):
    """Hämtar de senaste tweetsen från valda konton."""
    for username in usernames:
        try:
            user = client.get_user(username=username, user_auth=False)
            tweets = client.get_users_tweets(user.data.id, max_results=3, tweet_fields=["created_at"])
            
            if tweets.data:
                for tweet in tweets.data:
                    if username not in last_tweet_ids or tweet.id > last_tweet_ids[username]:
                        last_tweet_ids[username] = tweet.id
                        matches = re.findall(SOLANA_CA_REGEX, tweet.text)
                        if matches:
                            message = f"🚀 Ny Solana Token!\n🔹 CA: {matches[0]}\n🔗 Tweet: https://twitter.com/i/web/status/{tweet.id}"
                            send_telegram_message(message)
                            print(f"🔔 Ny Solana CA hittad: {matches[0]}")
        except tweepy.errors.TooManyRequests:
            print("⚠️ För många förfrågningar! Väntar 30 minuter...")
            time.sleep(1800)  # Vänta 30 minuter om vi får 429-fel
        except Exception as e:
            print(f"Fel vid hämtning av tweets från @{username}: {e}")

def start_polling():
    """Hämtar nya tweets var 15:e minut istället för att streama."""
    client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
    konton = ["elonmusk"]  # Börja med 1 konto
    last_tweet_ids = {}

    while True:
        get_latest_tweets(client, konton, last_tweet_ids)
        print("✅ Väntar 15 minuter innan nästa hämtning...")
        time.sleep(900)  # Vänta 15 minuter mellan varje hämtning

if __name__ == "__main__":
    start_polling()
