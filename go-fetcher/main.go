package main

import (
	"bufio"
	"encoding/json"
	"encoding/xml"
	"fmt"
	"html"
	"io"
	"log"
	"math/rand"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"
)

// RSS 结构
type RSS struct {
	Channel struct {
		Items []RSSItem `xml:"item"`
	} `xml:"channel"`
}

type Atom struct {
	Entries []AtomEntry `xml:"entry"`
}

type RSSItem struct {
	Title string `xml:"title"`
	Link  string `xml:"link"`
}

type AtomEntry struct {
	Title string   `xml:"title"`
	Link  AtomLink `xml:"link"`
}

type AtomLink struct {
	Href string `xml:"href,attr"`
}

// 历史记录
type HistoryItem struct {
	Title     string `json:"title"`
	URL       string `json:"url"`
	Timestamp string `json:"timestamp"`
}

// 抓取结果
type TrendItem struct {
	Title string `json:"title"`
	URL   string `json:"url"`
}

// User-Agent 池
var userAgents = []string{
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
	"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

// 备用 RSSHub 镜像（按稳定性排序）
var backupMirrors = []string{
	"https://rsshub.app",
}

var (
	primaryRSSHub   string
	currentMirrorIdx int
	httpClient      *http.Client
)

func init() {
	// 初始化 HTTP 客户端，带超时和连接池
	httpClient = &http.Client{
		Timeout: 30 * time.Second,
		Transport: &http.Transport{
			MaxIdleConns:        100,
			MaxIdleConnsPerHost: 10,
			IdleConnTimeout:     90 * time.Second,
		},
	}
	
	// 从环境变量获取主 RSSHub
	primaryRSSHub = os.Getenv("RSSHUB_URL")
	if primaryRSSHub == "" {
		primaryRSSHub = "https://rsshub.app"
	}
	
	rand.Seed(time.Now().UnixNano())
}

func getRandomUA() string {
	return userAgents[rand.Intn(len(userAgents))]
}

func getCurrentRSSHub() string {
	if currentMirrorIdx == 0 {
		return primaryRSSHub
	}
	if currentMirrorIdx <= len(backupMirrors) {
		return backupMirrors[currentMirrorIdx-1]
	}
	return primaryRSSHub
}

func switchToBackup() {
	currentMirrorIdx++
	if currentMirrorIdx > len(backupMirrors) {
		currentMirrorIdx = 0 // 回到主实例重试
	}
	log.Printf("🔄 Switching to mirror: %s", getCurrentRSSHub())
}

// 重置回主 RSSHub
func resetToPrimary() {
	currentMirrorIdx = 0
	log.Printf("🔄 Reset to primary RSSHub: %s", primaryRSSHub)
}

// 带重试的 HTTP 请求
func fetchWithRetry(url string, maxRetries int) ([]byte, error) {
	var lastErr error
	
	for attempt := 0; attempt < maxRetries; attempt++ {
		req, err := http.NewRequest("GET", url, nil)
		if err != nil {
			lastErr = err
			continue
		}
		
		req.Header.Set("User-Agent", getRandomUA())
		req.Header.Set("Accept", "application/xml, text/xml, */*")
		
		resp, err := httpClient.Do(req)
		if err != nil {
			lastErr = err
			log.Printf("⚠️ Attempt %d failed for %s: %v", attempt+1, url, err)
			time.Sleep(time.Duration(attempt+1) * 2 * time.Second)
			continue
		}
		
		if resp.StatusCode != 200 {
			resp.Body.Close()
			lastErr = fmt.Errorf("HTTP %d", resp.StatusCode)
			log.Printf("⚠️ Attempt %d returned %d for %s", attempt+1, resp.StatusCode, url)
			time.Sleep(time.Duration(attempt+1) * 2 * time.Second)
			continue
		}
		
		body, err := io.ReadAll(resp.Body)
		resp.Body.Close()
		if err != nil {
			lastErr = err
			continue
		}
		
		return body, nil
	}
	
	return nil, fmt.Errorf("all %d attempts failed: %v", maxRetries, lastErr)
}

// 解析 RSS/Atom
func parseRSS(data []byte) []TrendItem {
	var items []TrendItem
	
	// 尝试 RSS 格式
	var rss RSS
	if err := xml.Unmarshal(data, &rss); err == nil && len(rss.Channel.Items) > 0 {
		for i, item := range rss.Channel.Items {
			if i >= 10 {
				break
			}
			title := html.UnescapeString(strings.TrimSpace(item.Title))
			if title != "" {
				items = append(items, TrendItem{
					Title: title,
					URL:   strings.TrimSpace(item.Link),
				})
			}
		}
		return items
	}
	
	// 尝试 Atom 格式
	var atom Atom
	if err := xml.Unmarshal(data, &atom); err == nil && len(atom.Entries) > 0 {
		for i, entry := range atom.Entries {
			if i >= 10 {
				break
			}
			title := html.UnescapeString(strings.TrimSpace(entry.Title))
			if title != "" {
				items = append(items, TrendItem{
					Title: title,
					URL:   entry.Link.Href,
				})
			}
		}
	}
	
	return items
}

// 抓取单个 RSS 源
func fetchSingleRSS(name, rssURL string, useBackup bool) ([]TrendItem, error) {
	// 替换 RSSHub URL
	currentHub := getCurrentRSSHub()
	if strings.Contains(rssURL, "rsshub.app") {
		rssURL = strings.Replace(rssURL, "https://rsshub.app", currentHub, 1)
	}
	
	data, err := fetchWithRetry(rssURL, 3)
	if err != nil {
		// 如果主实例失败，尝试备用
		if !useBackup && strings.Contains(rssURL, currentHub) {
			switchToBackup()
			newURL := strings.Replace(rssURL, currentHub, getCurrentRSSHub(), 1)
			return fetchSingleRSS(name, newURL, true)
		}
		return nil, err
	}
	
	items := parseRSS(data)
	if len(items) == 0 {
		return nil, fmt.Errorf("no items parsed")
	}
	
	return items, nil
}

// 读取 RSS 配置
func loadRSSConfig(configPath string) (map[string]string, error) {
	file, err := os.Open(configPath)
	if err != nil {
		return nil, err
	}
	defer file.Close()
	
	feeds := make(map[string]string)
	scanner := bufio.NewScanner(file)
	
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		
		parts := strings.Split(line, "|")
		if len(parts) < 3 {
			continue
		}
		
		name := strings.TrimSpace(parts[0])
		url := strings.TrimSpace(parts[1])
		enabled := strings.ToLower(strings.TrimSpace(parts[2]))
		
		if enabled == "true" {
			feeds[name] = url
		}
	}
	
	return feeds, scanner.Err()
}

// 读取关键词
func loadKeywords(configPath string) [][]string {
	file, err := os.Open(configPath)
	if err != nil {
		log.Printf("No keywords file found: %v", err)
		return nil
	}
	defer file.Close()
	
	var keywords [][]string
	scanner := bufio.NewScanner(file)
	
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		words := strings.Fields(line)
		if len(words) > 0 {
			keywords = append(keywords, words)
		}
	}
	
	return keywords
}

// 关键词过滤
func matchKeywords(title string, keywordGroups [][]string) bool {
	if len(keywordGroups) == 0 {
		return true // 没有关键词配置，返回所有
	}
	
	titleLower := strings.ToLower(title)
	
	for _, group := range keywordGroups {
		matched := false
		excluded := false
		
		for _, word := range group {
			wordLower := strings.ToLower(word)
			
			if strings.HasPrefix(word, "!") {
				// 排除词
				if strings.Contains(titleLower, strings.ToLower(word[1:])) {
					excluded = true
					break
				}
			} else if strings.HasPrefix(word, "+") {
				// 必须词
				if !strings.Contains(titleLower, strings.ToLower(word[1:])) {
					matched = false
					break
				}
				matched = true
			} else {
				// 普通词（任意匹配）
				if strings.Contains(titleLower, wordLower) {
					matched = true
				}
			}
		}
		
		if matched && !excluded {
			return true
		}
	}
	
	return false
}

// 读取历史记录
func loadHistory(historyPath string) map[string]bool {
	history := make(map[string]bool)
	
	data, err := os.ReadFile(historyPath)
	if err != nil {
		return history
	}
	
	var items []HistoryItem
	if err := json.Unmarshal(data, &items); err != nil {
		return history
	}
	
	for _, item := range items {
		history[item.URL] = true
	}
	
	return history
}

// 保存历史记录
func saveHistory(historyPath string, newItems []TrendItem, existingHistory map[string]bool) error {
	// 读取现有历史
	var items []HistoryItem
	data, err := os.ReadFile(historyPath)
	if err == nil {
		json.Unmarshal(data, &items)
	}
	
	// 添加新项目
	now := time.Now().Format(time.RFC3339)
	for _, item := range newItems {
		if !existingHistory[item.URL] {
			items = append(items, HistoryItem{
				Title:     item.Title,
				URL:       item.URL,
				Timestamp: now,
			})
		}
	}
	
	// 只保留最近 1000 条
	if len(items) > 1000 {
		items = items[len(items)-1000:]
	}
	
	newData, err := json.MarshalIndent(items, "", "  ")
	if err != nil {
		return err
	}
	
	return os.WriteFile(historyPath, newData, 0644)
}

// 发送 Telegram 消息
func sendTelegram(token, chatID, message string) error {
	apiURL := fmt.Sprintf("https://api.telegram.org/bot%s/sendMessage", token)
	
	data := url.Values{}
	data.Set("chat_id", chatID)
	data.Set("text", message)
	data.Set("parse_mode", "Markdown")
	data.Set("disable_web_page_preview", "true")
	
	resp, err := http.PostForm(apiURL, data)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != 200 {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("telegram error: %s", string(body))
	}
	
	return nil
}

// 格式化消息
func formatMessage(items []TrendItem) string {
	var sb strings.Builder
	
	for i, item := range items {
		// 转义 Markdown 特殊字符
		title := strings.ReplaceAll(item.Title, "[", "\\[")
		title = strings.ReplaceAll(title, "]", "\\]")
		
		sb.WriteString(fmt.Sprintf("%d. [%s](%s)\n\n", i+1, title, item.URL))
	}
	
	return sb.String()
}

// 预热 RSSHub（等待冷启动）
func warmupRSSHub() {
	log.Printf("🔥 Warming up RSSHub: %s", primaryRSSHub)
	
	// Railway 免费版冷启动可能需要 60 秒
	// 创建一个专门用于预热的客户端，超时更长
	warmupClient := &http.Client{
		Timeout: 90 * time.Second,
	}
	
	// 尝试 3 次预热
	for attempt := 1; attempt <= 3; attempt++ {
		log.Printf("🔄 Warmup attempt %d/3...", attempt)
		
		req, _ := http.NewRequest("GET", primaryRSSHub, nil)
		req.Header.Set("User-Agent", getRandomUA())
		
		resp, err := warmupClient.Do(req)
		if err != nil {
			log.Printf("⚠️ Warmup attempt %d failed: %v", attempt, err)
			if attempt < 3 {
				time.Sleep(10 * time.Second)
			}
			continue
		}
		resp.Body.Close()
		
		if resp.StatusCode == 200 {
			log.Println("✅ RSSHub warmup successful!")
			return
		}
		
		log.Printf("⚠️ Warmup returned %d", resp.StatusCode)
		if attempt < 3 {
			time.Sleep(10 * time.Second)
		}
	}
	
	log.Printf("⚠️ Primary RSSHub warmup failed after 3 attempts, will try backup if needed")
}

func main() {
	startTime := time.Now()
	log.Println("🚀 Go TrendMonitor Starting...")
	log.Println("=" + strings.Repeat("=", 50))
	
	// 显示配置
	log.Printf("📡 Primary RSSHub: %s", primaryRSSHub)
	log.Printf("📡 Backup mirrors: %v", backupMirrors)
	log.Println("=" + strings.Repeat("=", 50))
	
	// 获取项目根目录
	execPath, _ := os.Executable()
	projectRoot := filepath.Dir(filepath.Dir(execPath))
	
	// 如果是 go run，使用当前目录
	if strings.Contains(execPath, "go-build") {
		projectRoot, _ = os.Getwd()
		projectRoot = filepath.Dir(projectRoot)
	}
	
	// GitHub Actions 环境
	if os.Getenv("GITHUB_WORKSPACE") != "" {
		projectRoot = os.Getenv("GITHUB_WORKSPACE")
	}
	
	// 配置文件路径
	rssConfigPath := filepath.Join(projectRoot, "config", "rss_feeds.txt")
	keywordsPath := filepath.Join(projectRoot, "config", "frequency_words.txt")
	historyPath := filepath.Join(projectRoot, "data", "history.json")
	
	// 环境变量
	telegramToken := os.Getenv("TELEGRAM_BOT_TOKEN")
	telegramChatID := os.Getenv("TELEGRAM_CHAT_ID")
	
	// 预热 RSSHub
	warmupRSSHub()
	
	// 加载配置
	feeds, err := loadRSSConfig(rssConfigPath)
	if err != nil {
		log.Fatalf("❌ Failed to load RSS config: %v", err)
	}
	log.Printf("📋 Loaded %d RSS feeds", len(feeds))
	
	keywords := loadKeywords(keywordsPath)
	log.Printf("🔑 Loaded %d keyword groups", len(keywords))
	
	history := loadHistory(historyPath)
	log.Printf("📜 Loaded %d history items", len(history))
	
	// 并发抓取
	var wg sync.WaitGroup
	var mu sync.Mutex
	results := make(map[string][]TrendItem)
	successCount := 0
	failCount := 0
	
	// 限制并发数
	semaphore := make(chan struct{}, 5)
	
	for name, rssURL := range feeds {
		wg.Add(1)
		go func(name, url string) {
			defer wg.Done()
			semaphore <- struct{}{}
			defer func() { <-semaphore }()
			
			// 随机延迟
			time.Sleep(time.Duration(rand.Intn(1000)) * time.Millisecond)
			
			items, err := fetchSingleRSS(name, url, false)
			if err != nil {
				mu.Lock()
				failCount++
				mu.Unlock()
				log.Printf("❌ %s failed: %v", name, err)
				return
			}
			
			mu.Lock()
			results[name] = items
			successCount++
			mu.Unlock()
			log.Printf("✅ %s: %d items", name, len(items))
		}(name, rssURL)
	}
	
	wg.Wait()
	
	log.Printf("📊 Fetch complete: %d success, %d failed", successCount, failCount)
	
	// 过滤和去重
	var allItems []TrendItem
	for _, items := range results {
		for _, item := range items {
			// 关键词过滤
			if !matchKeywords(item.Title, keywords) {
				continue
			}
			// 去重
			if history[item.URL] {
				continue
			}
			allItems = append(allItems, item)
		}
	}
	
	log.Printf("📰 %d new items after filtering", len(allItems))
	
	// 发送 Telegram
	if telegramToken != "" && telegramChatID != "" && len(allItems) > 0 {
		// 分批发送（每批 10 条）
		batchSize := 10
		for i := 0; i < len(allItems); i += batchSize {
			end := i + batchSize
			if end > len(allItems) {
				end = len(allItems)
			}
			
			batch := allItems[i:end]
			message := formatMessage(batch)
			
			if err := sendTelegram(telegramToken, telegramChatID, message); err != nil {
				log.Printf("❌ Telegram send failed: %v", err)
			} else {
				log.Printf("✅ Sent batch %d-%d", i+1, end)
			}
			
			// 间隔 3 秒
			if end < len(allItems) {
				time.Sleep(3 * time.Second)
			}
		}
		
		// 保存历史
		if err := saveHistory(historyPath, allItems, history); err != nil {
			log.Printf("❌ Failed to save history: %v", err)
		}
	} else if len(allItems) == 0 {
		log.Println("📭 No new items to send")
	} else {
		log.Println("⚠️ Telegram not configured, dry run mode")
		for i, item := range allItems {
			if i >= 10 {
				log.Printf("... and %d more items", len(allItems)-10)
				break
			}
			log.Printf("  %d. %s", i+1, item.Title)
		}
	}
	
	elapsed := time.Since(startTime)
	log.Printf("⏱️ Completed in %v", elapsed)
}

