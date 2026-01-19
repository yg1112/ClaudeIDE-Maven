# Maven - AI CMO Agent for Reddit Marketing

<div align="center">

**Intelligent, Cost-Efficient Reddit Marketing Automation**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Powered by Claude](https://img.shields.io/badge/Powered%20by-Claude-purple.svg)](https://www.anthropic.com/claude)

[Features](#-features) • [Quick Start](#-quick-start) • [Test Results](#-test-results) • [Documentation](#-documentation)

</div>

---

## 🎯 What is Maven?

Maven is an AI-powered Chief Marketing Officer (CMO) agent that helps you execute sophisticated Reddit marketing campaigns. Built with expert guerrilla marketing principles, Maven finds opportunities, generates human-like responses, and engages with communities—all while avoiding spam detection.

### Why Maven?

- **🎯 Sniper Strategy**: Two-step approach that provides value first, mentions product only when asked
- **⏱️ Pacing Engine**: Smart rate limiting prevents shadowbans (10-30min delays, max 5/day/subreddit)
- **🔍 Duplicate Detection**: Never repeat what others already said—always adds unique value
- **💰 Cost-Optimized**: 95% scripted (free), only final reply generation uses Claude (~$0.03/week)
- **🎭 Tone Matching**: Adapts to each subreddit's culture and communication style
- **📊 Market Intelligence**: Track competitors, analyze sentiment, identify opportunities

---

## ✨ Features

### 1. Guerrilla Marketing
Find and respond to pain-point posts with genuine value:
```
Input: Target r/productivity for voice typing discussions
Output: 6 high-quality opportunities identified (from 12 posts)
Cost: $0 (scripted filtering, LLM only for final replies)
```

### 2. Sniper Strategy (Two-Step Logic)
**Traditional Spam**:
```
User: "Looking for transcription tools"
Bot: "Try ProductX! [link]"  ❌ Looks promotional
```

**Maven Sniper**:
```
Step 1: Provide value (no product mention)
"I've been using local transcription and the speed difference
is huge. A 1-hour meeting goes from ~50 min to 6 min..."

[Wait for trigger: "What app do you use?"]

Step 2: Share when invited
"Sure! I'll DM you to avoid being promotional here..."  ✅ Natural
```

### 3. Pacing Engine
Prevents spam detection with:
- Random delays: 10-30 minutes between posts
- Daily limits: Max 5 posts per subreddit
- Cooldown: 60 min after 3 consecutive posts
- Per-subreddit tracking

### 4. Duplicate Detection
Ensures unique contributions:
```
Existing comments: "Try Whisper or Rev"
Maven: ✅ Focuses on uncovered angles (privacy, speed, cost)
       ❌ Blocks repetitive suggestions
```

### 5. Karma Building
Build credibility before promoting:
- Answer technical questions genuinely
- No product mentions (pure value)
- Target: r/learnprogramming, r/webdev

### 6. Post Defense
Monitor and respond to your published posts:
- Track new comments
- Identify questions/criticism/praise
- Generate appropriate responses
- Prioritize urgent issues

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install praw pyyaml anthropic
```

### 2. Configure Reddit API
Create `config/reddit.yaml` from template:
```bash
cp config/reddit.yaml.template config/reddit.yaml
# Edit with your Reddit API credentials
```

Get credentials: https://www.reddit.com/prefs/apps

### 3. Configure Your Product
Edit `product.yaml`:
```yaml
product:
  name: "Your Product Name"
  tagline: "One-line description"
  website: "https://yourproduct.com"

  pain_points_solved:
    - "Problem 1"
    - "Problem 2"

  features:
    - name: "Feature 1"
      description: "What it does"
      differentiator: "Why it's better"
```

### 4. Use with Claude Code
```
You: @Maven 帮我在 r/productivity 找营销机会
Claude: [Analyzes Reddit, finds opportunities, generates replies]
```

Or run standalone:
```bash
python maven.py --subreddit productivity --keywords "voice typing" "transcription"
```

---

## 📊 Test Results

Real test conducted on **2026-01-18** with [Reso](https://github.com/yg1112/Reso) (voice typing app):

### Test Summary
- **12 Reddit posts** analyzed (r/productivity, r/macapps)
- **6 high-quality opportunities** identified
- **465 real comments** processed
- **0 LLM calls** (100% scripted filtering)
- **$0 cost** for discovery phase

### Key Findings

| Opportunity | Subreddit | Engagement | Category |
|-------------|-----------|------------|----------|
| FreeVoice Reader | r/macapps | 261👍 471💬 | Competitor Launch |
| Pipit (WisprFlow alt) | r/macapps | 33👍 79💬 | Alternative Request |
| Ottex AI | r/macapps | 11👍 40💬 | BYOK Discussion |
| Fluent 1.7 | r/macapps | 11👍 36💬 | Feature Release |
| Offline TTS | r/macapps | 39👍 99💬 | Privacy-Focused |
| FonoX | r/macapps | 1👍 9💬 | Early Discussion |

### Generated Strategies

**Sniper Reply Example** (for Pipit discussion):
```
I've been using local transcription for a while and the speed
difference from cloud services is huge.

For context: cloud services like Otter process on their servers,
so you're waiting for upload + processing. With optimized local
models on M1/M2, a 1-hour meeting goes from ~50 minutes (most apps)
to about 6 minutes.

Key benefits I found:
- Privacy: nothing leaves your Mac
- Speed: Whisper Large V3 Turbo optimized for Apple Silicon
- Cost: one-time vs subscription

The tradeoff is you need decent hardware (M1/M2 or better),
but if you have that, it's worth exploring.

[Monitoring for: "what app", "which tool", "link?"]
```

**See full test report**: [test_run_20260118_172145/TEST_REPORT.md](test_run_20260118_172145/TEST_REPORT.md)

---

## 📖 Documentation

- **[MAVEN.md](MAVEN.md)**: Core concepts and strategies
- **[QUICKSTART.md](QUICKSTART.md)**: Step-by-step setup guide
- **[CLAUDE_CODE_INTEGRATION.md](CLAUDE_CODE_INTEGRATION.md)**: How to use Maven with Claude Code
- **[ADVANCED_FEATURES.md](ADVANCED_FEATURES.md)**: Deep dive into expert features
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**: Common issues and solutions

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│          MAVEN PROCESSING PIPELINE              │
├─────────────────────────────────────────────────┤
│                                                 │
│  Reddit Search (PRAW)       [FREE]  100 posts  │
│         │                                       │
│         ▼                                       │
│  Keyword Filter            [FREE]   → 40 posts │
│         │                                       │
│         ▼                                       │
│  Heuristic Scoring         [FREE]   → 15 posts │
│         │                                       │
│         ▼                                       │
│  Duplicate Detection       [FREE]   → 10 posts │
│         │                                       │
│         ▼                                       │
│  Tone Matching             [FREE]   → 5 posts  │
│         │                                       │
│         ▼                                       │
│  LLM Reply Generation      [$$$]    → 5 replies│
│                                                 │
│  💰 COST SAVINGS: 95% filtered without LLM     │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Core Modules

- **`reddit_client.py`**: Reddit API wrapper (PRAW)
- **`post_finder.py`**: Smart post discovery and filtering
- **`sniper_strategy.py`**: Two-step marketing logic
- **`pacing_engine.py`**: Rate limiting and spam prevention
- **`duplicate_detector.py`**: Uniqueness validation
- **`reply_generator.py`**: Human-like reply generation
- **`maven_orchestrator.py`**: Main workflow coordination
- **`karma_builder.py`**: Credibility building
- **`market_intelligence.py`**: Competitor analysis
- **`post_monitor.py`**: Post defense and monitoring

---

## 🔒 Safety Features

### Anti-Spam Protection
- ✅ **Dry Run Mode** (default): Preview replies before posting
- ✅ **Rate Limiting**: 10-30 min delays, max 5/day/subreddit
- ✅ **Content Validation**: Checks for marketing red flags
- ✅ **Duplicate Detection**: Never repeats existing comments
- ✅ **Tone Matching**: Adapts to subreddit culture

### Privacy
- ✅ **Credentials Protected**: `config/reddit.yaml` in .gitignore
- ✅ **Activity Tracking Local**: All history stored locally only
- ✅ **No Telemetry**: Zero data sent to third parties

---

## 💡 Use Cases

### For Product Launches
```
@Maven 帮我写一个 r/SideProject 的发布帖
→ Generates launch post with proper tone and structure
```

### For Market Research
```
@Maven 分析竞品 Otter.ai 的用户反馈
→ Searches mentions, analyzes sentiment, extracts pain points
```

### For Community Engagement
```
@Maven 帮我在 r/macapps 找语音转写讨论
→ Finds relevant threads, generates contextual replies
```

### For Karma Building
```
@Maven 帮我在 r/learnprogramming 攒 karma
→ Finds technical questions, generates helpful answers (no promotion)
```

---

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines first.

### Areas for Improvement
- [ ] Add support for more social platforms (HackerNews, Twitter/X)
- [ ] Improve sentiment analysis accuracy
- [ ] Add A/B testing for different reply styles
- [ ] Build web dashboard for monitoring
- [ ] Add multi-language support

---

## 📜 License

MIT License - feel free to use for commercial or personal projects.

---

## ⚠️ Ethical Guidelines

Maven is designed for **authentic engagement**, not spam. Please:

- ✅ **Add genuine value** to discussions
- ✅ **Be transparent** about product affiliation when asked
- ✅ **Respect subreddit rules** and community norms
- ✅ **Prioritize helpfulness** over promotion
- ❌ **Never lie** about using automation
- ❌ **Don't spam** or violate rate limits
- ❌ **Don't manipulate** votes or brigade

---

## 🙏 Acknowledgments

- **Anthropic Claude**: Powers intelligent reply generation
- **PRAW**: Python Reddit API Wrapper
- **Reddit Community**: For being awesome and teaching us how to engage properly

---

## 📬 Contact

Questions? Suggestions? Open an issue or reach out!

**Built with ❤️ by the Claude Code community**

---

<div align="center">

**[⬆ Back to Top](#maven---ai-cmo-agent-for-reddit-marketing)**

</div>
