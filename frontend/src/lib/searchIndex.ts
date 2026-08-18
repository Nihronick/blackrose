import MiniSearch from 'minisearch'
import type { Guide } from './types'

export interface SearchDoc {
  id: string
  key: string
  title: string
  preview: string
  category_key: string
  text?: string
}

let miniSearchInstance: MiniSearch<SearchDoc> | null = null
const indexedDocsMap = new Map<string, SearchDoc>()

export function getSearchIndex(): MiniSearch<SearchDoc> {
  if (!miniSearchInstance) {
    miniSearchInstance = new MiniSearch<SearchDoc>({
      fields: ['title', 'preview', 'category_key', 'text'],
      storeFields: ['id', 'key', 'title', 'preview', 'category_key'],
      searchOptions: {
        boost: { title: 3, preview: 1.5, text: 1 },
        fuzzy: 0.25,
        prefix: true,
      },
    })
  }
  return miniSearchInstance
}

export function indexGuides(guides: Guide[]): void {
  const index = getSearchIndex()
  const newDocs: SearchDoc[] = []

  for (const g of guides) {
    if (!g.key) continue
    const doc: SearchDoc = {
      id: g.key,
      key: g.key,
      title: g.title || '',
      preview: g.preview || '',
      category_key: g.category_key || '',
      text: (g as any).text || '',
    }

    if (indexedDocsMap.has(g.key)) {
      try {
        index.discard(g.key)
      } catch {
        // ignore if not found
      }
    }
    indexedDocsMap.set(g.key, doc)
    newDocs.push(doc)
  }

  if (newDocs.length > 0) {
    index.addAll(newDocs)
  }
}

export function searchGuidesClient(query: string, maxResults = 30): SearchDoc[] {
  if (!query || query.trim().length < 2) {
    return []
  }

  const index = getSearchIndex()
  const results = index.search(query.trim(), {
    fuzzy: (term) => (term.length > 3 ? 0.25 : 0),
    prefix: true,
    combineWith: 'OR',
  })

  return results.slice(0, maxResults).map((r) => {
    const cached = indexedDocsMap.get(r.id)
    return (
      cached || {
        id: r.id,
        key: r.id,
        title: (r as any).title || r.id,
        preview: (r as any).preview || '',
        category_key: (r as any).category_key || '',
      }
    )
  })
}
