#!/usr/bin/env python3
"""
Duplicate Detector - Avoid repeating what others said
=====================================================

Checks existing comments to ensure our reply adds unique value.
"""

from typing import List, Dict, Any
import re
from difflib import SequenceMatcher


class DuplicateDetector:
    """
    Detect if our reply is too similar to existing comments.

    Rules:
    1. Don't repeat same solutions
    2. Don't use same phrasing
    3. Add unique perspective
    """

    def __init__(self, similarity_threshold: float = 0.6):
        """
        Initialize detector.

        Args:
            similarity_threshold: 0-1, replies above this are considered duplicates
        """
        self.similarity_threshold = similarity_threshold

    def extract_key_points(self, text: str) -> List[str]:
        """
        Extract key points from a comment.

        Returns:
            List of key phrases (products, tools, techniques mentioned)
        """
        text_lower = text.lower()

        key_points = []

        # Extract product mentions
        product_patterns = [
            r'\b(otter\.ai|descript|whisper|notion|obsidian)\b',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:app|tool|software)\b',
            r'\buse\s+([a-z]+(?:\s+[a-z]+){0,2})\b',
            r'\btry\s+([a-z]+(?:\s+[a-z]+){0,2})\b'
        ]

        for pattern in product_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            key_points.extend(matches)

        # Extract techniques
        technique_patterns = [
            r'(?:i|we)\s+(.*?)\s+(?:and|to|for)',
            r'(?:use|using|try)\s+(.*?)\s+(?:to|for|and)',
        ]

        for pattern in technique_patterns:
            matches = re.findall(pattern, text_lower)
            key_points.extend([m[:50] for m in matches if len(m) > 5])

        return [p.strip() for p in key_points if p.strip()]

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts.

        Returns:
            0-1 score (1 = identical)
        """
        # Normalize texts
        t1 = text1.lower().strip()
        t2 = text2.lower().strip()

        # Use SequenceMatcher for similarity
        return SequenceMatcher(None, t1, t2).ratio()

    def is_duplicate(
        self,
        proposed_reply: str,
        existing_comments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check if proposed reply is too similar to existing comments.

        Args:
            proposed_reply: Our draft reply
            existing_comments: List of existing comments on the post

        Returns:
            {
                'is_duplicate': bool,
                'reason': str,
                'similar_to': str,  # Comment it's similar to
                'similarity_score': float,
                'suggestions': List[str]  # How to make it unique
            }
        """
        proposed_lower = proposed_reply.lower()
        proposed_points = self.extract_key_points(proposed_reply)

        for comment in existing_comments:
            comment_text = comment.get('body', '')

            # Calculate text similarity
            similarity = self.calculate_similarity(proposed_reply, comment_text)

            if similarity > self.similarity_threshold:
                return {
                    'is_duplicate': True,
                    'reason': f'Too similar to existing comment ({similarity:.0%} match)',
                    'similar_to': comment_text[:200],
                    'similarity_score': similarity,
                    'suggestions': [
                        'Add a different perspective',
                        'Mention a different approach',
                        'Focus on a different aspect'
                    ]
                }

            # Check for same key points
            comment_points = self.extract_key_points(comment_text)

            common_points = set(proposed_points) & set(comment_points)
            if len(common_points) > 0 and len(proposed_points) > 0:
                overlap_ratio = len(common_points) / len(proposed_points)

                if overlap_ratio > 0.7:  # 70% of our points already mentioned
                    return {
                        'is_duplicate': True,
                        'reason': f'{len(common_points)} key points already mentioned',
                        'similar_to': comment_text[:200],
                        'similarity_score': overlap_ratio,
                        'common_points': list(common_points),
                        'suggestions': [
                            'Mention different tools/approaches',
                            'Add a unique angle or perspective',
                            'Focus on implementation details'
                        ]
                    }

        # Not a duplicate
        return {
            'is_duplicate': False,
            'reason': 'Reply adds unique value',
            'similarity_score': 0.0
        }

    def extract_mentioned_products(self, comments: List[Dict[str, Any]]) -> List[str]:
        """
        Extract all products/tools already mentioned in comments.

        Returns:
            List of product names
        """
        products = set()

        for comment in comments:
            text = comment.get('body', '')
            points = self.extract_key_points(text)
            products.update(points)

        return sorted(list(products))

    def suggest_unique_angle(
        self,
        existing_comments: List[Dict[str, Any]],
        post_context: Dict[str, Any]
    ) -> List[str]:
        """
        Suggest unique angles not yet covered in existing comments.

        Returns:
            List of suggestions for making reply unique
        """
        mentioned_products = self.extract_mentioned_products(existing_comments)

        suggestions = []

        # Check what's NOT mentioned yet
        common_aspects = [
            'speed/performance',
            'cost/pricing',
            'privacy/security',
            'ease of use',
            'offline capability',
            'customization',
            'support/community'
        ]

        # Simple heuristic: check if these words appear in comments
        aspect_keywords = {
            'speed/performance': ['fast', 'speed', 'quick', 'slow', 'performance'],
            'cost/pricing': ['price', 'cost', 'expensive', 'cheap', 'free', 'subscription'],
            'privacy/security': ['privacy', 'secure', 'cloud', 'local', 'offline'],
            'ease of use': ['easy', 'simple', 'intuitive', 'complicated'],
            'offline capability': ['offline', 'local', 'internet', 'cloud'],
            'customization': ['custom', 'configure', 'settings', 'options'],
            'support/community': ['support', 'community', 'help', 'documentation']
        }

        comments_text = ' '.join([c.get('body', '') for c in existing_comments]).lower()

        for aspect, keywords in aspect_keywords.items():
            if not any(kw in comments_text for kw in keywords):
                suggestions.append(f"Focus on {aspect} (not mentioned yet)")

        if not suggestions:
            suggestions = [
                "Add personal experience/story",
                "Provide specific numbers/benchmarks",
                "Share implementation tips"
            ]

        return suggestions


# Example usage
if __name__ == "__main__":
    detector = DuplicateDetector()

    # Example comments
    existing = [
        {'body': 'I use Otter.ai for transcription. Works great but expensive.'},
        {'body': 'Try Descript, it has good accuracy and is free for basic use.'},
    ]

    proposed = "I recommend using Otter.ai, it works great for transcription!"

    result = detector.is_duplicate(proposed, existing)

    print(f"Is duplicate: {result['is_duplicate']}")
    print(f"Reason: {result['reason']}")

    if result['is_duplicate']:
        print(f"\nSimilar to:\n{result['similar_to']}")
        print(f"\nSuggestions:")
        for s in result['suggestions']:
            print(f"  - {s}")

    # Check unique angles
    print("\n\n🎯 Unique angles available:")
    angles = detector.suggest_unique_angle(existing, {})
    for angle in angles:
        print(f"  - {angle}")
