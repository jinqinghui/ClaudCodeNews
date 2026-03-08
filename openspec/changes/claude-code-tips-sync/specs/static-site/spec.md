## ADDED Requirements

### Requirement: Generate a browsable documentation site
The system SHALL use VitePress to generate a static site from the Markdown files in `docs/`, producing an index page and individual tip pages.

#### Scenario: Build site with existing tips
- **WHEN** `npm run docs:build` is executed with tip files present in `docs/tips/`
- **THEN** VitePress produces a `docs/.vitepress/dist/` directory containing the static site with all tips rendered as HTML pages

### Requirement: Display tips in reverse chronological order
The site index page SHALL list all translated tips sorted by date in reverse chronological order (newest first).

#### Scenario: Multiple tips exist
- **WHEN** a user visits the site index page
- **THEN** tips are listed newest first based on the date in their frontmatter

### Requirement: Provide "view original" link
Each translated tip page SHALL include a link to the original English source document.

#### Scenario: User wants to verify translation
- **WHEN** a user views a translated tip page
- **THEN** a clearly visible link labeled "查看原文" (View Original) links to the `original_url` from frontmatter

### Requirement: Deploy to GitHub Pages
The built static site SHALL be deployable to GitHub Pages from the `docs/.vitepress/dist/` output directory.

#### Scenario: Deployment after build
- **WHEN** the CI pipeline triggers a deployment step after a successful build
- **THEN** the contents of `docs/.vitepress/dist/` are published to GitHub Pages and accessible via the repository's Pages URL
