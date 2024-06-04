# =============================================================================
# Title: Twitter Users Tweets Scraper 
# Language: Python
# Description: This script does scrape the first 100 tweets
#   of any Twitter User.
# Author: Sasha Bouloudnine
# Date: 2023-08-08
#
# Usage:
# - Make sure you have the required libraries installed by running:
#   `pip install requests`
# - Run the script using `python twitter_scraper.py`.
# - Use the dynamic variables:
#   - `--username` to specify the Twitter username from which to scrape tweets.
#   - `--limit` to set the maximum number of tweets to scrape.
#
# Notes:
# - As of July 1st, 2023, Twitter removed public access to user tweets.
# - Starting from August 1st, 2023, the script is no longer constrained by the limit
#   but can collect a maximum of 100 tweets per user.
#
# =============================================================================


import json
import requests
import re

from database import db
from datetime import datetime
from WriteToRabbit import WriteToRabbit

# First request default headers
DEFAULT_HEADERS ={
    'authority': 'twitter.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

# All values stored here are constant, copy-pasted from the website
FEATURES_USER = '{"hidden_profile_likes_enabled":false,"hidden_profile_subscriptions_enabled":true,"responsive_web_graphql_exclude_directive_enabled":true,"verified_phone_label_enabled":false,"subscriptions_verification_info_is_identity_verified_enabled":false,"subscriptions_verification_info_verified_since_enabled":true,"highlights_tweets_tab_ui_enabled":true,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"responsive_web_graphql_timeline_navigation_enabled":true}'
FEATURES_TWEETS = '{"rweb_lists_timeline_redesign_enabled":true,"responsive_web_graphql_exclude_directive_enabled":true,"verified_phone_label_enabled":false,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_timeline_navigation_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"tweetypie_unmention_optimization_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,"responsive_web_twitter_article_tweet_consumption_enabled":false,"tweet_awards_web_tipping_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":true,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,"longform_notetweets_rich_text_read_enabled":true,"longform_notetweets_inline_media_enabled":true,"responsive_web_media_download_video_enabled":false,"responsive_web_enhance_cards_enabled":false}'

AUTHORIZATION_TOKEN = 'AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'
HEADERS = {
        'authorization': 'Bearer %s' % AUTHORIZATION_TOKEN,
        # The Bearer value is a fixed value that is copy-pasted from the website
        # 'x-guest-token': None,
}

GET_USER_URL = 'https://twitter.com/i/api/graphql/SAMkL5y_N9pmahSw8yy6gw/UserByScreenName'
GET_TWEETS_URL = 'https://twitter.com/i/api/graphql/XicnWRbyQ3WgVY__VataBQ/UserTweets'
FIELDNAMES = ['id', 'tweet_url', 'name', 'user_id', 'username', 'published_at', 'content', 'views_count', 'retweet_count', 'likes', 'quote_count', 'reply_count', 'bookmarks_count', 'medias']

class TwitterScraper:

    def __init__(self, username, q):
        # We do initiate requests Session, and we get the `guest-token` from the HomePage
        resp = requests.get("https://twitter.com/", headers=DEFAULT_HEADERS)
        self.gt = resp.cookies.get_dict().get("gt") or "".join(re.findall(r'(?<=\"gt\=)[^;]+', resp.text))
        assert self.gt
        HEADERS['x-guest-token'] = getattr(self, 'gt')
        # assert self.guest_token
        self.HEADERS = HEADERS
        assert username
        self.username = username
        self.db = db()
        self.q = q

    def get_user(self):
        # We recover the user_id required to go ahead
        arg = {"screen_name": self.username, "withSafetyModeUserFields": True}
        
        params = {
            'variables': json.dumps(arg),
            'features': FEATURES_USER,
        }

        response = requests.get(
            GET_USER_URL,
            params=params, 
            headers=self.HEADERS
        )

        try: 
            json_response = response.json()
        except requests.exceptions.JSONDecodeError: 
            print(response.status_code)
            print(response.text)
            raise

        result = json_response.get("data", {}).get("user", {}).get("result", {})
        legacy = result.get("legacy", {})

        return {
            "id": result.get("rest_id"), 
            "username": self.username, 
            "full_name": legacy.get("name")
        }

    def tweet_parser(
            self,
            user_id, 
            full_name, 
            tweet_id, 
            item_result, 
            legacy
        ):

        # It's a static method to parse from a tweet
        medias = legacy.get("entities").get("media")
        medias = ", ".join(["%s (%s)" % (d.get("media_url_https"), d.get('type')) for d in legacy.get("entities").get("media")]) if medias else None

        return {
            "id": tweet_id,
            "tweet_url": f"https://twitter.com/{self.username}/status/{tweet_id}",
            "name": full_name,
            "user_id": user_id,
            "username": self.username,
            "published_at": legacy.get("created_at"),
            "content": legacy.get("full_text"),
            "views_count": item_result.get("views", {}).get("count"),
            "retweet_count": legacy.get("retweet_count"),
            "likes": legacy.get("favorite_count"),
            "quote_count": legacy.get("quote_count"),
            "reply_count": legacy.get("reply_count"),
            "bookmarks_count": legacy.get("bookmark_count"),
            "medias": medias
        }

    def iter_tweets(self, limit=100):

        # The main navigation method
        _user = self.get_user()
        full_name = _user.get("full_name")
        user_id = _user.get("id")
        if not user_id:
            raise NotImplementedError
        cursor = None
        _tweets = []
        while True:
            var = {
                "userId": user_id, 
                "count": 100, 
                "cursor": cursor, 
                "includePromotedContent": True,
                "withQuickPromoteEligibilityTweetFields": True, 
                "withVoice": True,
                "withV2Timeline": True
            }

            params = {
                'variables': json.dumps(var),
                'features': FEATURES_TWEETS,
            }

            response = requests.get(
                GET_TWEETS_URL,
                params=params,
                headers=self.HEADERS,
            )

            json_response = response.json()

            result = json_response.get("data", {}).get("user", {}).get("result", {})
            timeline = result.get("timeline_v2", {}).get("timeline", {}).get("instructions", {})
            entries = [x.get("entries") for x in timeline if x.get("type") == "TimelineAddEntries"]
            entries = entries[0] if entries else []

            for entry in entries:
                content = entry.get("content")
                entry_type = content.get("entryType")
                tweet_id = entry.get("sortIndex")
                if entry_type == "TimelineTimelineItem":
                    item_result = content.get("itemContent", {}).get("tweet_results", {}).get("result", {})
                    legacy = item_result.get("legacy")

                    tweet_data = self.tweet_parser(user_id, full_name, tweet_id, item_result, legacy)
                    lastWorkTime = [item[0] for item in self.db.GetPublishedAt(self.username)]

                    try:
                        if(tweet_data['published_at'] == lastWorkTime[0]):
                            self.adding_to_db()
                    except:
                        pass

                    _tweets.append(tweet_data)

                if entry_type == "TimelineTimelineCursor" and content.get("cursorType") == "Bottom":
                    # NB: after 07/01 lock and unlock — no more cursor available if no login provided i.e. max. 100 tweets per username no more
                    cursor = content.get("value")


                if len(_tweets) >= limit:
                    # We do stop — once reached tweets limit provided by user
                    break


            if len(_tweets) >= limit or cursor is None or len(entries) == 2:
                break

        return _tweets

    def adding_to_db(self, tweets=[]):
        for tweet in tweets:
            if tweet == tweets[0]:
                username = tweet['username']
                published_at = tweet['published_at']
                lastWorkTime = datetime.now()
                checkperiod = '15'
                self.db.Put(username=username, published_at=published_at, lastWorktime=lastWorkTime,checkPeriod=checkperiod, active=True)
            else:
                data = {
                    'Provider': 'Twitter',
                    'tweet' : tweet,
                }
                self.q.put(data)
            
                


def main(username, limit, q):

    username = username
    limit = limit

    assert all([username, limit])

    twitter_scraper = TwitterScraper(username, q)
    tweets = twitter_scraper.iter_tweets(limit=limit)
    twitter_scraper.adding_to_db(tweets)


