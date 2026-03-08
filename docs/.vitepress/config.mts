import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Claude Code 技巧中文站',
  description: 'Claude Code 使用技巧的中文翻译与索引',
  base: '/ClaudCodeNews/',
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
