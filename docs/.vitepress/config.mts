import { defineConfig } from 'vitepress'
import fs from 'node:fs'
import path from 'node:path'
import matter from 'gray-matter'

function getTipsSidebar() {
  const tipsDir = path.resolve(__dirname, '../tips')
  if (!fs.existsSync(tipsDir)) return []

  const files = fs.readdirSync(tipsDir)
    .filter(f => f.endsWith('.md') && f !== 'index.md')
    .sort()
    .reverse() // 最新的排前面

  return files.map(f => {
    const content = fs.readFileSync(path.join(tipsDir, f), 'utf-8')
    const { data } = matter(content)
    const slug = f.replace(/\.md$/, '')
    return {
      text: data.title || slug,
      link: `/tips/${slug}`
    }
  })
}

export default defineConfig({
  title: 'Claude Code 技巧中文站',
  description: 'Claude Code 使用技巧的中文翻译与索引',
  base: process.env.CI ? '/ClaudCodeNews/' : '/',
  lang: 'zh-CN',
  srcExclude: ['design.md'],

  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
      { text: '所有技巧', link: '/tips/' }
    ],

    sidebar: [
      {
        text: '技巧列表',
        link: '/tips/',
        items: getTipsSidebar()
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/jqh9804/ClaudCodeNews' }
    ],

    outline: {
      label: '页面导航'
    },

    lastUpdated: {
      text: '最后更新于'
    },

    docFooter: {
      prev: '上一篇',
      next: '下一篇'
    }
  }
})
