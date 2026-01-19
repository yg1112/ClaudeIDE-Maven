#!/usr/bin/env python3
"""
Maven - AI CMO Agent Main Controller
=====================================

This is the brain of Maven. It orchestrates all components and implements
the cost-optimized processing pipeline.

COST OPTIMIZATION STRATEGY:
1. Free tier: Keyword matching, rule-based filtering
2. Cheap tier: Simple heuristics, scoring
3. Expensive tier: LLM only for high-value posts

HUMAN-LIKE BEHAVIOR:
1. Read all context before responding
2. Never repeat what others said
3. Vary response timing and length
4. Match subreddit tone
5. Add genuine value, not just promotion
"""

import json
import yaml
import random
import time
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

# Import Maven components
from reddit_client import RedditClient
from post_finder import PostFinder
from reply_generator import ReplyGenerator
from karma_builder import KarmaBuilder
from market_intelligence import MarketIntelligence
from post_monitor import PostMonitor
from content_generator import ContentGenerator


class Maven:
    """
    Maven CMO Agent - Main Controller
    
    Usage:
        maven = Maven()
        
        # Guerrilla marketing
        maven.guerrilla_marketing(subreddits=['productivity', 'transcription'])
        
        # Build karma
        maven.build_karma(subreddit='learnprogramming')
        
        # Monitor your posts
        maven.monitor_posts()
        
        # Collect market intelligence
        maven.collect_intelligence(competitor='otter.ai')
        
        # Generate launch post
        maven.create_launch_post(subreddit='SideProject')
    """
    
    def __init__(
        self,
        config_dir: str = "config",
        data_dir: str = "data",
        github_repo_path: str = None,
        dry_run: bool = True,  # Safety: don't actually post by default
        llm_callback: Callable = None  # Function to call LLM
    ):
        """
        Initialize Maven.
        
        Args:
            config_dir: Path to config directory
            data_dir: Path to data directory
            github_repo_path: Path to your product's GitHub repo (for context)
            dry_run: If True, don't actually post to Reddit
            llm_callback: Function to call for LLM generations
                         Signature: llm_callback(prompt: str) -> str
        """
        self.config_dir = config_dir
        self.data_dir = data_dir
        self.github_repo_path = github_repo_path
        self.dry_run = dry_run
        self.llm_callback = llm_callback
        
        # Ensure data directory exists
        Path(data_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self._init_components()
        
        # Load product context from GitHub if available
        self.product_context = self._load_github_context()
        
        # Session stats
        self.session_stats = {
            'posts_analyzed': 0,
            'llm_calls': 0,
            'replies_generated': 0,
            'replies_posted': 0,
            'cost_saved_by_filtering': 0
        }
    
    def _init_components(self):
        """Initialize all Maven components."""
        product_config = f"{self.config_dir}/product.yaml"
        reddit_config = f"{self.config_dir}/reddit.yaml"
        personas_config = f"{self.config_dir}/personas.yaml"
        
        self.reddit = RedditClient(reddit_config)
        self.finder = PostFinder(product_config, reddit_config)
        self.generator = ReplyGenerator(product_config, personas_config)
        self.karma = KarmaBuilder(product_config, f"{self.data_dir}/karma_history.json")
        self.intel = MarketIntelligence(product_config, f"{self.data_dir}/market_insights.json")
        self.monitor = PostMonitor(f"{self.data_dir}/monitored_posts.json")
        self.content = ContentGenerator(product_config)
    
    def _load_github_context(self) -> str:
        """Load product context from GitHub repo if available."""
        if not self.github_repo_path:
            return None
        
        context_parts = []
        
        # Look for README
        readme_paths = ['README.md', 'readme.md', 'README.txt']
        for readme in readme_paths:
            path = os.path.join(self.github_repo_path, readme)
            if os.path.exists(path):
                with open(path, 'r') as f:
                    content = f.read()[:5000]  # Limit size
                    context_parts.append(f"# README\n{content}")
                break
        
        # Look for docs
        docs_paths = ['docs', 'documentation', 'doc']
        for docs_dir in docs_paths:
            path = os.path.join(self.github_repo_path, docs_dir)
            if os.path.isdir(path):
                # Read first few doc files
                for i, doc_file in enumerate(os.listdir(path)[:5]):
                    if doc_file.endswith('.md'):
                        with open(os.path.join(path, doc_file), 'r') as f:
                            content = f.read()[:2000]
                            context_parts.append(f"# {doc_file}\n{content}")
                break
        
        return "\n\n---\n\n".join(context_parts) if context_parts else None
    
    def _call_llm(self, prompt: str) -> str:
        """
        Call LLM with the given prompt.
        Tracks usage for cost monitoring.
        """
        self.session_stats['llm_calls'] += 1
        
        if self.llm_callback:
            return self.llm_callback(prompt)
        else:
            # Placeholder - in real usage, this would be replaced
            print(f"[LLM CALL #{self.session_stats['llm_calls']}]")
            print(f"Prompt length: {len(prompt)} chars")
            return "[LLM response would go here]"
    
    # =========================================================================
    # GUERRILLA MARKETING
    # =========================================================================
    
    def guerrilla_marketing(
        self,
        subreddits: List[str],
        max_replies_per_session: int = 5,
        search_queries: List[str] = None
    ) -> Dict[str, Any]:
        """
        Find relevant posts and generate human-like replies.
        
        PIPELINE:
        1. Search Reddit (free API)
        2. Keyword filter (no cost)
        3. Heuristic scoring (no cost)
        4. LLM analysis only for top posts
        5. Generate contextual reply
        6. Human delay before posting
        
        Args:
            subreddits: Subreddits to search
            max_replies_per_session: Limit replies to avoid spam detection
            search_queries: Custom search queries (uses config if None)
        """
        results = {
            'posts_found': 0,
            'posts_filtered': 0,
            'posts_analyzed_by_llm': 0,
            'replies_generated': [],
            'errors': []
        }
        
        # Get search queries from config if not provided
        if not search_queries:
            with open(f"{self.config_dir}/product.yaml", 'r') as f:
                config = yaml.safe_load(f)
            keywords = config.get('search_keywords', {})
            search_queries = (
                keywords.get('primary', []) + 
                keywords.get('pain_points', [])
            )
        
        all_posts = []
        
        # Stage 1: Collect posts (FREE - just API calls)
        print("\n📡 Stage 1: Searching Reddit...")
        for subreddit in subreddits:
            for query in search_queries[:5]:  # Limit queries
                try:
                    posts = self.reddit.search_posts(
                        subreddit=subreddit,
                        query=query,
                        time_filter='week',
                        limit=10
                    )
                    all_posts.extend(posts)
                    print(f"  r/{subreddit} '{query}': {len(posts)} posts")
                except Exception as e:
                    results['errors'].append(f"Search error: {e}")
        
        # Deduplicate by ID
        seen_ids = set()
        unique_posts = []
        for post in all_posts:
            if post['id'] not in seen_ids:
                seen_ids.add(post['id'])
                unique_posts.append(post)
        
        results['posts_found'] = len(unique_posts)
        print(f"  Total unique posts: {len(unique_posts)}")
        self.session_stats['posts_analyzed'] += len(unique_posts)
        
        # Stage 2: Filter posts (FREE - keyword matching)
        print("\n🔍 Stage 2: Filtering posts (no LLM cost)...")
        filtered = self.finder.filter_posts(unique_posts)
        
        results['posts_filtered'] = len(filtered['for_llm'])
        self.session_stats['cost_saved_by_filtering'] += (
            len(filtered['skipped']) + len(filtered['maybe'])
        )
        
        print(f"  For LLM analysis: {len(filtered['for_llm'])}")
        print(f"  Maybe later: {len(filtered['maybe'])}")
        print(f"  Skipped: {len(filtered['skipped'])}")
        print(f"  💰 Saved {len(filtered['skipped'])} LLM calls")
        
        # Stage 3: LLM Analysis for top posts only
        print("\n🧠 Stage 3: LLM analysis for top candidates...")
        
        replies_generated = 0
        
        for post in filtered['for_llm'][:max_replies_per_session]:
            if replies_generated >= max_replies_per_session:
                break
            
            try:
                reply_result = self._process_guerrilla_post(post)
                if reply_result['should_post']:
                    results['replies_generated'].append(reply_result)
                    replies_generated += 1
                    
            except Exception as e:
                results['errors'].append(f"Post {post['id']}: {e}")
        
        results['posts_analyzed_by_llm'] = self.session_stats['llm_calls']
        
        # Print summary
        print("\n" + "="*50)
        print("📊 GUERRILLA MARKETING SESSION SUMMARY")
        print("="*50)
        print(f"Posts searched: {results['posts_found']}")
        print(f"Posts passed filter: {results['posts_filtered']}")
        print(f"LLM calls made: {results['posts_analyzed_by_llm']}")
        print(f"Replies generated: {len(results['replies_generated'])}")
        print(f"Errors: {len(results['errors'])}")
        
        return results
    
    def _process_guerrilla_post(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single post for guerrilla marketing."""
        
        print(f"\n  Processing: {post['title'][:50]}...")
        
        # Get full post with comments for context
        full_post = self.reddit.get_post_with_comments(post['url'])
        comments = full_post.get('comments', [])
        
        # Categorize the post
        category = self.finder.categorize_post(post)
        print(f"    Category: {category}")
        
        # Select persona
        persona = self.generator.select_persona(category, post['subreddit'])
        print(f"    Persona: {persona}")
        
        # Generate reply prompt
        prompt = self.generator.generate_reply_prompt(
            post=post,
            post_category=category,
            existing_comments=comments,
            persona=persona,
            github_context=self.product_context
        )
        
        # Call LLM
        reply_text = self._call_llm(prompt)
        
        # Post-process and validate
        validation = self.generator.post_process_reply(
            reply=reply_text,
            post=post,
            existing_comments=comments
        )
        
        if validation['warnings']:
            print(f"    ⚠️ Warnings: {', '.join(validation['warnings'])}")
        
        # Add human touches
        if validation['should_post']:
            reply_text = self.generator.add_human_touches(validation['text'])
        
        result = {
            'post_id': post['id'],
            'post_url': post['url'],
            'post_title': post['title'],
            'category': category,
            'persona': persona,
            'reply_text': reply_text,
            'should_post': validation['should_post'],
            'validation': validation
        }
        
        # Post if not dry run
        if validation['should_post'] and not self.dry_run:
            print(f"    ⏳ Waiting before posting (human-like delay)...")
            self.reddit.human_delay()
            
            reply_id = self.reddit.reply_to_post(
                post_id=post['id'],
                reply_text=reply_text,
                dry_run=False
            )
            result['reply_id'] = reply_id
            result['posted'] = True
            
            # Record that we replied
            self.finder.save_replied_post(post['id'])
            self.session_stats['replies_posted'] += 1
            
            print(f"    ✅ Posted! Reply ID: {reply_id}")
        else:
            result['posted'] = False
            if self.dry_run:
                print(f"    📝 [DRY RUN] Would post reply")
        
        self.session_stats['replies_generated'] += 1
        
        return result
    
    # =========================================================================
    # KARMA BUILDING
    # =========================================================================
    
    def build_karma(
        self,
        subreddit: str,
        max_replies: int = 3,
        expertise: List[str] = None
    ) -> Dict[str, Any]:
        """
        Build karma by being genuinely helpful (NO product mentions).
        
        Args:
            subreddit: Subreddit to build karma in
            max_replies: Max replies this session
            expertise: Your areas of expertise for better matching
        """
        results = {
            'opportunities_found': 0,
            'replies_generated': [],
            'karma_before': None,
            'errors': []
        }
        
        # Check if we can reply today
        if not self.karma.can_reply_today(subreddit, max_replies):
            print(f"⚠️ Already hit reply limit for r/{subreddit} today")
            return results
        
        # Get current karma
        try:
            results['karma_before'] = self.reddit.get_user_karma()
            print(f"Current karma: {results['karma_before']['total']}")
        except:
            pass
        
        # Get new posts
        print(f"\n📡 Finding karma opportunities in r/{subreddit}...")
        posts = self.reddit.get_new_posts(subreddit, limit=50)
        
        # Find good opportunities
        opportunities = self.karma.find_best_karma_posts(posts, expertise)
        results['opportunities_found'] = len(opportunities)
        
        print(f"Found {len(opportunities)} good opportunities")
        
        # Process top opportunities
        for post in opportunities[:max_replies]:
            try:
                # Generate helpful reply (no product mention)
                prompt = self.karma.generate_karma_reply_prompt(post, expertise)
                reply_text = self._call_llm(prompt)
                
                result = {
                    'post_id': post['id'],
                    'post_title': post['title'],
                    'reply_text': reply_text,
                    'posted': False
                }
                
                if not self.dry_run:
                    self.reddit.human_delay()
                    reply_id = self.reddit.reply_to_post(
                        post_id=post['id'],
                        reply_text=reply_text,
                        dry_run=False
                    )
                    result['reply_id'] = reply_id
                    result['posted'] = True
                    
                    # Record for tracking
                    self.karma.record_reply(
                        subreddit=subreddit,
                        post_id=post['id'],
                        reply_id=reply_id,
                        reply_type='karma_building'
                    )
                
                results['replies_generated'].append(result)
                print(f"  ✅ Generated reply for: {post['title'][:40]}...")
                
            except Exception as e:
                results['errors'].append(str(e))
        
        return results
    
    # =========================================================================
    # POST MONITORING (Defend your posts)
    # =========================================================================
    
    def monitor_posts(self) -> Dict[str, Any]:
        """
        Check monitored posts for new comments needing response.
        """
        results = {
            'posts_checked': 0,
            'new_comments': 0,
            'responses_needed': [],
            'responses_generated': []
        }
        
        status = self.monitor.get_monitoring_status()
        print(f"\n👀 Checking {status['total_monitored']} monitored posts...")
        
        for post_info in status['posts']:
            post_url = post_info['url']
            
            try:
                # Get current state
                current = self.reddit.get_post_with_comments(post_url)
                comments = current.get('comments', [])
                
                # Find new comments
                new_comments = self.monitor.check_for_new_comments(post_url, comments)
                results['posts_checked'] += 1
                results['new_comments'] += len(new_comments)
                
                if not new_comments:
                    continue
                
                print(f"\n  📬 {len(new_comments)} new comments on: {current['title'][:40]}...")
                
                # Analyze each new comment
                for comment in new_comments:
                    analysis = self.monitor.analyze_comment(comment)
                    
                    if analysis['needs_response']:
                        results['responses_needed'].append({
                            'post_url': post_url,
                            'comment': comment,
                            'analysis': analysis
                        })
                        
            except Exception as e:
                print(f"  ❌ Error checking {post_url}: {e}")
        
        # Prioritize responses
        if results['responses_needed']:
            prioritized = self.monitor.prioritize_responses([
                (r['comment'], r['analysis']) 
                for r in results['responses_needed']
            ])
            
            print(f"\n📝 {len(prioritized)} comments need response")
            
            for comment, analysis in prioritized[:3]:  # Limit per session
                strategy = self.monitor.generate_defense_strategy(comment, analysis)
                
                # Generate response
                prompt = self.generator.generate_defense_reply_prompt(
                    original_post=current,
                    comment_to_reply=comment,
                    is_criticism=(analysis['response_type'] == 'criticism')
                )
                
                reply_text = self._call_llm(prompt)
                
                result = {
                    'comment_id': comment['id'],
                    'response_type': analysis['response_type'],
                    'reply_text': reply_text,
                    'posted': False
                }
                
                if not self.dry_run:
                    self.reddit.human_delay()
                    reply_id = self.reddit.reply_to_comment(
                        comment_id=comment['id'],
                        reply_text=reply_text,
                        dry_run=False
                    )
                    result['reply_id'] = reply_id
                    result['posted'] = True
                
                results['responses_generated'].append(result)
        
        return results
    
    def add_post_to_monitor(self, post_url: str):
        """Add a post to monitoring."""
        self.monitor.add_post(post_url)
        print(f"✅ Now monitoring: {post_url}")
    
    # =========================================================================
    # MARKET INTELLIGENCE
    # =========================================================================
    
    def collect_intelligence(
        self,
        competitor: str = None,
        subreddits: List[str] = None,
        days_back: int = 7
    ) -> Dict[str, Any]:
        """
        Collect market intelligence about competitors and opportunities.
        
        Args:
            competitor: Specific competitor to research
            subreddits: Subreddits to search (uses config if None)
            days_back: How far back to search
        """
        results = {
            'posts_analyzed': 0,
            'insights': [],
            'report': None
        }
        
        # Get subreddits from config
        if not subreddits:
            with open(f"{self.config_dir}/product.yaml", 'r') as f:
                config = yaml.safe_load(f)
            subreddits = config.get('target_subreddits', {}).get('primary', [])
        
        print(f"\n🔍 Collecting market intelligence...")
        
        # Search for competitor mentions
        all_posts = []
        search_terms = [competitor] if competitor else []
        
        # Add competitor names from config
        with open(f"{self.config_dir}/product.yaml", 'r') as f:
            config = yaml.safe_load(f)
        for c in config['product'].get('competitors', []):
            search_terms.append(c['name'])
        
        for subreddit in subreddits:
            for term in search_terms[:3]:
                posts = self.reddit.search_posts(
                    subreddit=subreddit,
                    query=term,
                    time_filter='month',
                    limit=20
                )
                all_posts.extend(posts)
        
        print(f"  Found {len(all_posts)} posts to analyze")
        
        # Analyze posts (no LLM needed - rule-based)
        analyses = []
        for post in all_posts:
            analysis = self.intel.analyze_post(post)
            analyses.append(analysis)
            self.intel.save_analysis(analysis)
        
        results['posts_analyzed'] = len(analyses)
        
        # Aggregate insights
        aggregated = self.intel.aggregate_insights(analyses)
        results['insights'] = aggregated['actionable_insights']
        
        # Generate report using LLM
        report_prompt = self.intel.generate_report_prompt(aggregated)
        report = self._call_llm(report_prompt)
        results['report'] = report
        
        # Print summary
        print("\n" + "="*50)
        print("📊 MARKET INTELLIGENCE SUMMARY")
        print("="*50)
        for insight in results['insights']:
            print(f"  {insight}")
        
        return results
    
    # =========================================================================
    # CONTENT CREATION
    # =========================================================================
    
    def create_launch_post(
        self,
        subreddit: str,
        angle: str = "problem_solution"
    ) -> Dict[str, Any]:
        """
        Generate a product launch post.
        
        Args:
            subreddit: Target subreddit
            angle: Post angle (problem_solution, show_hn_style, personal_journey, comparison)
        """
        print(f"\n✍️ Creating launch post for r/{subreddit}...")
        
        # Get subreddit guidelines
        guidelines = self.content.get_subreddit_guidelines(subreddit)
        print(f"  Guidelines: {guidelines}")
        
        # Generate prompt
        prompt = self.content.generate_launch_post_prompt(
            subreddit=subreddit,
            angle=angle,
            github_docs=self.product_context
        )
        
        # Generate content
        content = self._call_llm(prompt)
        
        # Parse title and body (assuming LLM outputs them labeled)
        # This is simplified - real implementation would parse more carefully
        
        result = {
            'subreddit': subreddit,
            'angle': angle,
            'content': content,
            'guidelines': guidelines
        }
        
        return result
    
    # =========================================================================
    # SCHEDULER
    # =========================================================================
    
    def run_daily_routine(self):
        """
        Run the daily Maven routine.
        
        Schedule:
        1. Check monitored posts for new comments
        2. Build some karma (early morning is good)
        3. Guerrilla marketing (afternoon)
        4. Collect any new intelligence
        """
        print("\n" + "="*60)
        print("🚀 MAVEN DAILY ROUTINE")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*60)
        
        # 1. Monitor posts
        print("\n\n📌 TASK 1: Checking monitored posts...")
        monitor_results = self.monitor_posts()
        
        # 2. Build karma (if not too much activity already)
        print("\n\n🏆 TASK 2: Building karma...")
        karma_results = self.build_karma(
            subreddit='learnprogramming',  # Would come from config
            max_replies=2
        )
        
        # 3. Guerrilla marketing
        print("\n\n🎯 TASK 3: Guerrilla marketing...")
        guerrilla_results = self.guerrilla_marketing(
            subreddits=['productivity', 'transcription'],  # Would come from config
            max_replies_per_session=3
        )
        
        # 4. Intelligence (weekly, not daily)
        # if datetime.now().weekday() == 0:  # Monday
        #     intel_results = self.collect_intelligence()
        
        # Summary
        print("\n\n" + "="*60)
        print("📊 DAILY ROUTINE COMPLETE")
        print("="*60)
        print(f"Monitored posts checked: {monitor_results['posts_checked']}")
        print(f"Karma replies: {len(karma_results['replies_generated'])}")
        print(f"Marketing replies: {len(guerrilla_results['replies_generated'])}")
        print(f"Total LLM calls: {self.session_stats['llm_calls']}")
        print(f"Cost saved by filtering: {self.session_stats['cost_saved_by_filtering']} posts")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get stats for current session."""
        return self.session_stats


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """Command-line interface for Maven."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Maven - AI CMO Agent')
    parser.add_argument('command', choices=[
        'guerrilla', 'karma', 'monitor', 'intel', 'launch', 'daily'
    ])
    parser.add_argument('--subreddit', '-s', help='Target subreddit')
    parser.add_argument('--dry-run', action='store_true', default=True)
    parser.add_argument('--live', action='store_true', help='Actually post (disable dry run)')
    
    args = parser.parse_args()
    
    dry_run = not args.live
    maven = Maven(dry_run=dry_run)
    
    if args.command == 'guerrilla':
        subs = [args.subreddit] if args.subreddit else ['productivity']
        maven.guerrilla_marketing(subreddits=subs)
    
    elif args.command == 'karma':
        sub = args.subreddit or 'learnprogramming'
        maven.build_karma(subreddit=sub)
    
    elif args.command == 'monitor':
        maven.monitor_posts()
    
    elif args.command == 'intel':
        maven.collect_intelligence()
    
    elif args.command == 'launch':
        sub = args.subreddit or 'SideProject'
        result = maven.create_launch_post(subreddit=sub)
        print("\n" + "="*50)
        print("GENERATED LAUNCH POST")
        print("="*50)
        print(result['content'])
    
    elif args.command == 'daily':
        maven.run_daily_routine()


if __name__ == "__main__":
    main()
