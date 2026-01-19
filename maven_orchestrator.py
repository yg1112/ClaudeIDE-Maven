#!/usr/bin/env python3
"""
Maven Orchestrator - Automated Marketing Workflow
=================================================

This orchestrates the complete marketing workflow:
1. Find opportunities (scripted)
2. Filter and score (scripted)
3. Check duplicates (scripted)
4. Generate replies (Claude API)
5. Apply sniper strategy (scripted)
6. Pace actions (scripted)
7. Monitor triggers (scripted)

ONLY the final reply generation uses Claude API for quality.
Everything else is scripted to save costs.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List

# Add Maven to path
sys.path.insert(0, str(Path(__file__).parent))

from reddit_client import RedditClient
from post_finder import PostFinder
from reply_generator import ReplyGenerator
from duplicate_detector import DuplicateDetector
from sniper_strategy import SniperStrategy
from pacing_engine import PacingEngine


class MavenOrchestrator:
    """
    Complete automated marketing workflow.
    """

    def __init__(
        self,
        config_dir: str = "config",
        data_dir: str = "data",
        dry_run: bool = True
    ):
        """Initialize orchestrator."""
        self.dry_run = dry_run
        self.config_dir = config_dir
        self.data_dir = data_dir

        # Initialize components
        print("🚀 Initializing Maven Orchestrator...")

        self.reddit = RedditClient(f"{config_dir}/reddit.yaml")
        self.finder = PostFinder(f"{config_dir}/product.yaml", f"{config_dir}/reddit.yaml")
        self.generator = ReplyGenerator(f"{config_dir}/product.yaml", f"{config_dir}/personas.yaml")
        self.duplicate_detector = DuplicateDetector(similarity_threshold=0.6)
        self.sniper = SniperStrategy(f"{data_dir}/sniper_tracking.json")
        self.pacing = PacingEngine(f"{data_dir}/pacing_state.json")

        print("✅ All components ready\n")

    def run_guerrilla_marketing(
        self,
        subreddits: List[str],
        max_replies: int = 3,
        use_sniper_strategy: bool = True
    ) -> Dict[str, Any]:
        """
        Complete guerrilla marketing workflow.

        Args:
            subreddits: Target subreddits
            max_replies: Maximum replies to generate
            use_sniper_strategy: Use two-step sniper approach

        Returns:
            Results summary
        """
        print("=" * 70)
        print("🎯 GUERRILLA MARKETING WORKFLOW")
        print("=" * 70)

        results = {
            'posts_searched': 0,
            'posts_filtered': 0,
            'duplicates_avoided': 0,
            'replies_queued': 0,
            'replies_posted': 0,
            'sniper_deployed': 0,
            'cost_saved': 0
        }

        # STEP 1: Find opportunities (SCRIPTED - FREE)
        print("\n📡 STEP 1: Finding opportunities...")
        all_posts = self._search_posts_scripted(subreddits)
        results['posts_searched'] = len(all_posts)
        print(f"   Found: {len(all_posts)} posts")

        # STEP 2: Filter and score (SCRIPTED - FREE)
        print("\n🔍 STEP 2: Filtering with heuristics...")
        filtered = self.finder.filter_posts(all_posts)
        high_quality = filtered['for_llm'][:max_replies * 2]  # Get 2x to account for duplicates
        results['posts_filtered'] = len(high_quality)
        results['cost_saved'] = len(filtered['skipped'])
        print(f"   High quality: {len(high_quality)} posts")
        print(f"   💰 Saved: {results['cost_saved']} LLM calls")

        # STEP 3: Process each opportunity
        print("\n🎯 STEP 3: Processing opportunities...")

        replies_generated = 0

        for post in high_quality:
            if replies_generated >= max_replies:
                break

            # Check pacing
            can_post = self.pacing.can_post_now(post['subreddit'])
            if not can_post['can_post']:
                print(f"\n⏸️  Pacing limit: {can_post['reason']}")
                # Queue for later
                self.pacing.queue_action({
                    'type': 'comment',
                    'subreddit': post['subreddit'],
                    'post_id': post['id'],
                    'post_data': post,
                    'priority': 3
                })
                continue

            # Get post with comments (SCRIPTED - FREE)
            full_post = self.reddit.get_post_with_comments(post['url'])
            comments = full_post.get('comments', [])

            print(f"\n  Processing: {post['title'][:60]}...")
            print(f"  Subreddit: r/{post['subreddit']} | Comments: {len(comments)}")

            # STEP 3A: Check for duplicates (SCRIPTED - FREE)
            # First, generate a draft reply to check
            # (We'll use a template here to avoid LLM cost for checking)
            draft_points = self._extract_our_key_points(post)

            duplicate_check = self.duplicate_detector.is_duplicate(
                ' '.join(draft_points),
                comments
            )

            if duplicate_check['is_duplicate']:
                print(f"  ❌ Skipped: {duplicate_check['reason']}")
                results['duplicates_avoided'] += 1
                continue

            # Get unique angles
            unique_angles = self.duplicate_detector.suggest_unique_angle(
                comments,
                post
            )
            print(f"  💡 Unique angles: {', '.join(unique_angles[:2])}")

            # STEP 3B: Generate reply (CLAUDE API - $$$ BUT HIGH QUALITY)
            print(f"  🤖 Generating reply with Claude...")

            # Choose persona
            persona = self.generator.select_persona(
                self.finder.categorize_post(post),
                post['subreddit']
            )

            # Generate prompt
            prompt = self.generator.generate_reply_prompt(
                post=post,
                post_category=self.finder.categorize_post(post),
                existing_comments=comments,
                persona=persona
            )

            # TODO: Call Claude API here
            # For now, placeholder
            reply_text = "[CLAUDE API CALL WOULD GO HERE]"
            print(f"  ✅ Reply generated ({len(reply_text)} chars)")

            # Validate reply
            validation = self.generator.post_process_reply(
                reply_text,
                post,
                comments
            )

            if not validation['should_post']:
                print(f"  ⚠️  Validation failed: {validation['reason']}")
                continue

            if validation['warnings']:
                print(f"  ⚠️  Warnings: {', '.join(validation['warnings'])}")

            # STEP 3C: Apply sniper strategy (SCRIPTED - FREE)
            if use_sniper_strategy:
                print(f"  🎯 Applying sniper strategy (two-step)...")

                # Generate sniper version (without product link)
                sniper_reply = self._convert_to_sniper(reply_text)

                # Deploy sniper comment (DRY RUN)
                if self.dry_run:
                    print(f"  📝 [DRY RUN] Would post sniper comment")
                    print(f"     (monitoring for OP asking for link)")
                else:
                    # Actually post
                    comment_id = self.reddit.reply_to_post(
                        post['id'],
                        sniper_reply,
                        dry_run=False
                    )

                    # Track for monitoring
                    self.sniper.deploy_sniper_comment(
                        post_id=post['id'],
                        comment_id=comment_id,
                        comment_text=sniper_reply,
                        subreddit=post['subreddit'],
                        triggers=['what app', 'which tool', 'link?', 'what do you use']
                    )

                    print(f"  ✅ Sniper deployed: {comment_id}")
                    results['sniper_deployed'] += 1

                    # Record action for pacing
                    self.pacing.record_action(post['subreddit'], 'comment')

                replies_generated += 1

            else:
                # Standard reply (not sniper)
                if self.dry_run:
                    print(f"  📝 [DRY RUN] Would post standard reply")
                else:
                    comment_id = self.reddit.reply_to_post(
                        post['id'],
                        reply_text,
                        dry_run=False
                    )
                    print(f"  ✅ Posted: {comment_id}")
                    self.pacing.record_action(post['subreddit'], 'comment')

                replies_generated += 1

        results['replies_queued'] = replies_generated

        # Summary
        print("\n" + "=" * 70)
        print("📊 WORKFLOW SUMMARY")
        print("=" * 70)
        print(f"Posts searched: {results['posts_searched']}")
        print(f"High quality: {results['posts_filtered']}")
        print(f"Duplicates avoided: {results['duplicates_avoided']}")
        print(f"Replies generated: {results['replies_queued']}")
        print(f"Sniper deployed: {results['sniper_deployed']}")
        print(f"💰 Cost saved: {results['cost_saved']} LLM calls")

        return results

    def monitor_sniper_triggers(self) -> Dict[str, Any]:
        """
        Monitor deployed sniper comments for OP asking for link.

        This is SCRIPTED (no LLM cost).
        """
        print("=" * 70)
        print("👀 MONITORING SNIPER TRIGGERS")
        print("=" * 70)

        active_monitors = self.sniper.get_active_monitors()

        print(f"\nActive sniper comments: {len(active_monitors)}")

        notifications = []

        for monitor in active_monitors:
            post_id = monitor['post_id']

            # Get current comments
            full_post = self.reddit.get_post_with_comments(
                f"https://reddit.com/comments/{post_id}"
            )
            current_comments = full_post.get('comments', [])

            # Check for triggers
            notification = self.sniper.check_for_triggers(post_id, current_comments)

            if notification:
                print(f"\n🔔 TRIGGER DETECTED!")
                print(f"   Post: {post_id}")
                print(f"   Trigger word: {notification['trigger_word']}")
                print(f"   OP said: {notification['op_comment']['body'][:100]}...")
                print(f"\n   ⚡ ACTION NEEDED: Send follow-up with link!")

                notifications.append(notification)

        if not notifications:
            print("\n✅ No triggers detected (OP hasn't asked for link yet)")

        return {
            'active_monitors': len(active_monitors),
            'triggers_detected': len(notifications),
            'notifications': notifications
        }

    def _search_posts_scripted(self, subreddits: List[str]) -> List[Dict[str, Any]]:
        """Search posts using scripted Reddit API (FREE)."""
        all_posts = []

        # Get keywords from config
        import yaml
        with open(f"{self.config_dir}/product.yaml") as f:
            config = yaml.safe_load(f)

        keywords = config.get('search_keywords', {}).get('primary', [])

        for subreddit in subreddits:
            for keyword in keywords[:3]:  # Limit keywords
                posts = self.reddit.search_posts(
                    subreddit,
                    keyword,
                    time_filter='week',
                    limit=10
                )
                all_posts.extend(posts)

        # Deduplicate
        seen = set()
        unique = []
        for post in all_posts:
            if post['id'] not in seen:
                seen.add(post['id'])
                unique.append(post)

        return unique

    def _extract_our_key_points(self, post: Dict[str, Any]) -> List[str]:
        """Extract key points we would mention (for duplicate checking)."""
        # This is a simple heuristic
        points = [
            "local processing",
            "privacy first",
            "fast speed",
            "offline capable",
            "one-time cost"
        ]
        return points

    def _convert_to_sniper(self, original_reply: str) -> str:
        """
        Convert a standard reply to sniper version (no product name/link).

        Replace product mentions with generic descriptions.
        """
        # TODO: Implement actual conversion
        # For now, return template
        return """I had the same issue! Here's what worked for me:

Used a local transcription approach instead of cloud services.
The speed difference was huge - went from 50 minutes to ~6 minutes
for a 1-hour meeting.

Key was finding something optimized for Apple Silicon.
Privacy is better too since nothing leaves the machine.

Totally changed my meeting workflow."""


# Command-line interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Maven Orchestrator')
    parser.add_argument('command', choices=['guerrilla', 'monitor'])
    parser.add_argument('--subreddits', default='productivity,macapps')
    parser.add_argument('--max-replies', type=int, default=3)
    parser.add_argument('--dry-run', action='store_true', default=True)
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--sniper', action='store_true', default=True,
                       help='Use sniper strategy (two-step)')

    args = parser.parse_args()

    orchestrator = MavenOrchestrator(
        dry_run=not args.live
    )

    if args.command == 'guerrilla':
        subreddits = args.subreddits.split(',')
        orchestrator.run_guerrilla_marketing(
            subreddits=subreddits,
            max_replies=args.max_replies,
            use_sniper_strategy=args.sniper
        )

    elif args.command == 'monitor':
        orchestrator.monitor_sniper_triggers()
