#!/usr/bin/env python3
"""
Content Generator - Generate launch posts and marketing content
"""

import yaml
from typing import Dict, Any


class ContentGenerator:
    """Generate marketing content for different platforms."""

    def __init__(self, product_config_path: str):
        """Initialize content generator."""
        with open(product_config_path) as f:
            self.config = yaml.safe_load(f)
        self.product = self.config.get('product', {})

    def get_subreddit_guidelines(self, subreddit: str) -> str:
        """Get posting guidelines for a subreddit."""

        # Common guidelines for popular subreddits
        guidelines_map = {
            'SideProject': 'Be humble, share journey, include what you learned',
            'Entrepreneur': 'Focus on business value, not just tech',
            'programming': 'Technical details, architecture, tech stack',
            'Python': 'Python-specific implementation details',
            'InternetIsBeautiful': 'Must be actually useful, not promotional'
        }

        return guidelines_map.get(subreddit, 'Follow community rules')

    def generate_launch_post_prompt(
        self,
        subreddit: str,
        angle: str,
        github_docs: str = None
    ) -> str:
        """Generate LLM prompt for a launch post."""

        guidelines = self.get_subreddit_guidelines(subreddit)

        product_info = f"""
Product: {self.product.get('name')}
Tagline: {self.product.get('tagline')}
Features: {self.product.get('features')}
Target Audience: {self.product.get('target_audience')}
"""

        if github_docs:
            product_info += f"\n\nGitHub Docs:\n{github_docs[:2000]}"

        angle_instructions = {
            'problem_solution': 'Lead with the pain point, then introduce solution',
            'show_hn_style': 'Technical deep-dive, architecture, interesting challenges',
            'personal_journey': 'Story-driven, what motivated you, lessons learned',
            'comparison': 'Position vs alternatives, unique selling points'
        }

        return f"""Generate a Reddit launch post for r/{subreddit}.

{product_info}

Angle: {angle}
Instructions: {angle_instructions.get(angle)}

Subreddit guidelines: {guidelines}

IMPORTANT RULES:
- Be humble, not salesy
- Focus on value, not features
- Match subreddit culture
- Include a clear call-to-action
- 200-400 words

Generate:
1. Title (catchy but not clickbait)
2. Post body (markdown formatted)
"""
