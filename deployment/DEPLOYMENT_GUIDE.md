# 混合架构部署指南

本指南将帮助你部署 TrendMonitor 的混合架构：RSSHub + API Wrapper + GitHub Actions。

---

## 📋 前置准备

- GitHub 账号
- [Vercel](https://vercel.com) 账号（免费）
- [Railway](https://railway.app) 或 [Render](https://render.com) 账号（免费）

---

## 第一步：部署 RSSHub 到 Vercel

### 1.1 Fork RSSHub 仓库

1. 访问 [RSSHub GitHub](https://github.com/DIYgod/RSSHub)
2. 点击右上角 **Fork** 按钮，将仓库 fork 到你的账号

### 1.2 部署到 Vercel

1. 访问 [Vercel Dashboard](https://vercel.com/dashboard)
2. 点击 **Add New... → Project**
3. 从你的 GitHub 仓库列表中选择 **RSSHub**
4. 点击 **Import**
5. 无需修改配置，直接点击 **Deploy**
6. 等待部署完成（约 2-3 分钟）
7. 部署成功后，获取 URL（例如：`https://rsshub-yourname.vercel.app`）

### 1.3 测试 RSSHub

在浏览器访问：
```
https://rsshub-yourname.vercel.app/weibo/search/hot
```

如果看到 RSS 内容，说明部署成功！

---

## 第二步：部署 API Wrapper 到 Railway

### 2.1 创建 GitHub 仓库（可选）

如果你想单独管理 API Wrapper：

1. 在 GitHub 创建新仓库（例如：`trendmonitor-api-wrapper`）
2. 将 `deployment/api_wrapper` 文件夹内容推送到新仓库

**或者**直接使用 TrendMonitor 仓库的 `deployment/api_wrapper` 子目录。

### 2.2 部署到 Railway

1. 访问 [Railway](https://railway.app)
2. 点击 **New Project**
3. 选择 **Deploy from GitHub repo**
4. 选择你的仓库（TrendMonitor 或单独的 api-wrapper 仓库）
5. **重要**：如果使用 TrendMonitor 仓库，需要配置 Root Directory：
   - 点击 **Settings** → **Service**
   - 找到 **Root Directory**
   - 设置为 `deployment/api_wrapper`
6. Railway 会自动检测 `Procfile` 并部署
7. 等待部署完成（约 1-2 分钟）
8. 在 **Settings** → **Networking** 中生成 Public Domain
9. 获取 URL（例如：`https://your-api.railway.app`）

### 2.3 测试 API Wrapper

在浏览器或命令行访问：
```bash
curl https://your-api.railway.app/health
curl https://your-api.railway.app/api/weibo
```

如果返回 JSON 数据，说明部署成功！

### 2.4 备选方案：部署到 Render

如果 Railway 免费额度用完，可以使用 Render：

1. 访问 [Render Dashboard](https://dashboard.render.com)
2. 点击 **New → Web Service**
3. 连接 GitHub 仓库
4. 配置：
   - **Name**: `trendmonitor-api`
   - **Root Directory**: `deployment/api_wrapper`（如果需要）
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn api_wrapper:app`
   - **Plan**: Free
5. 点击 **Create Web Service**
6. 等待部署完成，获取 URL

> ⚠️ **注意**：Render 免费版有冷启动（15分钟无请求后会休眠），首次请求可能较慢。

---

## 第三步：配置 GitHub Secrets

在你的 TrendMonitor 仓库中配置环境变量：

1. 进入仓库 **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**，添加以下两个 secret：

### Secret 1: RSSHUB_URL
- **Name**: `RSSHUB_URL`
- **Value**: `https://rsshub-yourname.vercel.app`（替换为你的 Vercel URL）

### Secret 2: API_WRAPPER_URL（可选）
- **Name**: `API_WRAPPER_URL`
- **Value**: `https://your-api.railway.app`（替换为你的 Railway URL）

> 💡 **提示**：如果不配置 `API_WRAPPER_URL`，系统会自动使用直接抓取作为备份。

---

## 第四步：测试部署

### 4.1 本地测试（可选）

```bash
cd f:\pachong\TrendMonitor

# 设置环境变量
$env:RSSHUB_URL="https://rsshub-yourname.vercel.app"
$env:API_WRAPPER_URL="https://your-api.railway.app"

# 运行测试
python src/main.py
```

查看输出日志，确认：
- ✅ 出现 "RSSHub URL: https://rsshub-yourname.vercel.app"
- ✅ 出现 "API Wrapper URL: https://your-api.railway.app"
- ✅ 看到 "✓ Weibo: 使用 API Wrapper 成功" 或 "✓ Weibo: 直接抓取成功"

### 4.2 GitHub Actions 测试

1. 进入仓库 **Actions** 页面
2. 选择 **Hourly Trend Monitor** 工作流
3. 点击 **Run workflow** → **Run workflow**
4. 等待运行完成（约 2-5 分钟）
5. 点击运行记录，查看日志
6. 确认：
   - ✅ 没有错误
   - ✅ Telegram 收到推送
   - ✅ `data/history.json` 被更新

---

## 🎉 部署完成！

现在你的 TrendMonitor 已经使用混合架构运行：

- **RSSHub**：~50 个 RSS 源由你的私有 Vercel 实例提供
- **API Wrapper**：微博、知乎、百度等平台通过服务器代理抓取
- **GitHub Actions**：定时调度、数据聚合、Telegram 推送

---

## 📊 监控与维护

### 检查服务状态

定期访问以下 URL 确认服务正常：

```bash
# RSSHub 健康检查
https://rsshub-yourname.vercel.app/

# API Wrapper 健康检查
https://your-api.railway.app/health
```

### 查看 Railway 使用情况

- 访问 [Railway Dashboard](https://railway.app/dashboard)
- 查看 **Usage** 标签
- 免费额度：500 小时/月，每月重置

### Vercel 使用情况

- 访问 [Vercel Dashboard](https://vercel.com/dashboard)
- 免费额度：无限制（有带宽和调用限制，但对个人使用足够）

---

## ⚠️ 故障排查

### RSSHub 返回 429 错误
- **原因**：请求过于频繁
- **解决**：在 Vercel 项目设置中配置环境变量 `CACHE_EXPIRE=3600`（缓存 1 小时）

### API Wrapper 冷启动慢（Render）
- **原因**：Render 免费版会休眠
- **解决**：使用 [UptimeRobot](https://uptimerobot.com) 每 5 分钟 ping 一次保持唤醒

### GitHub Actions 报错 "Health check failed"
- **原因**：服务器不可访问
- **解决**：检查 Railway/Vercel 是否正常运行，查看日志

### 微博/知乎仍然被封
- **原因**：API Wrapper 所在服务器 IP 也被封
- **解决**：系统会自动回退到直接抓取（可能成功率较低）

---

## 🚀 进阶优化

### 1. 添加多个 RSSHub 实例（高可用）

在不同平台部署 RSSHub 备份：
- Vercel（主）
- Netlify（备）
- Cloudflare Pages（备）

修改 `fetcher.py` 实现自动切换。

### 2. 使用 Redis 缓存（Railway）

Railway 提供免费 Redis 插件，可以提升 API Wrapper 性能。

### 3. 添加监控告警

使用 [UptimeRobot](https://uptimerobot.com)：
- 监控 RSSHub 和 API Wrapper
- 宕机时发送邮件/Telegram 通知

---

## 📞 需要帮助？

如果遇到问题，请检查：
1. GitHub Actions 运行日志
2. Railway/Render 部署日志
3. Vercel 部署日志

常见日志关键词：
- ✅ 成功：`✓ Weibo: 使用 API Wrapper 成功`
- ⚠️ 回退：`API Wrapper 失败，回退到直接抓取`
- ❌ 错误：`Error fetching`
