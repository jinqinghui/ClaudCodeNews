---
title: "Claude Code overview - Claude Code Docs"
date: 2026-03-08
source: "anthropic-docs"
original_url: "https://docs.anthropic.com/en/docs/claude-code/overview"
---

# Claude Code overview - Claude Code Docs

[查看原文](https://docs.anthropic.com/en/docs/claude-code/overview)

## ​Get started

- Terminal
- VS Code
- Desktop app
- Web
- JetBrains
- Native Install (Recommended)
- Homebrew
- WinGet

```
curl -fsSL https://claude.ai/install.sh | bash

```


```
irm https://claude.ai/install.ps1 | iex

```


```
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd

```


```
brew install --cask claude-code

```


```
winget install Anthropic.ClaudeCode

```


```
cd your-project
claude

```

- Install for VS Code
- Install for Cursor
- macOS(Intel and Apple Silicon)
- Windows(x64)
- Windows ARM64(remote sessions only)

## ​What you can do

Automate the work you keep putting off


```
claude "write tests for the auth module, run them, and fix any failures"

```

Build features and fix bugs

Create commits and pull requests


```
claude "commit my changes with a descriptive message"

```

Connect your tools with MCP

Customize with instructions, skills, and hooks

Run agent teams and build custom agents

Pipe, script, and automate with the CLI


```
# Monitor logs and get alerted
tail -f app.log | claude -p "Slack me if you see any anomalies"

# Automate translations in CI
claude -p "translate new strings into French and raise a PR for review"

# Bulk operations across files
git diff main --name-only | claude -p "review these changed files for security issues"

```

Work from anywhere

- Step away from your desk and keep working from your phone or any browser withRemote Control
- Kick off a long-running task on theweboriOS app, then pull it into your terminal with/teleport
- Hand off a terminal session to theDesktop appwith/desktopfor visual diff review
- Route tasks from team chat: mention@ClaudeinSlackwith a bug report and get a pull request back

## ​Use Claude Code everywhere


## ​Next steps

- Quickstart: walk through your first real task, from exploring a codebase to committing a fix
- Store instructions and memories: give Claude persistent instructions with CLAUDE.md files and auto memory
- Common workflowsandbest practices: patterns for getting the most out of Claude Code
- Settings: customize Claude Code for your workflow
- Troubleshooting: solutions for common issues
- code.claude.com: demos, pricing, and product details
