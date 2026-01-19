# Maven配置文件说明

这个目录包含Maven的配置文件。

## 📁 文件说明

### reddit.yaml（敏感 - 不提交到GitHub）
包含你的Reddit API凭证。

**重要**：这个文件已经配置好了你的凭证，**不会被提交到GitHub**（已添加到.gitignore）。

如果需要修改：
```bash
nano config/reddit.yaml
```

### personas.yaml
定义Maven在不同场景下使用的回复风格。

可用persona：
- `helpful_user` - 友好的社区成员（最常用）
- `technical_expert` - 技术专家（用于开发者社区）
- `empathetic_helper` - 同理心帮助者（用于痛点讨论）
- `storyteller` - 讲故事者（用于个人经历分享）

### reddit.yaml.template
Reddit配置模板，供参考或分享给其他人。

## 🔧 修改配置

### 修改Reddit凭证

```bash
cd ~/github/ClaudeIDE-Maven
nano config/reddit.yaml
```

### 修改回复风格

```bash
nano config/personas.yaml
```

可以调整：
- `tone`: casual, professional, warm, personal
- `enthusiasm`: low, medium, high
- `formality`: low, medium, high

### 修改速率限制

在 `reddit.yaml` 中：

```yaml
rate_limits:
  max_posts_per_subreddit_per_day: 5  # 每天每个subreddit最多发几个帖子
  min_delay_between_posts_seconds: 600  # 帖子间最小延迟（秒）
  max_delay_between_posts_seconds: 7200  # 帖子间最大延迟（秒）
```

## 🛡️ 安全性

- `config/reddit.yaml` 已添加到 `.gitignore`，不会被提交
- 即使不小心 `git add .`，这个文件也会被忽略
- `reddit.yaml.template` 是模板，可以安全地提交

## 📝 创建新的Persona

编辑 `personas.yaml`，添加：

```yaml
personas:
  my_custom_persona:
    tone: casual
    enthusiasm: medium
    formality: low
    personality_traits:
      - 你的特质1
      - 你的特质2
    avoid:
      - 避免的东西1
      - 避免的东西2
    example_phrases:
      - "常用短语1"
      - "常用短语2"
```

然后在使用Maven时可以指定这个persona。

## 🔄 备份配置

建议定期备份你的配置（到安全的地方，不是GitHub）：

```bash
cp config/reddit.yaml ~/Backups/maven-reddit-config.yaml
cp config/personas.yaml ~/Backups/maven-personas-config.yaml
```

## ❓ 常见问题

### Q: 不小心把reddit.yaml提交到GitHub了怎么办？

A: 立即：
1. 去Reddit删除这个App：https://www.reddit.com/prefs/apps
2. 创建新的App，获取新凭证
3. 更新 `reddit.yaml`
4. 从Git历史中删除这个文件：
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch config/reddit.yaml" \
     --prune-empty --tag-name-filter cat -- --all
   ```

### Q: 想在多台电脑上使用Maven怎么办？

A: 将 `reddit.yaml` 复制到其他电脑：
```bash
# 在原电脑
scp config/reddit.yaml user@other-computer:~/github/ClaudeIDE-Maven/config/

# 或者用USB
cp config/reddit.yaml /Volumes/USB/
```

### Q: 想用不同的Reddit账号怎么办？

A: 创建多个配置文件：
```bash
cp config/reddit.yaml config/reddit-account2.yaml
nano config/reddit-account2.yaml  # 修改凭证
```

使用时指定配置文件（未来功能）。
