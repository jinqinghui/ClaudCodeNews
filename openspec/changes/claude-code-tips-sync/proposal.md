## Why

Claude Code's official documentation and community tips are primarily in English. Chinese-speaking developers need a reliable, automated way to access translated, up-to-date tips without manual effort. A serverless pipeline can deliver this at near-zero cost using GitHub Actions and free/low-cost LLM APIs.

## What Changes

- Add a Python scraper that monitors Claude Code documentation sources (official docs, GitHub repos, changelogs) for new content
- Add an LLM-powered translation engine that converts English tips to Chinese with accurate technical terminology
- Add a VitePress-based static site for browsing translated tips, deployed via GitHub Pages
- Add a GitHub Actions workflow that orchestrates the daily scrape-translate-publish pipeline
- Add content deduplication via file hashing to avoid redundant LLM calls

## Capabilities

### New Capabilities
- `content-scraper`: Fetches new tips/docs from Anthropic sources with change detection and deduplication
- `llm-translator`: Translates English content to Chinese using configurable LLM backends (Gemini/DeepSeek) with domain-aware prompts
- `static-site`: VitePress documentation site with date-organized tips and "view original" links
- `ci-pipeline`: GitHub Actions workflow for scheduled and manual scrape-translate-deploy cycles

### Modified Capabilities
<!-- No existing capabilities to modify - this is a greenfield project -->

## Impact

- **New dependencies**: Python (requests, BeautifulSoup), Node.js (VitePress), LLM API keys (Gemini, DeepSeek)
- **Infrastructure**: GitHub Actions (scheduled cron), GitHub Pages (static hosting)
- **External APIs**: Anthropic docs/GitHub API (read), Gemini API (translation primary), DeepSeek API (translation fallback)
- **Repository**: Adds `scripts/`, `docs/`, `.github/workflows/`, and configuration files
