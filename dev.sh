#!/bin/bash
# 一键全流程：拉取内容 → 翻译 → 本地预览
set -e

cd "$(dirname "$0")"

# ---------- 颜色 ----------
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

step() { echo -e "\n${GREEN}▶ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠ $1${NC}"; }
fail() { echo -e "${RED}✗ $1${NC}"; exit 1; }

# ---------- 1. 检查 & 安装 Node 依赖 ----------
step "检查 Node 依赖..."
if [ ! -d "node_modules" ]; then
  npm install
else
  echo "  node_modules 已存在，跳过"
fi

# ---------- 2. 检查 & 安装 Python 依赖 ----------
step "检查 Python 依赖..."
if ! python3 -c "import requests, bs4, yaml" 2>/dev/null; then
  echo "  安装 Python 依赖..."
  pip3 install -r requirements.txt
else
  echo "  Python 依赖已就绪"
fi

# ---------- 3. 检查 API Key ----------
step "检查翻译 API Key..."
if [ -z "$GEMINI_API_KEY" ] && [ -z "$DEEPSEEK_API_KEY" ]; then
  warn "未设置 GEMINI_API_KEY 或 DEEPSEEK_API_KEY"
  warn "将跳过翻译（仅拉取内容）"
  SKIP_TRANSLATE=1
fi

# ---------- 4. 拉取 & 翻译 ----------
step "拉取新内容并翻译..."
if python3 scripts/sync_tips.py; then
  echo "  同步完成"
else
  warn "同步过程出现错误，继续启动预览..."
fi

# ---------- 5. 启动本地预览 ----------
step "启动本地预览服务..."
echo "  按 Ctrl+C 停止"
npx vitepress dev docs --open
