## ADDED Requirements

### Requirement: Run on a daily schedule
The GitHub Actions workflow SHALL trigger on a daily cron schedule (`0 0 * * *` UTC) to check for new content.

#### Scenario: Daily trigger
- **WHEN** the cron schedule fires at midnight UTC
- **THEN** the workflow starts the scrape-translate-build-deploy pipeline

### Requirement: Support manual trigger
The workflow SHALL support `workflow_dispatch` for on-demand manual execution.

#### Scenario: Manual trigger
- **WHEN** a developer triggers the workflow manually from the GitHub Actions UI
- **THEN** the full pipeline runs identically to the scheduled trigger

### Requirement: Commit new content to repository
The workflow SHALL commit any new or updated translated Markdown files and the updated manifest back to the repository.

#### Scenario: New translations generated
- **WHEN** the scraper and translator produce new files
- **THEN** the workflow stages all changed files, commits with message `docs: sync new tips YYYY-MM-DD`, and pushes to the main branch

#### Scenario: No new content
- **WHEN** the scraper finds no new content and no files are changed
- **THEN** the workflow exits successfully without creating a commit

### Requirement: Build and deploy static site
The workflow SHALL build the VitePress site and deploy it to GitHub Pages after committing new content.

#### Scenario: Successful build and deploy
- **WHEN** new content has been committed (or a manual run is triggered)
- **THEN** the workflow runs `npm install` and `npm run docs:build`, then deploys the output to GitHub Pages

### Requirement: Secure API key handling
The workflow SHALL read LLM API keys from GitHub Secrets environment variables (`GEMINI_API_KEY`, `DEEPSEEK_API_KEY`) and MUST NOT log or expose them.

#### Scenario: API keys available
- **WHEN** the workflow runs with secrets configured
- **THEN** the scraper/translator scripts receive API keys via environment variables without them appearing in logs
