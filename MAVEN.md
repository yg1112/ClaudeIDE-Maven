# Maven - AI CMO Agent for Reddit Marketing

## 🎯 What is Maven?

Maven is a Claude-powered CMO (Chief Marketing Officer) agent that helps you:
1. **Guerrilla Marketing** - Find and respond to relevant pain-point posts
2. **Market Intelligence** - Collect competitor insights and market opportunities  
3. **Post Defense** - Monitor and defend your published posts
4. **Karma Building** - Build credibility in target subreddits
5. **Content Creation** - Generate launch posts and marketing content

## 🚀 Quick Start

Just tell Claude: **"@Maven"** or **"呼叫 Maven"** and describe what you need.

### Example Commands:

```
@Maven 帮我找 r/productivity 里关于语音转写的痛点帖子
@Maven 分析一下 Otter.ai 在 Reddit 上的用户吐槽
@Maven 帮我守护这个帖子: [URL]
@Maven 帮我在 r/transcription 攒点 karma
@Maven 帮我写一个产品发布帖子
```

## 📁 Project Structure

```
maven/
├── MAVEN.md              # This file - Main documentation
├── config/
│   ├── product.yaml      # Your product info
│   ├── reddit.yaml       # Reddit API & target subreddits
│   └── personas.yaml     # Reply personas/tones
├── scripts/
│   ├── reddit_client.py  # Reddit API wrapper
│   ├── post_finder.py    # Find relevant posts
│   ├── reply_generator.py # Generate human-like replies
│   ├── karma_builder.py  # Karma building logic
│   └── scheduler.py      # Scheduled tasks
├── data/
│   ├── replied_posts.json    # Track replied posts (avoid duplicates)
│   ├── monitored_posts.json  # Posts we're monitoring
│   └── karma_history.json    # Karma building history
└── templates/
    ├── launch_post.md        # Product launch template
    ├── pain_point_reply.md   # Pain point reply template
    └── technical_reply.md    # Technical question template
```

## 🔑 Setup Your Reddit Credentials

Create a Reddit app at: https://www.reddit.com/prefs/apps

You'll need:
- `client_id`
- `client_secret`  
- `username`
- `password`
- `user_agent`

## 💡 How Maven Works

### Smart Processing Pipeline (Cost Efficient)

```
┌─────────────────┐
│  Reddit Search  │  Free API calls
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Keyword Filter  │  No LLM cost
│ (Title/Body)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Relevance Score │  Simple heuristics
│ (0-100)         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Top 10 Posts    │  Only these go to LLM
│ for LLM Review  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Generate   │  Quality replies
│  Human Reply    │
└─────────────────┘
```

### Human-Like Behavior Rules

1. **Never reply to already-answered questions**
2. **Read full context before replying**
3. **Match the tone of the subreddit**
4. **Don't spam - max 3-5 replies per day per subreddit**
5. **Vary reply length and style**
6. **Add genuine value, not just promotion**
7. **Wait random intervals between replies**

## 📊 Karma Building Strategy

### Phase 1: Lurk & Learn (Week 1)
- Identify high-karma posts in target subreddits
- Understand community rules and culture
- Find easy technical questions to answer

### Phase 2: Helpful Contributor (Week 2-4)
- Answer technical questions genuinely
- No product mentions yet
- Build reputation

### Phase 3: Trusted Member (Month 2+)
- Can now mention product when genuinely relevant
- Still primarily helpful, promotion is secondary

## ⚠️ Important Guidelines

- **Never lie** about being affiliated with the product
- **Add value first**, promote second
- **Respect subreddit rules**
- **Don't be defensive** when criticized
- **Sound human** - use casual language, occasional typos even
