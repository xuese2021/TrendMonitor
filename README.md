# TrendMonitor

一个实时热点监控应用，灵感来自 [TopList](https://github.com/tophubs/TopList) 和 [TrendRadar](https://github.com/sansan0/TrendRadar)。

## 功能特性
- 监控来自 **微博**、**知乎**、**百度**、**GitHub** 和 **36Kr** 的实时热点
- 支持**关键词过滤**，只推送您关心的内容
- 将更新推送到 **Telegram** 频道
- 通过 **GitHub Actions** 自动执行

## 快速开始

### 1. 配置关键词
编辑 `config/frequency_words.txt` 文件，添加您想监控的关键词：

```
# 普通关键词（匹配任意一个即可）
人工智能 AI ChatGPT

# 必须词语法：+词汇（必须同时包含）
华为 OPPO 小米 +发布

# 过滤词语法：!词汇（排除包含此词的结果）
苹果 华为 !水果 !价格

# 组合使用
比亚迪 特斯拉 +新能源 !广告
```

**语法说明：**
- **普通关键词**：标题包含任意一个词即匹配
- **必须词 `+词汇`**：必须同时包含普通词和必须词
- **过滤词 `!词汇`**：包含过滤词的新闻会被排除
- **注释**：以 `#` 开头的行会被忽略

### 2. 本地运行
1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 设置环境变量（可选，用于 Telegram 推送）：
   ```bash
   export TELEGRAM_BOT_TOKEN="your_bot_token"
   export TELEGRAM_CHAT_ID="your_chat_id"
   ```
3. 运行脚本：
   ```bash
   python src/main.py
   ```

### 3. GitHub Actions 部署
1. Fork 或推送此仓库到 GitHub
2. 进入 **Settings** > **Secrets and variables** > **Actions**
3. 添加以下仓库密钥：
   - `TELEGRAM_BOT_TOKEN`: 您的 Telegram Bot Token
   - `TELEGRAM_CHAT_ID`: 您的 Telegram Chat ID
4. 工作流将每天午夜 UTC 自动运行，或者您可以从 **Actions** 标签手动触发

## 项目结构
- `config/frequency_words.txt`: 关键词配置文件
- `src/fetcher.py`: 抓取热点的逻辑
- `src/notifier.py`: 发送 Telegram 消息的逻辑
- `src/main.py`: 程序入口
- `.github/workflows/daily_monitor.yml`: CI/CD 配置

## 示例配置

### 示例 1：监控科技新闻
```
人工智能 AI ChatGPT +技术
华为 小米 OPPO +手机
特斯拉 比亚迪 +汽车 !广告
```

### 示例 2：监控股市
```
A股 上证 深证 +涨跌 !预测
```

### 示例 3：监控体育赛事
```
世界杯 欧洲杯 亚洲杯 +比赛
```

## License
MIT
