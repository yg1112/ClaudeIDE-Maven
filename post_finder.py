#!/usr/bin/env python3
"""
Post Finder for Maven
Finds relevant posts using smart filtering to minimize LLM costs
"""

import re
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict

class PostFinder:
    """
    Smart post finder with multi-stage filtering:
    1. Keyword matching (free)
    2. Heuristic scoring (free)
    3. LLM analysis (only for top candidates)
    """
    
    def __init__(
        self,
        product_config_path: str = "config/product.yaml",
        reddit_config_path: str = "config/reddit.yaml",
        replied_posts_path: str = "data/replied_posts.json"
    ):
        self.product_config = self._load_yaml(product_config_path)
        self.reddit_config = self._load_yaml(reddit_config_path)
        self.replied_posts = self._load_replied_posts(replied_posts_path)
        self.replied_posts_path = replied_posts_path
        
        # Build keyword sets for fast matching
        self._build_keyword_sets()
    
    def _load_yaml(self, path: str) -> dict:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    def _load_replied_posts(self, path: str) -> set:
        """Load set of post IDs we've already replied to."""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                return set(data.get('replied_ids', []))
        except FileNotFoundError:
            return set()
    
    def save_replied_post(self, post_id: str):
        """Mark a post as replied to."""
        self.replied_posts.add(post_id)
        Path(self.replied_posts_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.replied_posts_path, 'w') as f:
            json.dump({
                'replied_ids': list(self.replied_posts),
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
    
    def _build_keyword_sets(self):
        """Pre-compute keyword patterns for fast matching."""
        keywords = self.product_config.get('search_keywords', {})
        
        self.primary_keywords = set(
            kw.lower() for kw in keywords.get('primary', [])
        )
        self.pain_point_keywords = set(
            kw.lower() for kw in keywords.get('pain_points', [])
        )
        self.competitor_keywords = set(
            kw.lower() for kw in keywords.get('competitor_mentions', [])
        )
        
        # High-value signals that strongly indicate relevance
        self.high_value_patterns = [
            r'\balternative\s+to\b',
            r'\bbetter\s+than\b',
            r'\brecommend(ation)?s?\b',
            r'\blooking\s+for\b',
            r'\bwhat\s+do\s+you\s+use\b',
            r'\bany(one)?\s+(know|suggest|recommend)\b',
            r'\bhelp\s+(me\s+)?find\b',
            r'\bswitch(ing)?\s+from\b',
            r'\bfrustrat(ed|ing)\b',
            r'\bexpensive\b',
            r'\bfree\s+(alternative|option|tool)\b',
        ]
        self.high_value_regex = re.compile(
            '|'.join(self.high_value_patterns), 
            re.IGNORECASE
        )
    
    def filter_posts(
        self,
        posts: List[Dict[str, Any]],
        max_for_llm: int = 10
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Filter posts through multiple stages.
        
        Returns:
            {
                'for_llm': [...],      # Top candidates for LLM analysis
                'maybe': [...],         # Could be relevant, lower priority
                'skipped': [...]        # Filtered out
            }
        """
        results = {
            'for_llm': [],
            'maybe': [],
            'skipped': []
        }
        
        optimization = self.reddit_config.get('optimization', {})
        min_score = optimization.get('min_post_score', 2)
        max_age = optimization.get('max_post_age_hours', 72)
        relevance_threshold = optimization.get('relevance_threshold', 30)
        
        scored_posts = []
        
        for post in posts:
            # Skip if already replied
            if post['id'] in self.replied_posts:
                results['skipped'].append({
                    **post, 
                    'skip_reason': 'already_replied'
                })
                continue
            
            # Basic filters
            if post['score'] < min_score:
                results['skipped'].append({
                    **post, 
                    'skip_reason': f'low_score ({post["score"]} < {min_score})'
                })
                continue
                
            if post.get('age_hours', 0) > max_age:
                results['skipped'].append({
                    **post, 
                    'skip_reason': f'too_old ({post["age_hours"]:.0f}h > {max_age}h)'
                })
                continue
            
            # Calculate relevance score
            score, reasons = self._calculate_relevance(post)
            post['relevance_score'] = score
            post['relevance_reasons'] = reasons
            
            if score < relevance_threshold:
                results['skipped'].append({
                    **post, 
                    'skip_reason': f'low_relevance ({score} < {relevance_threshold})'
                })
                continue
            
            scored_posts.append(post)
        
        # Sort by relevance and split
        scored_posts.sort(key=lambda p: p['relevance_score'], reverse=True)
        
        results['for_llm'] = scored_posts[:max_for_llm]
        results['maybe'] = scored_posts[max_for_llm:]
        
        return results
    
    def _calculate_relevance(
        self, 
        post: Dict[str, Any]
    ) -> tuple[int, List[str]]:
        """
        Calculate relevance score (0-100) using heuristics.
        No LLM calls - pure keyword/pattern matching.
        """
        score = 0
        reasons = []
        
        text = f"{post['title']} {post['body']}".lower()
        
        # Primary keyword matches (+15 each, max 30)
        primary_matches = sum(1 for kw in self.primary_keywords if kw in text)
        if primary_matches:
            points = min(primary_matches * 15, 30)
            score += points
            reasons.append(f"primary_keywords: +{points}")
        
        # Pain point keywords (+20 each, max 40)
        pain_matches = sum(1 for kw in self.pain_point_keywords if kw in text)
        if pain_matches:
            points = min(pain_matches * 20, 40)
            score += points
            reasons.append(f"pain_point_keywords: +{points}")
        
        # Competitor mentions (+25)
        competitor_matches = sum(1 for kw in self.competitor_keywords if kw in text)
        if competitor_matches:
            score += 25
            reasons.append("competitor_mention: +25")
        
        # High-value patterns (+20)
        if self.high_value_regex.search(text):
            score += 20
            reasons.append("high_value_pattern: +20")
        
        # Question indicators (+10)
        if '?' in post['title'] or text.startswith(('how ', 'what ', 'which ', 'any ')):
            score += 10
            reasons.append("question_format: +10")
        
        # Engagement bonus (more comments = more visibility)
        if post['num_comments'] >= 10:
            score += 10
            reasons.append("high_engagement: +10")
        elif post['num_comments'] >= 5:
            score += 5
            reasons.append("medium_engagement: +5")
        
        # Freshness bonus
        age = post.get('age_hours', 24)
        if age < 6:
            score += 15
            reasons.append("very_fresh: +15")
        elif age < 24:
            score += 10
            reasons.append("fresh: +10")
        
        # Cap at 100
        score = min(score, 100)
        
        return score, reasons
    
    def categorize_post(self, post: Dict[str, Any]) -> str:
        """
        Categorize a post to determine reply strategy.
        
        Categories:
        - 'competitor_complaint': Complaining about a competitor
        - 'recommendation_request': Asking for recommendations
        - 'technical_question': Technical how-to question
        - 'general_discussion': General discussion
        """
        text = f"{post['title']} {post['body']}".lower()
        
        # Check for competitor complaints
        complaint_words = ['hate', 'terrible', 'awful', 'expensive', 'broken', 
                         'doesn\'t work', 'stopped working', 'frustrated', 'annoying']
        has_competitor = any(c in text for c in self.competitor_keywords)
        has_complaint = any(w in text for w in complaint_words)
        
        if has_competitor and has_complaint:
            return 'competitor_complaint'
        
        # Check for recommendation requests
        rec_patterns = [
            r'recommend',
            r'looking for',
            r'suggest(ion)?',
            r'what (do you|should I) use',
            r'best (tool|app|software)',
            r'alternative to',
        ]
        if any(re.search(p, text) for p in rec_patterns):
            return 'recommendation_request'
        
        # Check for technical questions
        tech_patterns = [
            r'how (do|can|to)',
            r'is (it|there) (a way|possible)',
            r'help with',
            r'issue with',
            r'problem with',
        ]
        if any(re.search(p, text) for p in tech_patterns):
            return 'technical_question'
        
        return 'general_discussion'
    
    def find_karma_opportunities(
        self, 
        posts: List[Dict[str, Any]],
        user_skills: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find posts good for karma building (not product related).
        
        Looks for:
        - Unanswered technical questions
        - Simple questions with easy answers
        - Posts asking for help
        """
        opportunities = []
        
        for post in posts:
            if post['id'] in self.replied_posts:
                continue
                
            text = f"{post['title']} {post['body']}".lower()
            
            # Skip if it's about our keywords (save for guerrilla marketing)
            if any(kw in text for kw in self.primary_keywords):
                continue
            
            # Look for questions we can answer
            is_question = '?' in post['title'] or any(
                text.startswith(w) for w in ['how', 'what', 'why', 'can', 'is']
            )
            
            # Prefer posts with few comments (opportunity to be helpful)
            few_comments = post['num_comments'] < 5
            
            # Fresh posts
            is_fresh = post.get('age_hours', 100) < 24
            
            if is_question and few_comments and is_fresh:
                post['karma_score'] = self._karma_opportunity_score(post)
                opportunities.append(post)
        
        # Sort by karma opportunity
        opportunities.sort(key=lambda p: p['karma_score'], reverse=True)
        
        return opportunities[:10]  # Top 10 opportunities
    
    def _karma_opportunity_score(self, post: Dict[str, Any]) -> int:
        """Score a post for karma-building potential."""
        score = 50  # Base score
        
        # Fewer comments = more opportunity
        score += max(0, 20 - post['num_comments'] * 4)
        
        # Higher engagement potential
        score += min(post['score'] * 2, 20)
        
        # Freshness
        age = post.get('age_hours', 24)
        score += max(0, 30 - age)
        
        return score


# Example usage
if __name__ == "__main__":
    finder = PostFinder()
    
    # Example posts (would come from RedditClient)
    sample_posts = [
        {
            'id': '1',
            'title': 'Looking for a free transcription alternative to Otter.ai',
            'body': 'Otter is getting too expensive for me. Any recommendations?',
            'score': 15,
            'num_comments': 8,
            'age_hours': 12,
        },
        {
            'id': '2', 
            'title': 'How to convert speech to text?',
            'body': 'Need to transcribe some podcasts',
            'score': 5,
            'num_comments': 2,
            'age_hours': 6,
        },
    ]
    
    results = finder.filter_posts(sample_posts)
    
    print("Posts for LLM analysis:")
    for p in results['for_llm']:
        print(f"  [{p['relevance_score']}] {p['title']}")
        print(f"      Reasons: {', '.join(p['relevance_reasons'])}")
        print(f"      Category: {finder.categorize_post(p)}")
