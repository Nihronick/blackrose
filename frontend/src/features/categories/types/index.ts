export interface Category {
  key: string
  title: string
  icon?: string
  icon_url?: string
  count?: number
}

export interface SearchResult {
  key: string
  title: string
  icon?: string
  category_key: string
  tags?: string[]
}
