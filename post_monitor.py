#!/usr/bin/env python3
"""
Post Monitor - Monitor and defend your published posts
"""

import json
from typing import Dict, Any, List
from datetime import datetime


class PostMonitor:
    """Monitor published posts and respond to comments."""

    def __init__(self, monitored_posts_path: str):
        """Initialize post monitor."""
        self.monitored_posts_path = monitored_posts_path
        self.monitored = self._load_monitored()

    def _load_monitored(self) -> Dict:
        """Load monitored posts."""
        try:
            with open(self.monitored_posts_path) as f:
                return json.load(f)
        except FileNotFoundError:
            return {'posts': []}

    def _save_monitored(self):
        """Save monitored posts."""
        with open(self.monitored_posts_path, 'w') as f:
            json.dump(self.monitored, f, indent=2)

    def add_post(self, post_url: str):
        """Add a post to monitoring."""
        self.monitored['posts'].append({
            'url': post_url,
            'added_at': datetime.now().isoformat(),
            'last_checked': None,
            'known_comment_ids': []
        })
        self._save_monitored()

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get status of all monitored posts."""
        return {
            'total_monitored': len(self.monitored['posts']),
            'posts': self.monitored['posts']
        }

    def check_for_new_comments(
        self,
        post_url: str,
        current_comments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check for new comments on a post."""

        # Find this post in our monitoring list
        post_entry = None
        for p in self.monitored['posts']:
            if p['url'] == post_url:
                post_entry = p
                break

        if not post_entry:
            return []

        known_ids = set(post_entry.get('known_comment_ids', []))
        current_ids = {c['id'] for c in current_comments}

        new_ids = current_ids - known_ids
        new_comments = [c for c in current_comments if c['id'] in new_ids]

        # Update known comments
        post_entry['known_comment_ids'] = list(current_ids)
        post_entry['last_checked'] = datetime.now().isoformat()
        self._save_monitored()

        return new_comments

    def analyze_comment(self, comment: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a comment to determine response type."""

        text = comment.get('body', '').lower()

        # Determine response type
        response_type = 'info'
        needs_response = False

        if '?' in text:
            response_type = 'question'
            needs_response = True
        elif any(word in text for word in ['bad', 'wrong', 'disagree', 'terrible']):
            response_type = 'criticism'
            needs_response = True
        elif any(word in text for word in ['thanks', 'great', 'love', 'awesome']):
            response_type = 'praise'
            needs_response = False

        return {
            'response_type': response_type,
            'needs_response': needs_response,
            'urgency': 'high' if response_type == 'criticism' else 'normal'
        }

    def prioritize_responses(
        self,
        comments_and_analyses: List[tuple]
    ) -> List[tuple]:
        """Prioritize which comments to respond to first."""

        # Sort by urgency: criticism first, then questions
        def priority_key(item):
            comment, analysis = item
            if analysis['response_type'] == 'criticism':
                return 0
            elif analysis['response_type'] == 'question':
                return 1
            else:
                return 2

        return sorted(comments_and_analyses, key=priority_key)

    def generate_defense_strategy(
        self,
        comment: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a strategy for responding to this comment."""

        return {
            'response_type': analysis['response_type'],
            'tone': 'professional' if analysis['response_type'] == 'criticism' else 'friendly',
            'urgency': analysis['urgency']
        }
