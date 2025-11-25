# TrendMonitor

一个实时热点监控应用，灵感来自 [TopList](https://github.com/tophubs/TopList) 和 [TrendRadar](https://github.com/sansan0/TrendRadar)。

## 功能特性
- 监控来自 **微博**、**知乎**、**百度**、**GitHub** 和 **36Kr** 的实时热点
- 支持**关键词过滤**，只推送您关心的内容
- 将更新推送到 **Telegram** 频道
- 通过 **GitHub Actions** 自动执行
- 支持通过 **RSS** 自定义信息源
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

## Custom RSS Feeds via OPML

You can extend TrendMonitor with your own RSS sources by providing an **OPML** file. Place an `feeds.opml` file in the `config/` directory. The application will parse this file on startup and automatically generate the required `config/rss_feeds.txt` entries (`Name|URL|Enabled`). Enabled feeds are then fetched together with the built‑in sources.

## License
MIT
