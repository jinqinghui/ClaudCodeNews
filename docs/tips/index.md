---
title: 所有技巧
---

# 所有技巧

这里汇集了所有已翻译的 Claude Code 使用技巧。每篇技巧包含中文翻译内容、原文链接及发布日期。

<script setup>
import { data } from './tips.data.mts'
</script>

<div v-for="tip of data" :key="tip.url" style="margin-bottom: 1rem;">
  <a :href="tip.url" style="font-size: 1.1em; font-weight: 600;">{{ tip.title }}</a>
  <div style="color: var(--vp-c-text-2); font-size: 0.9em;">
    {{ tip.date }} · 来源: {{ tip.source }}
    · <a :href="tip.original_url" target="_blank">查看原文</a>
  </div>
</div>
