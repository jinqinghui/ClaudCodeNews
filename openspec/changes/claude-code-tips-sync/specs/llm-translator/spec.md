## ADDED Requirements

### Requirement: Translate content to Chinese
The translator SHALL accept Markdown content in English and return a Chinese translation that preserves all Markdown formatting, code blocks, and inline code.

#### Scenario: Translate a tip with code blocks
- **WHEN** the translator receives English Markdown containing fenced code blocks
- **THEN** it returns Chinese translation with code blocks unchanged and surrounding text translated

#### Scenario: Translate plain text tip
- **WHEN** the translator receives English Markdown with no code blocks
- **THEN** it returns a fully translated Chinese Markdown document

### Requirement: Use domain-specific translation prompt
The translator SHALL use a system prompt that instructs the LLM to maintain accurate technical terminology (e.g., "context window" → "上下文窗口") and preserve a professional, concise tone.

#### Scenario: Technical term accuracy
- **WHEN** the source content contains technical terms like "context window", "token", "prompt"
- **THEN** the translated output uses standard Chinese technical translations for those terms

### Requirement: Support multiple LLM backends
The translator SHALL support at least two LLM backends (Gemini and DeepSeek) configurable via environment variables. The primary backend SHALL be attempted first.

#### Scenario: Primary backend succeeds
- **WHEN** the primary LLM backend (Gemini) returns a successful response
- **THEN** the translator uses that response and does not call the fallback

#### Scenario: Primary backend fails, fallback succeeds
- **WHEN** the primary LLM backend returns an error or times out
- **THEN** the translator retries with the fallback backend (DeepSeek) and uses its response

#### Scenario: All backends fail
- **WHEN** both primary and fallback backends fail
- **THEN** the translator raises an error and logs the failure, skipping that content item

### Requirement: Output translated Markdown files
The translator SHALL write each translated document as a Markdown file to `docs/tips/` with the naming convention `YYYY-MM-DD-<slug>.md`, including YAML frontmatter with title, date, source URL, and original language link.

#### Scenario: Write translated file
- **WHEN** translation completes successfully
- **THEN** a file is created at `docs/tips/YYYY-MM-DD-<slug>.md` with frontmatter containing `title`, `date`, `source`, and `original_url` fields
