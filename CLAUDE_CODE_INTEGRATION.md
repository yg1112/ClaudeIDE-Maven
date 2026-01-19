# Maven + Claude Code Integration Guide

## 🎯 How to Use Maven with Claude Code

Maven is designed to be invoked directly from Claude Code (Claude IDE). Just tell Claude what you need!

---

## Quick Commands

### 呼叫 Maven

Just say any of these:
- `@Maven` 
- `呼叫 Maven`
- `Maven, help me with...`

### Example Conversations

```
You: @Maven 帮我找 r/productivity 里关于语音转写的痛点帖子

Claude: [Reads Maven configs, searches Reddit, filters posts, shows top opportunities]
```

```
You: Maven，分析一下 Otter.ai 最近在 Reddit 上的评价

Claude: [Runs market intelligence, analyzes sentiment, generates report]
```

```
You: @Maven 帮我写一个 SideProject 的发布帖

Claude: [Reads your product config, generates launch post with proper tone]
```

---

## Setup Instructions

### 1. Configure Your Product

Edit `config/product.yaml` with your product details:

```yaml
product:
  name: "Your Product"
  tagline: "What it does in one line"
  website: "https://your-product.com"
  # ... rest of config
```

### 2. Add Reddit Credentials

Edit `config/reddit.yaml`:

```yaml
reddit:
  client_id: "your_client_id"
  client_secret: "your_client_secret"
  username: "your_reddit_username"
  password: "your_password"
  user_agent: "Maven CMO Agent v1.0"
```

Get credentials at: https://www.reddit.com/prefs/apps

### 3. Point to Your GitHub Repo (Optional)

If you want Maven to understand your product better, point it to your repo:

```
You: @Maven 我的项目在 /path/to/my/github/repo，帮我熟悉一下
```

---

## Maven Capabilities

### 1. 🎯 Guerrilla Marketing

Find and respond to relevant posts.

```
@Maven 帮我在这些 subreddit 找机会：r/productivity, r/transcription
```

**What Maven does:**
1. Searches Reddit (free API calls)
2. Filters by keywords (no LLM cost)
3. Scores relevance (no LLM cost)  
4. Only top posts go to LLM for reply generation
5. Reads ALL existing comments before replying
6. Generates human-like reply matching subreddit tone
7. Adds random delay before posting (looks human)

### 2. 🏆 Karma Building

Build credibility without promoting your product.

```
@Maven 帮我在 r/learnprogramming 攒点 karma
```

**What Maven does:**
1. Finds unanswered technical questions
2. Generates genuinely helpful answers
3. NO product mentions
4. Builds your reputation for future promotion

### 3. 👀 Post Monitoring

Defend your published posts.

```
@Maven 帮我监控这个帖子：[URL]
```

**What Maven does:**
1. Tracks new comments
2. Identifies questions, criticism, praise
3. Generates appropriate responses
4. Prioritizes urgent issues (criticism gets fast response)

### 4. 📊 Market Intelligence

Research competitors and opportunities.

```
@Maven 分析一下竞品 Otter.ai 的用户反馈
```

**What Maven does:**
1. Searches competitor mentions
2. Analyzes sentiment (positive/negative)
3. Extracts pain points
4. Identifies feature requests
5. Generates actionable report

### 5. ✍️ Content Creation

Generate launch posts and other content.

```
@Maven 帮我写一个 r/SideProject 的发布帖，用 personal_journey 风格
```

**Available angles:**
- `problem_solution` - Lead with pain point
- `show_hn_style` - Technical deep-dive
- `personal_journey` - Story-driven
- `comparison` - Position vs alternatives

---

## Cost Optimization

Maven is designed to minimize LLM costs:

```
┌─────────────────────────────────────────────────────────────┐
│                    MAVEN PROCESSING PIPELINE                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Reddit API Search          [FREE]        100 posts         │
│         │                                                   │
│         ▼                                                   │
│  Keyword Filtering          [FREE]        → 40 posts        │
│         │                                                   │
│         ▼                                                   │
│  Heuristic Scoring          [FREE]        → 15 posts        │
│         │                                                   │
│         ▼                                                   │
│  Relevance Threshold        [FREE]        → 10 posts        │
│         │                                                   │
│         ▼                                                   │
│  LLM Reply Generation       [$$$]         → 5 replies       │
│                                                             │
│  💰 SAVINGS: 95% of posts filtered WITHOUT LLM calls        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Human-Like Behavior Rules

Maven follows strict rules to avoid looking like a bot:

### ✅ DO
- Read all existing comments before replying
- Add value that hasn't been said
- Match subreddit tone and culture
- Use contractions (I'm, don't, it's)
- Include occasional filler words (actually, honestly, tbh)
- Vary reply length (50-200 words)
- Wait 10-120 minutes between posts
- Sometimes DON'T mention the product

### ❌ DON'T
- Repeat what others already said
- Use marketing language ("revolutionary", "game-changing")
- Reply immediately after searching
- Post at exact intervals
- Be overly enthusiastic
- Ignore emotional context
- Spam the same message

---

## File Structure

```
maven/
├── MAVEN.md                    # Main documentation
├── CLAUDE_CODE_INTEGRATION.md  # This file
├── config/
│   ├── product.yaml            # Your product info
│   ├── reddit.yaml             # Reddit API credentials  
│   └── personas.yaml           # Reply tone configurations
├── scripts/
│   ├── maven.py                # Main controller
│   ├── reddit_client.py        # Reddit API wrapper
│   ├── post_finder.py          # Smart post filtering
│   ├── reply_generator.py      # Human-like replies
│   ├── karma_builder.py        # Karma building logic
│   ├── market_intelligence.py  # Competitor analysis
│   ├── post_monitor.py         # Post defense
│   └── content_generator.py    # Content creation
└── data/
    ├── replied_posts.json      # Track what we've replied to
    ├── monitored_posts.json    # Posts we're watching
    ├── karma_history.json      # Karma building progress
    └── market_insights.json    # Collected intelligence
```

---

## Daily Routine

Maven can run a daily routine:

```
@Maven run daily routine
```

This does:
1. **Morning**: Check monitored posts, reply to urgent items
2. **Midday**: Build karma in target subreddits (2-3 helpful replies)
3. **Afternoon**: Guerrilla marketing (3-5 strategic replies)
4. **Weekly**: Market intelligence report (Mondays)

---

## Safety Features

### Dry Run Mode (Default)
Maven won't actually post unless you explicitly enable it:

```
@Maven 帮我回复这些帖子 --live
```

Without `--live`, Maven will generate replies but not post them.

### Rate Limiting
- Max 5 replies per subreddit per day
- Random delays between posts (10-120 minutes)
- Tracks all activity to prevent spam detection

### Content Validation
- Checks for marketing red flags
- Warns about overly promotional language
- Validates reply isn't duplicate of existing comments

---

## Tips for Best Results

1. **Start with karma building** - Build credibility first
2. **Read the room** - Check top posts in target subreddits
3. **Be patient** - Don't post too much too fast
4. **Engage genuinely** - Reply to comments on your posts
5. **Track results** - Monitor which approaches work
6. **Iterate** - Adjust product.yaml based on learnings

---

## Troubleshooting

### "Rate limited by Reddit"
Wait 10 minutes, then retry. Consider reducing post frequency.

### "Replies sound too promotional"
Edit `config/personas.yaml` to adjust tone. Use "helpful_user" persona.

### "Not finding relevant posts"
Add more keywords to `config/product.yaml` search_keywords section.

### "Getting downvoted"
- Are you adding value? 
- Are you matching community tone?
- Try pure karma building (no promotion) for a week first.
