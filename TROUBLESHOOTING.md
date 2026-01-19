# Maven 故障排除指南

## ❌ "Unknown slash command: maven"

如果你看到这个错误，说明Claude Code还没有识别到Maven skill。

### 解决方案

#### 方案1: 检查Skill文件是否存在

```bash
ls -la ~/.claude/skills/maven/
```

应该看到：
```
skill.yaml
skill.md
maven_bridge.py
README.md
```

如果缺少文件，说明安装不完整，需要重新安装。

#### 方案2: 检查skill.yaml格式

```bash
cat ~/.claude/skills/maven/skill.yaml
```

确保文件格式正确，没有语法错误。

#### 方案3: 重启Claude Code

Claude Code可能需要重启才能识别新的skill：

```bash
# 如果是CLI版本
claude --reload-skills

# 如果是IDE集成，重启你的编辑器
```

#### 方案4: 手动调用（不使用slash command）

如果slash command不工作，可以直接告诉Claude：

```
请帮我运行Maven营销助手，分析当前项目并找一些营销机会
```

Claude会理解你的意图并执行Maven的功能。

#### 方案5: 直接运行bridge脚本

你也可以直接运行Python脚本：

```bash
cd ~/github/ClaudeIDE-Maven
python3 ~/.claude/skills/maven/maven_bridge.py guerrilla \
  --repo-path $(pwd) \
  --subreddits "productivity,SideProject" \
  --max-replies 5
```

### Claude Code Skill系统说明

**注意**：截至目前，Claude Code的skill系统可能还在开发中，slash command功能可能有限制。

**推荐的调用方式**：

不使用 `/maven`，而是直接对话：

```
你：我在开发一个语音转写工具，能帮我在Reddit上做营销吗？

Claude：当然！我会使用Maven来帮你...
[然后Maven会自动运行]
```

或者：

```
你：用Maven帮我分析当前项目并生成营销内容

Claude：[读取当前repo，运行Maven]
```

这种方式更自然，而且不依赖slash command。

---

## ❌ "找不到Maven核心代码"

### 症状
```
ImportError: No module named 'maven'
或
FileNotFoundError: maven.py not found
```

### 解决方案

#### 检查Maven核心路径

```bash
ls -la ~/github/ClaudeIDE-Maven/
```

应该看到：
- maven.py
- post_finder.py
- reply_generator.py
- reddit_client.py
- karma_builder.py
- market_intelligence.py
- post_monitor.py
- content_generator.py

#### 如果路径不同

编辑bridge脚本：

```bash
nano ~/.claude/skills/maven/maven_bridge.py
```

修改第32行的路径：
```python
MAVEN_CORE_PATH = "/Users/yukungao/github/ClaudeIDE-Maven"
# 改成你的实际路径
MAVEN_CORE_PATH = "/your/actual/path/to/ClaudeIDE-Maven"
```

---

## ❌ "No Reddit credentials found"

### 症状
```
⚠️ No Reddit credentials found!
Please configure Reddit API credentials
```

### 解决方案

#### 检查配置文件

```bash
cat ~/github/ClaudeIDE-Maven/config/reddit.yaml
```

应该看到你的凭证（不是模板）。

#### 如果文件不存在或是模板

你的配置文件应该已经创建好了，在：
```
~/github/ClaudeIDE-Maven/config/reddit.yaml
```

如果需要重新配置：

```bash
nano ~/github/ClaudeIDE-Maven/config/reddit.yaml
```

填入你的真实凭证。

---

## ❌ Reddit API错误

### 症状
```
praw.exceptions.ResponseException: received 401 HTTP response
```

### 原因
- Reddit凭证错误
- Client ID或Secret错误
- 用户名或密码错误

### 解决方案

#### 验证凭证

1. 访问：https://www.reddit.com/prefs/apps
2. 找到你的App
3. 确认：
   - Client ID（图标下方的字符串）
   - Client Secret（点击"edit"后看到的secret）
4. 确认用户名和密码正确

#### 重新配置

```bash
nano ~/github/ClaudeIDE-Maven/config/reddit.yaml
```

仔细检查每个字段。

---

## ❌ "Module 'praw' not found"

### 症状
```
ModuleNotFoundError: No module named 'praw'
```

### 解决方案

安装依赖：

```bash
pip install praw pyyaml
```

或者如果使用pip3：

```bash
pip3 install praw pyyaml
```

如果使用虚拟环境：

```bash
cd ~/github/ClaudeIDE-Maven
python3 -m venv venv
source venv/bin/activate
pip install praw pyyaml
```

---

## ❌ 回复看起来太promotional（太像广告）

### 症状
生成的回复太像营销内容，不像真人。

### 解决方案

#### 调整Persona

编辑：
```bash
nano ~/github/ClaudeIDE-Maven/config/personas.yaml
```

修改 `helpful_user` persona：
```yaml
helpful_user:
  tone: casual  # 更随意
  enthusiasm: low  # 降低热情度
  formality: low  # 降低正式程度
```

#### 使用不同的Persona

在调用Maven时，可以指定persona：
- `helpful_user` - 最不像广告
- `technical_expert` - 技术讨论
- `empathetic_helper` - 同理心回复

---

## ❌ 被Reddit标记为spam

### 症状
- 帖子被自动删除
- 账号被shadowban
- Karma突然下降

### 原因
- 发帖太频繁
- 内容太相似
- 总是提到相同的产品

### 解决方案

#### 降低频率

编辑 `config/reddit.yaml`：
```yaml
rate_limits:
  max_posts_per_subreddit_per_day: 2  # 从5降到2
  min_delay_between_posts_seconds: 3600  # 1小时
```

#### 先积累Karma

在营销之前：
```
@maven 帮我在 r/learnprogramming 积累karma
```

用2-3天时间纯粹帮助别人，不提产品。

#### 多样化内容

- 不要每个回复都提产品
- 有时候只回答问题，不推荐任何工具
- 参与非营销讨论

---

## ❌ 生成的回复质量不高

### 症状
- 回复太短或太长
- 没有抓住要点
- 不符合subreddit文化

### 解决方案

#### 提供更多上下文

确保你的项目有详细的README：
```bash
nano ~/your-project/README.md
```

包含：
- 清楚的产品描述
- 解决什么问题
- 主要功能
- 目标用户

Maven会读取这些信息生成更好的回复。

#### 手动调整

Maven生成回复后，在发布前手动编辑：
- 添加个人经验
- 调整语气
- 删除不必要的内容

---

## 🆘 仍然有问题？

### 获取详细日志

运行Maven时添加verbose标志：

```bash
python3 ~/.claude/skills/maven/maven_bridge.py guerrilla \
  --repo-path $(pwd) \
  --subreddits "productivity" \
  --max-replies 5 \
  --verbose
```

### 检查Python版本

Maven需要Python 3.7+：

```bash
python3 --version
```

如果版本太老，升级Python。

### 手动测试每个组件

```python
cd ~/github/ClaudeIDE-Maven

# 测试Reddit连接
python3 -c "from reddit_client import RedditClient; r = RedditClient('config/reddit.yaml'); print('✓ Reddit client OK')"

# 测试Post Finder
python3 -c "from post_finder import PostFinder; p = PostFinder('config/product.yaml', 'config/reddit.yaml'); print('✓ Post finder OK')"
```

### 联系支持

如果以上都不行，可以：
1. 查看完整日志
2. 检查是否是Reddit API的问题
3. 尝试重新创建Reddit App

---

## 💡 最佳实践

### 避免常见问题

1. **慢慢来**
   - 第一天：只发1-2个回复
   - 之后：逐渐增加到每天3-5个

2. **多样化**
   - 不同的subreddit
   - 不同的话题
   - 有时不提产品

3. **真诚**
   - 真的帮助人
   - 不夸大产品功能
   - 承认缺点

4. **监控**
   - 检查karma变化
   - 看回复是否被删除
   - 调整策略

### 定期维护

```bash
# 每周检查一次
cd ~/github/ClaudeIDE-Maven

# 查看活动历史
cat data/replied_posts.json

# 检查karma趋势
cat data/karma_history.json

# 清理旧数据（可选）
# rm data/*.json
```
