# TrendMonitor API Wrapper

API代理服务，为容易被封IP的数据源提供缓存和稳定访问。

## 功能

- ✅ 微博热搜代理
- ✅ 知乎热榜代理  
- ✅ 百度热搜代理
- ✅ 5分钟内存缓存
- ✅ 健康检查端点

## 本地测试

```bash
# 安装依赖
pip install -r requirements.txt

# 运行服务
python api_wrapper.py

# 测试
curl http://localhost:8000/health
curl http://localhost:8000/api/weibo
```

## 部署到 Railway

1. 访问 [Railway](https://railway.app)
2. 点击 "New Project" → "Deploy from GitHub repo"
3. 选择此项目，Railway 会自动检测 Procfile
4. 部署完成后获取 URL（例如：`https://your-app.railway.app`）

## 部署到 Render

1. 访问 [Render](https://render.com)
2. 点击 "New" → "Web Service"
3. 连接 GitHub 仓库
4. 配置：
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn api_wrapper:app`
5. 部署完成后获取 URL

## API 端点

### GET /health
健康检查

**响应示例：**
```json
{
  "status": "ok",
  "timestamp": 1732604321.123,
  "cache_size": 3
}
```

### GET /api/weibo
获取微博热搜

**响应示例：**
```json
{
  "success": true,
  "data": [
    {
      "title": "热搜标题",
      "url": "https://s.weibo.com/..."
    }
  ],
  "count": 15,
  "timestamp": 1732604321.123
}
```

### GET /api/zhihu
获取知乎热榜

### GET /api/baidu
获取百度热搜

## 环境变量

无需配置环境变量，开箱即用。

## 性能

- **缓存时长**：5分钟
- **超时设置**：10秒
- **并发支持**：由Gunicorn提供多进程支持
