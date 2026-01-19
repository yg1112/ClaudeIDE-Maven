#!/usr/bin/env python3
"""
Karma Builder - Build credibility without promoting product
"""

import json
from typing import Dict, Any, List
from datetime import datetime


class KarmaBuilder:
    """Karma building strategy and tracking."""

    def __init__(self, product_config_path: str, history_path: str):
        """Initialize karma builder."""
        self.history_path = history_path
        self.history = self._load_history()

    def _load_history(self) -> Dict:
        """Load karma building history."""
        try:
            with open(self.history_path) as f:
                return json.load(f)
        except FileNotFoundError:
            return {'replies': [], 'daily_counts': {}}

    def _save_history(self):
        """Save karma history."""
        with open(self.history_path, 'w') as f:
            json.dump(self.history, f, indent=2)

    def can_reply_today(self, subreddit: str, max_per_day: int) -> bool:
        """Check if we can still reply today."""
        today = datetime.now().strftime('%Y-%m-%d')
        key = f"{subreddit}_{today}"
        count = self.history['daily_counts'].get(key, 0)
        return count < max_per_day

    def find_best_karma_posts(
        self,
        posts: List[Dict[str, Any]],
        expertise: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Find best posts for karma building."""

        # Filter for posts we can answer
        opportunities = []

        for post in posts:
            # Simple heuristic: questions are good opportunities
            title = post.get('title', '').lower()
            if any(word in title for word in ['how', 'what', 'why', 'help', 'question']):
                opportunities.append(post)

        return opportunities[:10]

    def generate_karma_reply_prompt(
        self,
        post: Dict[str, Any],
        expertise: List[str] = None
    ) -> str:
        """Generate prompt for karma-building reply."""

        return f"""Generate a helpful reply to this Reddit post.

IMPORTANT: This is for KARMA BUILDING, not marketing.
- DO NOT mention any product
- DO NOT promote anything
- JUST be genuinely helpful
- Use casual, friendly tone

Post title: {post['title']}
Post body: {post.get('body', '')}

Generate a helpful 2-3 paragraph reply that adds genuine value.
"""

    def record_reply(
        self,
        subreddit: str,
        post_id: str,
        reply_id: str,
        reply_type: str
    ):
        """Record a karma-building reply."""
        today = datetime.now().strftime('%Y-%m-%d')
        key = f"{subreddit}_{today}"

        self.history['daily_counts'][key] = \
            self.history['daily_counts'].get(key, 0) + 1

        self.history['replies'].append({
            'date': datetime.now().isoformat(),
            'subreddit': subreddit,
            'post_id': post_id,
            'reply_id': reply_id,
            'type': reply_type
        })

        self._save_history()
