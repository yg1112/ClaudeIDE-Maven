#!/usr/bin/env python3
"""
Reply Generator for Maven
Generates human-like replies using LLM with context awareness
"""

import yaml
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

class ReplyGenerator:
    """
    Generates human-like Reddit replies.
    
    Key principles:
    1. Read full context before replying
    2. Don't repeat what others said
    3. Add genuine value
    4. Sound human, not promotional
    5. Match subreddit tone
    """
    
    def __init__(
        self,
        product_config_path: str = "config/product.yaml",
        personas_config_path: str = "config/personas.yaml"
    ):
        self.product = self._load_yaml(product_config_path)
        self.personas = self._load_yaml(personas_config_path)
        
    def _load_yaml(self, path: str) -> dict:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    def generate_reply_prompt(
        self,
        post: Dict[str, Any],
        post_category: str,
        existing_comments: List[Dict[str, Any]] = None,
        persona: str = "helpful_user",
        github_context: str = None
    ) -> str:
        """
        Generate the prompt for LLM to create a reply.
        
        Args:
            post: The Reddit post data
            post_category: From PostFinder.categorize_post()
            existing_comments: Comments already on the post
            persona: Which persona to use
            github_context: Optional product documentation from GitHub
            
        Returns:
            Prompt string for the LLM
        """
        persona_config = self.personas['personas'].get(persona, {})
        context_rules = self.personas.get('context_rules', {}).get(post_category, {})
        
        # Build the prompt
        prompt = f"""You are helping write a Reddit reply. Your goal is to sound like a genuine, helpful Reddit user - NOT a marketer.

## POST INFORMATION
**Subreddit:** r/{post['subreddit']}
**Title:** {post['title']}
**Body:** {post['body']}
**Score:** {post['score']} | **Comments:** {post['num_comments']}
**Post Category:** {post_category}

## EXISTING COMMENTS (Don't repeat these points)
"""
        
        if existing_comments:
            for i, comment in enumerate(existing_comments[:10]):  # Max 10 comments
                prompt += f"""
Comment {i+1} by u/{comment['author']} (score: {comment['score']}):
{comment['body'][:500]}
---"""
        else:
            prompt += "\nNo existing comments.\n"
        
        prompt += f"""

## PRODUCT INFO (Use naturally, don't force)
**Name:** {self.product['product']['name']}
**Tagline:** {self.product['product']['tagline']}
**Key Features:** {', '.join([f['name'] for f in self.product['product'].get('features', [])])}
**Pricing:** {self.product['product'].get('pricing', {}).get('price_range', 'Free tier available')}
"""
        
        if github_context:
            prompt += f"""
## ADDITIONAL PRODUCT DOCS
{github_context[:2000]}
"""
        
        prompt += f"""

## PERSONA: {persona}
**Tone:** {persona_config.get('tone', 'friendly, casual, helpful')}
**Style Guidelines:**
{chr(10).join('- ' + s for s in persona_config.get('style', []))}

**AVOID:**
{chr(10).join('- ' + a for a in persona_config.get('avoid', []))}

## CONTEXT-SPECIFIC RULES FOR '{post_category}'
{json.dumps(context_rules, indent=2) if context_rules else 'No specific rules.'}

## CRITICAL INSTRUCTIONS

1. **READ THE ROOM**: Look at the existing comments. What hasn't been said yet? What can you add?

2. **DON'T BE THE FIRST TO MENTION THE PRODUCT**: If this is a competitor complaint, empathize first. If it's a recommendation request, mention alternatives too.

3. **BE GENUINELY HELPFUL**: Solve their problem. The product mention should feel natural, not forced.

4. **SOUND HUMAN**:
   - Use contractions (I'm, don't, it's)
   - Occasional filler words (actually, honestly, tbh)
   - Don't be too perfect or polished
   - Match the casualness of the subreddit
   - Keep it concise - don't write an essay

5. **DON'T REPEAT**: If someone already recommended the same thing, don't pile on. Add something new or skip.

6. **MAYBE DON'T MENTION THE PRODUCT**: If others already covered it or it's not genuinely relevant, just be helpful without promoting anything.

## OUTPUT FORMAT

Write ONLY the reply text. No explanations, no "Here's my reply:", just the actual Reddit comment.

Keep it between 50-200 words typically. Can be shorter if appropriate.
"""
        
        return prompt
    
    def post_process_reply(
        self, 
        reply: str,
        post: Dict[str, Any],
        existing_comments: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Post-process and validate the generated reply.
        
        Returns:
            {
                'text': str,           # The reply text
                'should_post': bool,   # Whether to actually post
                'reason': str,         # Why or why not
                'warnings': List[str]  # Any concerns
            }
        """
        warnings = []
        should_post = True
        reason = "Looks good"
        
        reply = reply.strip()
        
        # Check length
        word_count = len(reply.split())
        if word_count < 20:
            warnings.append("Reply might be too short")
        if word_count > 300:
            warnings.append("Reply might be too long - consider shortening")
        
        # Check for marketing red flags
        marketing_phrases = [
            "check out",
            "you should try",
            "I highly recommend",
            "amazing tool",
            "game changer",
            "life changing",
            "best thing ever",
        ]
        for phrase in marketing_phrases:
            if phrase.lower() in reply.lower():
                warnings.append(f"Marketing phrase detected: '{phrase}'")
        
        # Check if product is mentioned too early
        product_name = self.product['product']['name'].lower()
        if product_name in reply.lower():
            # Check position - should not be in first sentence
            first_sentence = reply.split('.')[0].lower()
            if product_name in first_sentence:
                warnings.append("Product mentioned too early - sounds promotional")
        
        # Check for duplication with existing comments
        if existing_comments:
            reply_lower = reply.lower()
            for comment in existing_comments:
                comment_lower = comment['body'].lower()
                # Check for high overlap
                overlap = self._text_overlap(reply_lower, comment_lower)
                if overlap > 0.5:
                    should_post = False
                    reason = "Too similar to existing comment"
                    break
        
        # Check for emotional awareness
        negative_indicators = ['struggling', 'frustrated', 'hate', 'terrible', 'awful']
        post_text = f"{post['title']} {post['body']}".lower()
        post_is_negative = any(ind in post_text for ind in negative_indicators)
        
        empathy_words = ['understand', 'feel', 'sorry', 'tough', 'hard', 'been there']
        reply_has_empathy = any(word in reply.lower() for word in empathy_words)
        
        if post_is_negative and not reply_has_empathy:
            warnings.append("Post seems emotional but reply lacks empathy")
        
        return {
            'text': reply,
            'should_post': should_post,
            'reason': reason,
            'warnings': warnings,
            'word_count': word_count,
        }
    
    def _text_overlap(self, text1: str, text2: str) -> float:
        """Calculate word overlap ratio between two texts."""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
            
        overlap = len(words1 & words2)
        return overlap / min(len(words1), len(words2))
    
    def generate_defense_reply_prompt(
        self,
        original_post: Dict[str, Any],
        comment_to_reply: Dict[str, Any],
        is_criticism: bool = False
    ) -> str:
        """Generate prompt for defending your own post."""
        
        prompt = f"""You are the original poster (OP) replying to a comment on your post.

## YOUR ORIGINAL POST
**Title:** {original_post['title']}
**Body:** {original_post['body']}

## COMMENT TO REPLY TO
**Author:** u/{comment_to_reply['author']}
**Their comment:** {comment_to_reply['body']}
**Is this criticism?** {'Yes' if is_criticism else 'No'}

## PRODUCT INFO
**Name:** {self.product['product']['name']}

## INSTRUCTIONS

{'This is criticism. Be gracious:' if is_criticism else 'This is a question or positive comment:'}
{'''
- Acknowledge valid points
- Don't be defensive
- Thank them for feedback if appropriate
- Explain your perspective calmly
- Never attack or argue
''' if is_criticism else '''
- Answer their question clearly
- Thank them if appropriate
- Offer to help further
- Be friendly and genuine
'''}

Write ONLY the reply. Keep it concise (50-150 words).
"""
        
        return prompt
    
    def select_persona(self, post_category: str, subreddit: str) -> str:
        """Select the best persona for the context."""
        
        # Technical subreddits
        technical_subs = ['programming', 'webdev', 'learnprogramming', 'coding']
        if subreddit.lower() in technical_subs:
            return 'technical_expert'
        
        # Based on post category
        if post_category == 'competitor_complaint':
            return 'casual_recommender'
        elif post_category == 'technical_question':
            return 'technical_expert'
        elif post_category == 'recommendation_request':
            return 'casual_recommender'
        
        return 'helpful_user'
    
    def add_human_touches(self, reply: str) -> str:
        """Add subtle human touches to make reply more natural."""
        
        behaviors = self.personas.get('human_like_behaviors', {})
        
        # Maybe add Reddit slang
        if random.random() < 0.2:
            slang = behaviors.get('use_reddit_slang', ['tbh', 'imo', 'fwiw'])
            if slang:
                # Don't add if already has one
                if not any(s in reply.lower() for s in slang):
                    word = random.choice(slang)
                    # Add at end of a sentence
                    sentences = reply.split('. ')
                    if len(sentences) > 1:
                        idx = random.randint(0, len(sentences) - 2)
                        sentences[idx] = sentences[idx] + f' {word}'
                        reply = '. '.join(sentences)
        
        return reply


# Example usage
if __name__ == "__main__":
    generator = ReplyGenerator()
    
    sample_post = {
        'title': 'Looking for Otter.ai alternatives - too expensive',
        'body': 'Been using Otter for transcription but it\'s getting too expensive. Any good alternatives?',
        'subreddit': 'productivity',
        'score': 25,
        'num_comments': 5,
    }
    
    sample_comments = [
        {
            'author': 'user1',
            'body': 'I switched to Rev, it\'s pretty good but also not cheap.',
            'score': 5
        }
    ]
    
    prompt = generator.generate_reply_prompt(
        post=sample_post,
        post_category='competitor_complaint',
        existing_comments=sample_comments,
        persona='casual_recommender'
    )
    
    print("Generated prompt for LLM:")
    print("-" * 50)
    print(prompt[:2000] + "...")
