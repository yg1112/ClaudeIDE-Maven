#!/usr/bin/env python3
"""
Reddit Client - Wrapper for Reddit API interactions
"""

import yaml
import time
import random
from typing import Dict, Any, List

try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False
    print("⚠️  PRAW not installed. Install with: pip install praw")


class RedditClient:
    """Reddit API client wrapper."""

    def __init__(self, config_path: str):
        """Initialize Reddit client with config."""
        with open(config_path) as f:
            config = yaml.safe_load(f)

        self.config = config.get('reddit', {})

        if not PRAW_AVAILABLE:
            print("⚠️  RedditClient initialized (stub mode - PRAW not installed)")
            self.reddit = None
            return

        # Initialize PRAW Reddit instance
        try:
            self.reddit = praw.Reddit(
                client_id=self.config['client_id'],
                client_secret=self.config['client_secret'],
                username=self.config['username'],
                password=self.config['password'],
                user_agent=self.config['user_agent']
            )

            # Test connection
            self.reddit.user.me()
            print(f"✅ RedditClient connected as u/{self.config['username']}")

        except Exception as e:
            print(f"❌ RedditClient initialization failed: {e}")
            self.reddit = None

    def search_posts(
        self,
        subreddit: str,
        query: str,
        time_filter: str = 'week',
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for posts in a subreddit."""

        if not self.reddit:
            print(f"⚠️  Cannot search (Reddit not connected)")
            return []

        try:
            subreddit_obj = self.reddit.subreddit(subreddit)
            submissions = subreddit_obj.search(
                query,
                time_filter=time_filter,
                limit=limit,
                sort='relevance'
            )

            posts = []
            for submission in submissions:
                posts.append({
                    'id': submission.id,
                    'title': submission.title,
                    'body': submission.selftext,
                    'url': f"https://reddit.com{submission.permalink}",
                    'score': submission.score,
                    'num_comments': submission.num_comments,
                    'created_utc': submission.created_utc,
                    'author': str(submission.author) if submission.author else '[deleted]',
                    'subreddit': str(submission.subreddit)
                })

            return posts

        except Exception as e:
            print(f"❌ Search error in r/{subreddit}: {e}")
            return []

    def get_new_posts(self, subreddit: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get new posts from a subreddit."""

        if not self.reddit:
            print(f"⚠️  Cannot get posts (Reddit not connected)")
            return []

        try:
            subreddit_obj = self.reddit.subreddit(subreddit)
            submissions = subreddit_obj.new(limit=limit)

            posts = []
            for submission in submissions:
                posts.append({
                    'id': submission.id,
                    'title': submission.title,
                    'body': submission.selftext,
                    'url': f"https://reddit.com{submission.permalink}",
                    'score': submission.score,
                    'num_comments': submission.num_comments,
                    'created_utc': submission.created_utc,
                    'author': str(submission.author) if submission.author else '[deleted]',
                    'subreddit': str(submission.subreddit)
                })

            return posts

        except Exception as e:
            print(f"❌ Error getting posts from r/{subreddit}: {e}")
            return []

    def get_post_with_comments(self, post_url: str) -> Dict[str, Any]:
        """Get a post with all its comments."""

        if not self.reddit:
            print(f"⚠️  Cannot get post (Reddit not connected)")
            return {'title': '', 'comments': []}

        try:
            submission = self.reddit.submission(url=post_url)
            submission.comments.replace_more(limit=0)  # Don't load "more comments"

            comments = []
            for comment in submission.comments.list():
                comments.append({
                    'id': comment.id,
                    'body': comment.body,
                    'author': str(comment.author) if comment.author else '[deleted]',
                    'score': comment.score,
                    'created_utc': comment.created_utc
                })

            return {
                'id': submission.id,
                'title': submission.title,
                'body': submission.selftext,
                'url': f"https://reddit.com{submission.permalink}",
                'score': submission.score,
                'num_comments': submission.num_comments,
                'comments': comments
            }

        except Exception as e:
            print(f"❌ Error fetching post: {e}")
            return {'title': '', 'comments': []}

    def reply_to_post(
        self,
        post_id: str,
        reply_text: str,
        dry_run: bool = True
    ) -> str:
        """Reply to a Reddit post."""

        if dry_run:
            print(f"[DRY RUN] Would reply to post {post_id}")
            return f"fake_reply_{post_id}"

        # TODO: Implement actual posting
        # submission = self.reddit.submission(id=post_id)
        # comment = submission.reply(reply_text)
        # return comment.id

        print(f"❌ Actual posting not implemented yet")
        return None

    def reply_to_comment(
        self,
        comment_id: str,
        reply_text: str,
        dry_run: bool = True
    ) -> str:
        """Reply to a Reddit comment."""

        if dry_run:
            print(f"[DRY RUN] Would reply to comment {comment_id}")
            return f"fake_reply_{comment_id}"

        # TODO: Implement
        return None

    def get_user_karma(self) -> Dict[str, int]:
        """Get current user's karma."""
        # TODO: Implement
        return {'post': 0, 'comment': 0, 'total': 0}

    def human_delay(self):
        """Wait a random human-like delay."""
        delay = random.randint(10, 120)
        print(f"⏳ Waiting {delay} seconds (human-like delay)...")
        time.sleep(delay)
