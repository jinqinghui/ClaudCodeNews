## 1. Project Setup

- [x] 1.1 Initialize Node.js project with `package.json` and add VitePress as a dev dependency
- [x] 1.2 Create Python virtual environment setup and `requirements.txt` with `requests`, `beautifulsoup4`
- [x] 1.3 Create project configuration file (`scripts/config.yaml`) with source URLs, LLM settings, and output paths
- [x] 1.4 Create empty manifest file (`scripts/processed.json`) for content deduplication tracking

## 2. Content Scraper

- [x] 2.1 Implement base scraper module (`scripts/scraper.py`) with HTTP fetching, error handling, and Markdown extraction
- [x] 2.2 Implement GitHub API source support with commit SHA tracking for change detection
- [x] 2.3 Implement MD5-based deduplication against `scripts/processed.json` manifest
- [x] 2.4 Implement structured output (JSON objects with `source_url`, `title`, `content_md`, `fetched_at`)

## 3. LLM Translation Engine

- [x] 3.1 Implement translator module (`scripts/translator.py`) with domain-specific system prompt and Markdown-preserving translation
- [x] 3.2 Implement Gemini API backend with API key from environment variable
- [x] 3.3 Implement DeepSeek API backend as fallback
- [x] 3.4 Implement multi-backend fallback logic (try primary, fall back to secondary, log failures)
- [x] 3.5 Implement translated Markdown file writer with YAML frontmatter (`title`, `date`, `source`, `original_url`) and date-slug naming

## 4. Pipeline Orchestrator

- [x] 4.1 Create main pipeline script (`scripts/sync_tips.py`) that chains scraper → translator → file writer
- [x] 4.2 Update `scripts/processed.json` manifest after successful translation

## 5. Static Site (VitePress)

- [x] 5.1 Initialize VitePress config (`docs/.vitepress/config.js`) with site title, theme, and sidebar
- [x] 5.2 Create `docs/index.md` landing page with reverse-chronological tip listing
- [x] 5.3 Add "查看原文" (View Original) link component/template for translated tip pages
- [x] 5.4 Add `docs:dev` and `docs:build` npm scripts

## 6. CI/CD Pipeline

- [x] 6.1 Create GitHub Actions workflow file (`.github/workflows/sync-tips.yml`) with daily cron and `workflow_dispatch` triggers
- [x] 6.2 Add scraper + translator step with `GEMINI_API_KEY` and `DEEPSEEK_API_KEY` from secrets
- [x] 6.3 Add git commit + push step for new translated content (skip if no changes)
- [x] 6.4 Add VitePress build + GitHub Pages deploy step

## 7. Testing & Validation

- [x] 7.1 Add unit tests for scraper deduplication and content extraction
- [x] 7.2 Add unit tests for translator prompt formatting and file output
- [x] 7.3 Manual end-to-end test: run pipeline locally, verify site builds and renders tips correctly
