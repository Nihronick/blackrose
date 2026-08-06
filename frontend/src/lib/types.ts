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

export interface MediaItem {
  url: string
  name: string
  type: 'image' | 'video'
}

export interface MediaGroup {
  id: string
  label: string
  items: MediaItem[]
}

export interface MediaListResponse {
  groups: MediaGroup[]
  total: number
}

// --- Guild System ---

export type GlobalRole = 'project_admin' | 'admin' | 'editor' | 'moderator' | 'member'
export type GuildRole = 'guild_master' | 'guild_vice_master' | 'guild_member'
export type MemberStatus = 'active' | 'trial' | 'left' | 'reserve' | string

export interface Guild {
  id: number
  name: string
  icon_url?: string
  description?: string
  max_members: number
  member_count: number
  is_active: boolean
}

export interface GuildMember {
  id: number
  guild_id: number
  user_id: number
  nickname: string
  rank: number
  rank_confirmed: boolean
  stage: number
  guild_role: GuildRole
  status: MemberStatus
  status_note?: string
  approved: boolean
  joined_at: string
}

export interface GuildStats {
  total_ranks: number
  average_rank: number
  member_count: number
}

export interface GuildRosterResponse {
  members: GuildMember[]
  stats: GuildStats
  guild: Guild
}

export interface GuildJoinRequest {
  id: number
  guild_id: number
  guild_name?: string
  user_id: number
  nickname: string
  message?: string
  status: 'pending' | 'approved' | 'rejected'
  created_at: string
}

export interface GuildStatusOption {
  key: string
  label: string
  color: string
  is_builtin: boolean
}
