import fs from 'node:fs'
import path from 'node:path'
import matter from 'gray-matter'

export default {
  watch: ['./**.md'],
  load() {
    const tipsDir = path.resolve(__dirname)
    const files = fs.readdirSync(tipsDir)
      .filter(f => f.endsWith('.md') && f !== 'index.md')
      .sort()
      .reverse()

    return files.map(f => {
      const content = fs.readFileSync(path.join(tipsDir, f), 'utf-8')
      const { data } = matter(content)
      const slug = f.replace(/\.md$/, '')
      return {
        title: data.title || slug,
        date: data.date || '',
        source: data.source || '',
        original_url: data.original_url || '',
        url: `/tips/${slug}`
      }
    })
  }
}
