/**
 * Core API response types and domain models
 */

export interface ApiResponse<T> {
  data?: T
  error?: string
  detail?: string
}

export interface AdminStats {
  guides: number
  categories: number
  views: number
  comments: number
}

export interface Guide {
  key: string
  title: string
  icon_url?: string
  icon?: string
  category_key: string
  views: number
  text?: string
  preview?: string
  created_at?: string
  updated_at?: string
  photo?: string[]
  video?: string[]
  document?: string[]
  has_photo?: boolean
  has_video?: boolean
  has_document?: boolean
  sort_order?: number
  tags?: string[]
  guide_links?: Record<string, unknown>
  icons?: Record<string, string>
}

export interface Category {
  key: string
  title: string
  icon?: string
  icon_url?: string
  sort_order: number
  count?: number
}

export interface GuideHistory {
  id: string
  action: 'create' | 'update' | 'delete' | 'import'
  changed_at: string
  changed_by?: string
  snapshot?: unknown
}

export interface AdminUser {
  id: number
  first_name: string
  is_admin: boolean
  is_local_admin: boolean
}

export interface TopGuidesResponse {
  results: Guide[]
}

export interface HistoryResponse {
  history: GuideHistory[]
}

export interface CategoriesResponse {
  categories: Category[]
}

export interface CategoryGuidesResponse {
  items: Guide[]
}

export interface Comment {
  id: string | number
  text: string
  created_at: string
  user_id: string | number
  first_name?: string
  username?: string
  guide_key?: string
  guide_title?: string
}

export interface CommentsResponse {
  comments: Comment[]
}

export interface TagsResponse {
  tags: string[]
}

export interface IconGroupResponse {
  id: string
  label: string
  icons: Array<{ key: string; url: string }>
}

// Backend returns IconGroupResponse[] directly (array, not wrapped)
export type IconsGroupedResponse = IconGroupResponse[]

export interface SubscriptionsResponse {
  subscriptions: string[]
}
