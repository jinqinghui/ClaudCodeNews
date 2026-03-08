项目名称：Claude-Code-Tips-Sync (CCTS)
状态：设计中

作者：Gemini (Collaborator)

目标：定时抓取 Claude Code 官方/社区最新技巧，通过 LLM 翻译，并发布为静态文档。

1. 摘要 (Abstract)
构建一个基于 GitHub Actions 的无服务器（Serverless）工作流，利用 LLM（Gemini/DeepSeek）将 Claude Code 的英文使用技巧翻译成中文，并使用静态网站生成器（SSG）进行展示，实现知识的零成本维护。

2. 系统架构 (Architecture)
数据源 (Source)：Anthropic 官方文档、GitHub 仓库或相关技术博客。

编排引擎 (Orchestrator)：GitHub Actions (Cron Trigger)。

核心逻辑 (Core Logic)：Python/Node.js 脚本（负责 Scrape + LLM Call）。

存储与展示 (Storage & UI)：Git 仓库存储 Markdown，GitHub Pages 展示。

3. 详细组件设计 (Detailed Design)
3.1 采集模块 (Scraper)
目标地址：假设为 Claude Code 的官方文档页面或其 GitHub 仓库的 README/Changelog。

技术选型：Python requests + BeautifulSoup 或直接使用 GitHub API 监听文件变更。

去重机制：通过文件哈希（MD5）或 Git Commit ID 判断是否为新内容，避免重复翻译消耗 Token。

3.2 翻译引擎 (LLM Translation)
API 选型：支持多模型切换（Gemini 1.5 Flash 速度快/成本低，DeepSeek-V3 编程理解强）。

Prompt 策略：

"你是一位资深的 Linux 性能工程师和开发者。请将以下关于 Claude Code 的技术技巧翻译成中文。要求：术语准确（如：context window 译为上下文窗口），保持 Markdown 格式，语气专业且简洁。"

3.3 文档索引与静态页面 (SSG)
技术选型：VitePress (推荐)。

理由：基于 Vue，性能极佳，对 Markdown 支持完美，非常适合做文档类索引。

结构：

Plaintext
/docs
  /tips
    2026-03-08-performance-tuning.md
  index.md
4. 工作流逻辑 (Workflow Logic)
YAML
name: Sync Claude Code Tips
on:
  schedule:
    - cron: '0 0 * * *' # 每天凌晨触发
  workflow_dispatch: # 支持手动触发

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Scraper & Translator
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
        run: |
          python scripts/sync_tips.py
          
      - name: Commit & Push
        run: |
          git config --global user.name "bot"
          git add .
          git commit -m "docs: sync new tips $(date +%F)" || exit 0
          git push
          
      - name: Build & Deploy to Pages
        run: |
          npm install
          npm run docs:build
          # 使用官方 action 部署到 GitHub Pages
5. 性能与成本考量 (Performance & Cost)
API 成本：Claude Code 的更新频率不高，预计每日 Token 消耗在 5k 以下。Gemini 1.5 Flash 的免费额度或低廉价格几乎可以忽略不计。

并发控制：GitHub Actions 串行执行即可，无需复杂的并发控制。

增量更新：仅对新增部分调用 LLM，节省成本。

6. 风险与对策 (Risks)
API 封禁/额度不足：设置多模型冗余（备选 DeepSeek）。

翻译质量异常：在静态页面提供“查看原文”链接，方便校对。

反爬虫：若官方文档有严格 WAF，改用 GitHub API 监控其文档仓库的 history。