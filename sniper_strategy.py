#!/usr/bin/env python3
"""
Sniper Strategy - Two-Step Guerrilla Marketing
==============================================

Step 1: Post helpful comment WITHOUT link
Step 2: Monitor for OP asking for link, then notify user

This avoids looking like spam and feels more organic.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class SniperStrategy:
    """
    Two-step marketing approach:
    1. Provide value without promotion
    2. Wait for user to ask
    3. Notify human to provide link
    """

    def __init__(self, tracking_file: str = "data/sniper_tracking.json"):
        """Initialize sniper strategy tracker."""
        self.tracking_file = tracking_file
        self.tracking = self._load_tracking()

    def _load_tracking(self) -> Dict:
        """Load tracking data."""
        try:
            with open(self.tracking_file) as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'deployed_comments': [],  # Comments we posted
                'triggered_notifications': []  # OP replied asking for link
            }

    def _save_tracking(self):
        """Save tracking data."""
        Path(self.tracking_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self.tracking_file, 'w') as f:
            json.dump(self.tracking, f, indent=2)

    def generate_sniper_reply(
        self,
        post: Dict[str, Any],
        product_name: str,
        key_benefit: str
    ) -> Dict[str, Any]:
        """
        Generate a helpful reply WITHOUT mentioning product name or link.

        Instead, describe the approach/solution that the product enables.

        Args:
            post: Reddit post data
            product_name: Your product name (to avoid mentioning)
            key_benefit: The key benefit (e.g., "9.26x real-time speed")

        Returns:
            {
                'reply_text': str,
                'triggers': List[str],  # Words that indicate OP asking for link
                'follow_up_template': str  # Template for when OP asks
            }
        """

        # Example sniper reply (value-first, no promotion)
        reply_template = """
I had the same problem! Here's what worked for me:

{solution_approach}

The key was {key_technique}. Once I figured that out, it went from
taking {before_time} to just {after_time}.

Game changer for my workflow.
"""

        # Trigger words that indicate OP is asking for details
        triggers = [
            'what app',
            'which app',
            'what tool',
            'which tool',
            'link?',
            'what do you use',
            'what are you using',
            'can you share',
            'tell me more',
            'how did you',
            'what\'s the',
            'dm me'
        ]

        # Follow-up template (when OP asks)
        follow_up_template = """
Sure! I'll DM you the link to avoid being promotional here.

[User will manually send this with the link]
"""

        return {
            'reply_text': reply_template,
            'triggers': triggers,
            'follow_up_template': follow_up_template,
            'strategy': 'sniper_step1'
        }

    def deploy_sniper_comment(
        self,
        post_id: str,
        comment_id: str,
        comment_text: str,
        subreddit: str,
        triggers: List[str]
    ):
        """
        Record a deployed sniper comment for monitoring.

        Args:
            post_id: Reddit post ID
            comment_id: Our comment ID
            comment_text: The comment we posted
            subreddit: Subreddit name
            triggers: Trigger words to watch for
        """
        deployment = {
            'post_id': post_id,
            'comment_id': comment_id,
            'comment_text': comment_text,
            'subreddit': subreddit,
            'triggers': triggers,
            'deployed_at': datetime.now().isoformat(),
            'status': 'monitoring',  # 'monitoring', 'triggered', 'expired'
            'op_replied': False
        }

        self.tracking['deployed_comments'].append(deployment)
        self._save_tracking()

        print(f"🎯 Sniper comment deployed: {comment_id}")
        print(f"   Monitoring for: {', '.join(triggers[:3])}...")

    def check_for_triggers(
        self,
        post_id: str,
        new_comments: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Check if OP replied asking for link.

        Args:
            post_id: Reddit post ID
            new_comments: New comments on the post

        Returns:
            Notification dict if triggered, None otherwise
        """
        # Find our deployed comment for this post
        deployed = None
        for comment in self.tracking['deployed_comments']:
            if comment['post_id'] == post_id and comment['status'] == 'monitoring':
                deployed = comment
                break

        if not deployed:
            return None

        # Check new comments for triggers
        for new_comment in new_comments:
            # Check if it's a reply to our comment
            # (This requires checking parent_id in real implementation)

            comment_text = new_comment.get('body', '').lower()

            # Check for trigger words
            for trigger in deployed['triggers']:
                if trigger in comment_text:
                    # TRIGGERED! OP is asking for link
                    notification = {
                        'type': 'sniper_triggered',
                        'priority': 5,  # Highest priority
                        'post_id': post_id,
                        'comment_id': deployed['comment_id'],
                        'op_comment': new_comment,
                        'trigger_word': trigger,
                        'subreddit': deployed['subreddit'],
                        'detected_at': datetime.now().isoformat(),
                        'action_needed': 'Send follow-up with link'
                    }

                    # Update status
                    deployed['status'] = 'triggered'
                    deployed['op_replied'] = True
                    deployed['triggered_at'] = datetime.now().isoformat()

                    self.tracking['triggered_notifications'].append(notification)
                    self._save_tracking()

                    return notification

        return None

    def get_active_monitors(self) -> List[Dict[str, Any]]:
        """Get all active sniper comments being monitored."""
        return [
            c for c in self.tracking['deployed_comments']
            if c['status'] == 'monitoring'
        ]

    def get_triggered_notifications(self, unread_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get notifications where OP asked for link.

        Args:
            unread_only: Only get unread notifications

        Returns:
            List of high-priority notifications
        """
        notifications = self.tracking['triggered_notifications']

        if unread_only:
            notifications = [n for n in notifications if not n.get('read', False)]

        return sorted(notifications, key=lambda x: x['detected_at'], reverse=True)

    def mark_notification_read(self, notification_id: str):
        """Mark a notification as read/handled."""
        for notif in self.tracking['triggered_notifications']:
            if notif.get('post_id') == notification_id:
                notif['read'] = True
                notif['handled_at'] = datetime.now().isoformat()

        self._save_tracking()


# Example usage
if __name__ == "__main__":
    sniper = SniperStrategy()

    # Example: Generate sniper reply
    post = {
        'title': 'Anyone struggling with meeting notes?',
        'body': 'I can never type fast enough...'
    }

    reply = sniper.generate_sniper_reply(
        post=post,
        product_name='Reso',
        key_benefit='9.26x real-time speed'
    )

    print("📝 Sniper Reply Template:")
    print(reply['reply_text'])
    print(f"\n🎯 Watching for: {', '.join(reply['triggers'][:5])}")
    print(f"\n💬 Follow-up template:\n{reply['follow_up_template']}")
