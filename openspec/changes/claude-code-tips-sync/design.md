## Context

ClaudCodeNews is a greenfield project. There is no existing codebase—only a design document describing the desired system. The goal is to build an automated pipeline that scrapes Claude Code tips from English sources, translates them to Chinese via LLM APIs, and publishes them as a static documentation site.

Key constraints:
- Zero ongoing cost target (leverage free tiers: GitHub Actions, GitHub Pages, Gemini Flash free tier)
- Daily update cadence is sufficient given Claude Code's documentation update frequency
- Single-developer maintenance model—automation is critical

## Goals / Non-Goals

**Goals:**
- Fully automated daily scrape → translate → publish pipeline with no manual intervention
- Incremental processing: only new/changed content triggers LLM translation
- Multi-model LLM support with automatic fallback for resilience
- Clean, browsable documentation site with bilingual access (translated + original links)

**Non-Goals:**
- Real-time or near-real-time sync (daily cron is sufficient)
- Multi-language translation (Chinese only for v1)
- User accounts, comments, or interactive features
- Custom CMS or admin interface
- Mobile app

## Decisions

### 1. Python for scraper and translation scripts
**Choice**: Python with `requests` + `BeautifulSoup`
**Rationale**: Rich ecosystem for web scraping, simple HTTP clients for LLM APIs, widely understood. Node.js was considered but Python's scraping libraries are more mature.
**Alternative**: Node.js (Puppeteer/Cheerio) — rejected as overkill for mostly static content pages.

### 2. GitHub API for change detection over direct scraping
**Choice**: Prefer GitHub API to monitor documentation repo commits when possible; fall back to HTTP scraping + content hashing for non-GitHub sources.
**Rationale**: GitHub API provides structured change history (commit SHAs, file diffs) which is more reliable than scraping and hashing. Avoids WAF/anti-bot issues.
**Alternative**: Pure HTTP scraping — kept as fallback for non-GitHub sources.

### 3. Content hash (MD5) for deduplication
**Choice**: Store MD5 hashes of processed source content in a JSON manifest file committed to the repo.
**Rationale**: Simple, deterministic, no external database needed. The manifest file (`scripts/processed.json`) tracks what's been translated.
**Alternative**: SQLite — rejected as unnecessary complexity for low-volume data.

### 4. Gemini Flash as primary translator, DeepSeek as fallback
**Choice**: Gemini 1.5 Flash primary, DeepSeek-V3 secondary.
**Rationale**: Gemini Flash has a generous free tier and fast response times. DeepSeek has strong technical Chinese translation quality as a backup if Gemini quota is exhausted or unavailable.
**Alternative**: Single model — rejected for resilience.

### 5. VitePress for static site generation
**Choice**: VitePress
**Rationale**: Purpose-built for documentation, excellent Markdown support, fast builds, simple configuration. Deploys trivially to GitHub Pages.
**Alternative**: MkDocs (Python-native) — VitePress has better theming and search out of the box.

### 6. Date-prefixed file organization
**Choice**: Tips stored as `docs/tips/YYYY-MM-DD-<slug>.md`
**Rationale**: Natural chronological ordering, easy to browse, avoids naming conflicts, works well with VitePress sidebar auto-generation.

## Risks / Trade-offs

- **Source structure changes** → Scraper breaks silently. Mitigation: GitHub Actions will report non-zero exit codes; add basic validation that scraped content is non-empty before proceeding.
- **LLM translation quality variance** → Inaccurate technical terms. Mitigation: Include "view original" link on every translated page; use domain-specific prompt with terminology glossary.
- **API rate limits / quota exhaustion** → Pipeline fails mid-run. Mitigation: Dual-model fallback; incremental processing keeps daily token usage low (<5k tokens typically).
- **GitHub Actions minutes consumption** → Exceeds free tier. Mitigation: Pipeline is lightweight (Python script + npm build), estimated <5 minutes per run. Free tier allows 2,000 minutes/month.
