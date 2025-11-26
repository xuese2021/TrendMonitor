# 🚀 TrendMonitor 混合架构部署清单

按照此清单逐步完成部署，每完成一步打勾 ✅

---

## 📋 准备工作（5分钟）

- [ ] 注册 [Vercel](https://vercel.com) 账号（使用 GitHub 登录）
- [ ] 注册 [Railway](https://railway.app) 账号（使用 GitHub 登录）
- [ ] 确保已有 GitHub 账号并登录

---

## 第一部分：部署 RSSHub 到 Vercel（10分钟）

### Step 1: Fork RSSHub 仓库

- [ ] 1.1 打开浏览器，访问 https://github.com/DIYgod/RSSHub
- [ ] 1.2 点击页面右上角的 **Fork** 按钮
- [ ] 1.3 在弹出的页面中，保持默认设置，点击 **Create fork**
- [ ] 1.4 等待 fork 完成，你会被跳转到你自己的 RSSHub 仓库

### Step 2: 部署到 Vercel

- [ ] 2.1 打开新标签页，访问 https://vercel.com/dashboard
- [ ] 2.2 点击 **Add New...** 按钮，选择 **Project**
- [ ] 2.3 在 "Import Git Repository" 页面中，找到你刚刚 fork 的 **RSSHub** 仓库
- [ ] 2.4 点击 RSSHub 仓库右侧的 **Import** 按钮
- [ ] 2.5 在配置页面：
  - **Project Name**: 保持默认（或改为 `rsshub-yourname`）
  - **Framework Preset**: 自动检测为 Other
  - **Root Directory**: 保持默认 `./`
  - **Environment Variables**: 暂不配置（保持空白）
- [ ] 2.6 点击 **Deploy** 按钮
- [ ] 2.7 等待部署完成（约 2-3 分钟），看到 "🎉 Congratulations!" 页面

### Step 3: 获取 RSSHub URL

- [ ] 3.1 在部署成功页面，找到 **Domains** 部分
- [ ] 3.2 复制 URL（格式类似：`https://rsshub-xxxx.vercel.app`）
- [ ] 3.3 **保存此 URL**，记录到记事本或备忘录中
  ```
  我的 RSSHub URL: https://rsshub-xxxx.vercel.app
  ```

### Step 4: 测试 RSSHub

- [ ] 4.1 在浏览器新标签页访问：`你的RSSHub URL/weibo/search/hot`
  - 例如：`https://rsshub-xxxx.vercel.app/weibo/search/hot`
- [ ] 4.2 确认页面显示 XML 格式的微博热搜内容
- [ ] 4.3 ✅ 如果能看到内容，说明部署成功！

---

## 第二部分：部署 API Wrapper 到 Railway（8分钟）

### Step 5: 提交代码到 GitHub

- [ ] 5.1 打开命令行（PowerShell），切换到项目目录
  ```powershell
  cd f:\pachong\TrendMonitor
  ```

- [ ] 5.2 添加新文件到 Git
  ```powershell
  git add deployment/
  git add src/fetcher.py
  git add .github/workflows/daily_monitor.yml
  git add README.md
  ```

- [ ] 5.3 提交更改
  ```powershell
  git commit -m "Add hybrid architecture support"
  ```

- [ ] 5.4 推送到 GitHub
  ```powershell
  git push
  ```

### Step 6: 在 Railway 创建项目

- [ ] 6.1 打开浏览器，访问 https://railway.app/dashboard
- [ ] 6.2 点击 **New Project**
- [ ] 6.3 选择 **Deploy from GitHub repo**
- [ ] 6.4 如果首次使用，点击 **Configure GitHub App**，授权 Railway 访问你的仓库
- [ ] 6.5 在仓库列表中找到 **TrendMonitor**，点击
- [ ] 6.6 Railway 会自动开始部署

### Step 7: 配置 Railway 项目

- [ ] 7.1 部署开始后，点击你的服务（应该显示为 "TrendMonitor" 或 "web"）
- [ ] 7.2 点击 **Settings** 标签
- [ ] 7.3 向下滚动找到 **Root Directory** 设置
- [ ] 7.4 输入：`deployment/api_wrapper`
- [ ] 7.5 Railway 会自动重新部署（约 1-2 分钟）

### Step 8: 生成公开域名

- [ ] 8.1 在服务页面，点击 **Settings** 标签
- [ ] 8.2 找到 **Networking** 部分
- [ ] 8.3 点击 **Generate Domain** 按钮
- [ ] 8.4 等待域名生成（约 10 秒）
- [ ] 8.5 复制生成的 URL（格式类似：`https://xxx.railway.app`）
- [ ] 8.6 **保存此 URL**，记录到记事本
  ```
  我的 API Wrapper URL: https://xxx.railway.app
  ```

### Step 9: 测试 API Wrapper

- [ ] 9.1 在浏览器访问：`你的API URL/health`
  - 例如：`https://xxx.railway.app/health`
- [ ] 9.2 确认返回 JSON 格式数据，包含 `"status": "ok"`
- [ ] 9.3 测试微博接口：`你的API URL/api/weibo`
- [ ] 9.4 ✅ 如果返回微博热搜数据，说明部署成功！

---

## 第三部分：配置 GitHub Secrets（5分钟）

### Step 10: 添加 RSSHUB_URL

- [ ] 10.1 打开浏览器，访问你的 TrendMonitor GitHub 仓库
- [ ] 10.2 点击 **Settings** 标签（如果看不到，确认你是仓库所有者）
- [ ] 10.3 在左侧菜单中，点击 **Secrets and variables** → **Actions**
- [ ] 10.4 点击 **New repository secret** 按钮
- [ ] 10.5 填写：
  - **Name**: `RSSHUB_URL`（注意大写）
  - **Secret**: 粘贴你在 Step 3.3 保存的 RSSHub URL
- [ ] 10.6 点击 **Add secret**

### Step 11: 添加 API_WRAPPER_URL

- [ ] 11.1 继续在 Secrets 页面，点击 **New repository secret**
- [ ] 11.2 填写：
  - **Name**: `API_WRAPPER_URL`（注意大写）
  - **Secret**: 粘贴你在 Step 8.6 保存的 API Wrapper URL
- [ ] 11.3 点击 **Add secret**

### Step 12: 验证配置

- [ ] 12.1 在 Secrets 页面，确认看到以下 secrets：
  - ✅ `TELEGRAM_BOT_TOKEN`
  - ✅ `TELEGRAM_CHAT_ID`
  - ✅ `GEMINI_API_KEY`（可能有）
  - ✅ `RSSHUB_URL`（新添加）
  - ✅ `API_WRAPPER_URL`（新添加）

---

## 第四部分：测试验证（5分钟）

### Step 13: 手动触发 GitHub Actions

- [ ] 13.1 在 TrendMonitor 仓库页面，点击 **Actions** 标签
- [ ] 13.2 在左侧工作流列表中，点击 **Hourly Trend Monitor**
- [ ] 13.3 点击右侧的 **Run workflow** 下拉按钮
- [ ] 13.4 确认分支为 `main`，点击绿色的 **Run workflow** 按钮
- [ ] 13.5 等待几秒钟，刷新页面

### Step 14: 查看运行日志

- [ ] 14.1 在 Actions 页面，点击刚刚创建的运行记录（最上面的黄色或绿色点）
- [ ] 14.2 点击 **build** 任务
- [ ] 14.3 点击 **Run Monitor** 步骤展开日志
- [ ] 14.4 检查日志中是否出现：
  - ✅ `RSSHub URL: https://rsshub-xxxx.vercel.app`
  - ✅ `API Wrapper URL: https://xxx.railway.app`
  - ✅ `✓ Weibo: 使用 API Wrapper 成功` 或 `✓ Weibo: 直接抓取成功`
  - ✅ `✓ xxx: 使用自建 RSSHub 实例`
  - ✅ `成功抓取RSS: xxx`

### Step 15: 验证 Telegram 推送

- [ ] 15.1 等待 GitHub Actions 运行完成（约 2-5 分钟）
- [ ] 15.2 检查你的 Telegram 频道
- [ ] 15.3 ✅ 确认收到新的热点推送消息

---

## 第五部分：本地测试（可选，5分钟）

如果你想在本地验证配置：

### Step 16: 本地测试

- [ ] 16.1 打开 PowerShell，切换到项目目录
  ```powershell
  cd f:\pachong\TrendMonitor
  ```

- [ ] 16.2 设置环境变量
  ```powershell
  $env:RSSHUB_URL="你的RSSHub URL"
  $env:API_WRAPPER_URL="你的API Wrapper URL"
  $env:TELEGRAM_BOT_TOKEN="你的Bot Token"
  $env:TELEGRAM_CHAT_ID="你的Chat ID"
  ```

- [ ] 16.3 运行程序
  ```powershell
  python src/main.py
  ```

- [ ] 16.4 检查输出：
  - ✅ 看到 "RSSHub URL: ..." 
  - ✅ 看到 "API Wrapper URL: ..."
  - ✅ 看到数据抓取成功的日志
  - ✅ Telegram 收到推送

---

## 🎉 部署完成检查清单

完成所有步骤后，确认以下所有项目：

- [ ] ✅ RSSHub 在 Vercel 上运行正常
- [ ] ✅ API Wrapper 在 Railway 上运行正常
- [ ] ✅ GitHub Secrets 已正确配置（5个）
- [ ] ✅ GitHub Actions 运行成功
- [ ] ✅ Telegram 收到推送消息
- [ ] ✅ 日志显示使用了服务器端数据源

---

## 📊 预期效果对比

| 指标 | 部署前 | 部署后 |
|------|-------|--------|
| RSS 抓取成功率 | ~70% | **~95%** ✅ |
| 微博/知乎/百度稳定性 | 经常失败 | **显著提升** ✅ |
| IP 封锁问题 | 频繁遇到 | **几乎消失** ✅ |
| 响应速度 | - | **提升 30-50%** ✅ |

---

## ⚠️ 常见问题排查

### 问题 1: Railway 部署失败

**症状**: 部署日志显示错误

**解决**:
1. 检查 Root Directory 是否正确设置为 `deployment/api_wrapper`
2. 检查 `requirements.txt` 和 `Procfile` 是否存在
3. 查看详细日志，搜索错误关键词

### 问题 2: GitHub Actions 报错 "Health check failed"

**症状**: 日志中出现健康检查失败

**解决**:
1. 访问你的 API Wrapper URL，确认能访问
2. 检查 Railway 服务是否在运行中
3. 如果 Railway 冷启动，第一次可能超时，这是正常的

### 问题 3: Vercel RSSHub 无法访问

**症状**: 浏览器无法打开 RSSHub URL

**解决**:
1. 检查 Vercel 项目是否部署成功
2. 访问 Vercel Dashboard 查看项目状态
3. 确认域名已经生成并激活

### 问题 4: GitHub Actions 仍使用旧配置

**症状**: 日志中看不到 "RSSHub URL" 输出

**解决**:
1. 确认已经 `git push` 最新代码
2. 确认 GitHub Secrets 已正确添加
3. 重新触发 workflow

---

## 📞 需要帮助？

如果遇到其他问题：

1. 查看 **deployment/DEPLOYMENT_GUIDE.md** 获取更详细说明
2. 检查 Railway/Vercel 的部署日志
3. 查看 GitHub Actions 的完整日志
4. 访问各服务的 /health 接口测试连通性

---

**恭喜！你已经完成了 TrendMonitor 混合架构部署！** 🎊

现在系统会更稳定、更快速地为你抓取热点信息。
