import { useEffect } from 'react'

interface MetaProps {
  title?: string
  description?: string
  image?: string
  url?: string
}

export function useDocumentMeta({ title, description, image, url }: MetaProps) {
  useEffect(() => {
    // 1. Update Document Title
    const formattedTitle = title
      ? `${title} | BlackRose`
      : 'BlackRose — База знаний и сообщество Slayer Legend'
    document.title = formattedTitle

    // 2. Helper to set/update meta tag
    const setMeta = (selector: string, attr: string, value: string) => {
      let element = document.querySelector(selector)
      if (!element) {
        element = document.createElement('meta')
        const [attrName, attrVal] = selector.replace('meta[', '').replace(']', '').split('=')
        element.setAttribute(attrName, attrVal.replace(/"/g, ''))
        document.head.appendChild(element)
      }
      element.setAttribute(attr, value)
    }

    const defaultDesc =
      'Главная база знаний, калькуляторы билдов, тир-листы и гайды по Slayer Legend'
    const finalDesc = description || defaultDesc
    const finalUrl = url || window.location.href
    const finalImage = image || `${window.location.origin}/app-icon.png`

    // Standard Meta
    setMeta('meta[name="description"]', 'content', finalDesc)

    // OpenGraph Meta
    setMeta('meta[property="og:title"]', 'content', formattedTitle)
    setMeta('meta[property="og:description"]', 'content', finalDesc)
    setMeta('meta[property="og:url"]', 'content', finalUrl)
    setMeta('meta[property="og:image"]', 'content', finalImage)

    // Twitter Card Meta
    setMeta('meta[name="twitter:card"]', 'content', 'summary_large_image')
    setMeta('meta[name="twitter:title"]', 'content', formattedTitle)
    setMeta('meta[name="twitter:description"]', 'content', finalDesc)
    setMeta('meta[name="twitter:image"]', 'content', finalImage)
  }, [title, description, image, url])
}
