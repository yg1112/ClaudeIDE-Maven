#!/usr/bin/env python3
"""
Pacing Engine - Rate limiting to avoid shadowban
================================================

Ensures all Reddit actions are paced properly to look human.
"""

import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional


class PacingEngine:
    """
    Rate limiting engine to avoid Reddit shadowban.

    Rules:
    - Max 1 action per X minutes (configurable)
    - Random delays (10-30 minutes by default)
    - Daily limits per subreddit
    - Cooldown after consecutive actions
    """

    def __init__(self, state_file: str = "data/pacing_state.json"):
        """Initialize pacing engine."""
        self.state_file = state_file
        self.state = self._load_state()

        # Configuration
        self.min_delay_minutes = 10  # Minimum 10 minutes between actions
        self.max_delay_minutes = 30  # Maximum 30 minutes
        self.max_daily_per_subreddit = 5  # Max 5 posts per subreddit per day
        self.consecutive_cooldown_minutes = 60  # 1 hour cooldown after 3 consecutive

    def _load_state(self) -> Dict:
        """Load pacing state from disk."""
        try:
            with open(self.state_file) as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'last_action_time': None,
                'action_queue': [],
                'daily_counts': {},  # {subreddit_date: count}
                'consecutive_count': 0
            }

    def _save_state(self):
        """Save pacing state to disk."""
        Path(self.state_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def can_post_now(self, subreddit: str) -> Dict[str, Any]:
        """
        Check if we can post now.

        Returns:
            {
                'can_post': bool,
                'reason': str,
                'wait_seconds': int,
                'next_available': str (ISO timestamp)
            }
        """
        now = datetime.now()

        # Check daily limit
        today = now.strftime('%Y-%m-%d')
        key = f"{subreddit}_{today}"
        daily_count = self.state['daily_counts'].get(key, 0)

        if daily_count >= self.max_daily_per_subreddit:
            return {
                'can_post': False,
                'reason': f'Daily limit reached for r/{subreddit} ({daily_count}/{self.max_daily_per_subreddit})',
                'wait_seconds': None,
                'next_available': (now + timedelta(days=1)).replace(hour=0, minute=0).isoformat()
            }

        # Check time since last action
        if self.state['last_action_time']:
            last_time = datetime.fromisoformat(self.state['last_action_time'])
            elapsed_minutes = (now - last_time).total_seconds() / 60

            required_delay = self.min_delay_minutes

            # Increase delay if consecutive actions
            if self.state['consecutive_count'] >= 3:
                required_delay = self.consecutive_cooldown_minutes

            if elapsed_minutes < required_delay:
                wait_seconds = int((required_delay - elapsed_minutes) * 60)
                next_time = last_time + timedelta(minutes=required_delay)

                return {
                    'can_post': False,
                    'reason': f'Too soon (need {required_delay} min, only {elapsed_minutes:.1f} min passed)',
                    'wait_seconds': wait_seconds,
                    'next_available': next_time.isoformat()
                }

        # Can post!
        return {
            'can_post': True,
            'reason': 'Ready to post',
            'wait_seconds': 0,
            'next_available': now.isoformat()
        }

    def record_action(self, subreddit: str, action_type: str = 'post'):
        """
        Record an action (post/comment).

        Args:
            subreddit: The subreddit posted to
            action_type: 'post' or 'comment'
        """
        now = datetime.now()

        # Update last action time
        self.state['last_action_time'] = now.isoformat()

        # Update daily count
        today = now.strftime('%Y-%m-%d')
        key = f"{subreddit}_{today}"
        self.state['daily_counts'][key] = self.state['daily_counts'].get(key, 0) + 1

        # Update consecutive count
        self.state['consecutive_count'] += 1

        # Clean old daily counts (keep only last 7 days)
        cutoff = (now - timedelta(days=7)).strftime('%Y-%m-%d')
        self.state['daily_counts'] = {
            k: v for k, v in self.state['daily_counts'].items()
            if k.split('_')[1] >= cutoff
        }

        self._save_state()

        print(f"✅ Action recorded: r/{subreddit} at {now.strftime('%H:%M:%S')}")
        print(f"   Daily count: {self.state['daily_counts'][key]}/{self.max_daily_per_subreddit}")
        print(f"   Consecutive: {self.state['consecutive_count']}")

    def reset_consecutive(self):
        """Reset consecutive counter (call when taking a break)."""
        self.state['consecutive_count'] = 0
        self._save_state()
        print("🔄 Consecutive counter reset")

    def get_recommended_delay(self) -> int:
        """
        Get recommended delay in seconds before next action.

        Returns human-like random delay.
        """
        # Random delay between min and max
        delay_minutes = random.randint(self.min_delay_minutes, self.max_delay_minutes)

        # Add some randomness (±20%)
        variance = delay_minutes * 0.2
        delay_minutes += random.uniform(-variance, variance)

        return int(delay_minutes * 60)

    def queue_action(self, action: Dict[str, Any]):
        """
        Add action to queue.

        Args:
            action: {
                'type': 'post' or 'comment',
                'subreddit': str,
                'content': str,
                'post_id': str (if comment),
                'priority': int (1-5, 5=highest)
            }
        """
        action['queued_at'] = datetime.now().isoformat()
        self.state['action_queue'].append(action)
        self._save_state()

        print(f"📥 Action queued: {action['type']} in r/{action['subreddit']}")

    def get_next_action(self) -> Optional[Dict[str, Any]]:
        """
        Get next action from queue (highest priority first).

        Returns None if queue is empty or can't post yet.
        """
        if not self.state['action_queue']:
            return None

        # Sort by priority (highest first)
        self.state['action_queue'].sort(key=lambda x: x.get('priority', 1), reverse=True)

        # Get first action
        action = self.state['action_queue'][0]

        # Check if we can post
        can_post = self.can_post_now(action['subreddit'])

        if not can_post['can_post']:
            print(f"⏳ Can't post yet: {can_post['reason']}")
            if can_post['wait_seconds']:
                print(f"   Wait {can_post['wait_seconds']//60} minutes")
            return None

        # Remove from queue
        self.state['action_queue'].pop(0)
        self._save_state()

        return action

    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status."""
        return {
            'queue_size': len(self.state['action_queue']),
            'actions': self.state['action_queue'],
            'last_action': self.state['last_action_time'],
            'consecutive_count': self.state['consecutive_count']
        }


# Example usage
if __name__ == "__main__":
    engine = PacingEngine()

    # Check if can post
    status = engine.can_post_now('productivity')
    print(f"\nCan post to r/productivity: {status['can_post']}")
    print(f"Reason: {status['reason']}")

    if status['can_post']:
        # Record action
        engine.record_action('productivity', 'comment')

        # Get recommended delay
        delay = engine.get_recommended_delay()
        print(f"\nRecommended delay: {delay//60} minutes")
