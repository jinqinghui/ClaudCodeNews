#!/bin/bash
# 一键启动本地预览

cd "$(dirname "$0")"

# 检查 node_modules 是否存在，不存在则安装依赖
if [ ! -d "node_modules" ]; then
  echo "正在安装依赖..."
  npm install
fi

echo "启动本地预览服务..."
npx vitepress dev docs --open
