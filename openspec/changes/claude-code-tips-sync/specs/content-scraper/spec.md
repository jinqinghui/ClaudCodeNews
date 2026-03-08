## ADDED Requirements

### Requirement: Fetch content from documentation sources
The scraper SHALL fetch content from configured documentation source URLs (Anthropic official docs, GitHub repositories, changelogs). The list of source URLs SHALL be configurable via a YAML configuration file.

#### Scenario: Fetch from a valid documentation URL
- **WHEN** the scraper runs against a configured source URL that returns HTTP 200
- **THEN** the scraper extracts the main content body as Markdown text

#### Scenario: Source URL is unreachable
- **WHEN** the scraper runs against a source URL that returns a non-200 status or times out
- **THEN** the scraper logs an error for that source and continues processing remaining sources

### Requirement: Detect new or changed content
The scraper SHALL compare fetched content against a local manifest (`scripts/processed.json`) using MD5 hashes to determine if content is new or changed.

#### Scenario: New content detected
- **WHEN** fetched content has an MD5 hash not present in the manifest
- **THEN** the scraper marks the content for translation and adds its hash to the manifest

#### Scenario: Content unchanged
- **WHEN** fetched content has an MD5 hash already present in the manifest
- **THEN** the scraper skips that content and does not invoke the translation engine

### Requirement: Support GitHub API as a source
The scraper SHALL support monitoring a GitHub repository's file changes via the GitHub API (commits endpoint) as an alternative to HTTP scraping.

#### Scenario: New commit changes documentation files
- **WHEN** the GitHub API reports commits since the last recorded commit SHA that modify documentation files
- **THEN** the scraper fetches the updated file contents and processes them as new content

#### Scenario: No new commits
- **WHEN** the GitHub API reports no new commits since the last recorded SHA
- **THEN** the scraper takes no action for that source

### Requirement: Output structured content for translation
The scraper SHALL output each new content item as a structured object containing: source URL, title, original Markdown content, and fetch timestamp.

#### Scenario: Content ready for translation
- **WHEN** the scraper identifies new content
- **THEN** it produces a JSON object with fields `source_url`, `title`, `content_md`, and `fetched_at`
