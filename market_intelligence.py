#!/usr/bin/env python3
"""
Market Intelligence - Competitor research and opportunity detection
"""

import json
from typing import Dict, Any, List


class MarketIntelligence:
    """Market intelligence and competitor analysis."""

    def __init__(self, product_config_path: str, insights_path: str):
        """Initialize market intelligence."""
        self.insights_path = insights_path
        self.insights = self._load_insights()

    def _load_insights(self) -> Dict:
        """Load saved insights."""
        try:
            with open(self.insights_path) as f:
                return json.load(f)
        except FileNotFoundError:
            return {'analyses': [], 'competitors': {}}

    def _save_insights(self):
        """Save insights."""
        with open(self.insights_path, 'w') as f:
            json.dump(self.insights, f, indent=2)

    def analyze_post(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a post for market intelligence."""

        text = f"{post.get('title', '')} {post.get('body', '')}".lower()

        # Simple sentiment analysis
        negative_words = ['bad', 'worse', 'terrible', 'hate', 'sucks', 'slow', 'expensive']
        positive_words = ['good', 'great', 'love', 'amazing', 'fast', 'cheap', 'free']

        sentiment = 'neutral'
        if any(word in text for word in negative_words):
            sentiment = 'negative'
        elif any(word in text for word in positive_words):
            sentiment = 'positive'

        return {
            'post_id': post.get('id'),
            'title': post.get('title'),
            'sentiment': sentiment,
            'url': post.get('url'),
            'text': text[:500]
        }

    def save_analysis(self, analysis: Dict[str, Any]):
        """Save an analysis."""
        self.insights['analyses'].append(analysis)
        self._save_insights()

    def aggregate_insights(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate multiple analyses into insights."""

        sentiments = [a['sentiment'] for a in analyses]

        return {
            'total_posts': len(analyses),
            'sentiment_breakdown': {
                'positive': sentiments.count('positive'),
                'negative': sentiments.count('negative'),
                'neutral': sentiments.count('neutral')
            },
            'actionable_insights': [
                f"Analyzed {len(analyses)} posts",
                f"Sentiment: {sentiments.count('negative')} negative, {sentiments.count('positive')} positive"
            ]
        }

    def generate_report_prompt(self, aggregated: Dict[str, Any]) -> str:
        """Generate LLM prompt for intelligence report."""

        return f"""Generate a market intelligence report based on this data:

Total posts analyzed: {aggregated['total_posts']}
Sentiment breakdown:
- Positive: {aggregated['sentiment_breakdown']['positive']}
- Negative: {aggregated['sentiment_breakdown']['negative']}
- Neutral: {aggregated['sentiment_breakdown']['neutral']}

Provide:
1. Key takeaways
2. Competitor weaknesses identified
3. Market opportunities
4. Recommended actions
"""
