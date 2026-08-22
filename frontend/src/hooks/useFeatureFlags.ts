import { apiFetch } from '@/lib/api'
import { useQuery } from '@tanstack/react-query'

export interface FeatureFlags {
  build_planner?: boolean
  tier_list?: boolean
  guild_wars?: boolean
  comments?: boolean
  reactions?: boolean
  favorites_sync?: boolean
  search?: boolean
  onboarding?: boolean
  roadmap?: boolean
  media_cache?: boolean
}

const DEFAULT_FLAGS: FeatureFlags = {
  build_planner: true,
  tier_list: true,
  guild_wars: false,
  comments: true,
  reactions: true,
  favorites_sync: true,
  search: true,
  onboarding: true,
  roadmap: true,
  media_cache: true,
}

export function useFeatureFlags() {
  const { data: flags = DEFAULT_FLAGS, isLoading } = useQuery<FeatureFlags>({
    queryKey: ['feature_flags'],
    queryFn: () => apiFetch<FeatureFlags>('/api/features').catch(() => DEFAULT_FLAGS),
    staleTime: 5 * 60 * 1000, // 5 min cache
  })

  const isEnabled = (flagName: keyof FeatureFlags): boolean => {
    return flags[flagName] ?? DEFAULT_FLAGS[flagName] ?? false
  }

  return {
    flags,
    isLoading,
    isEnabled,
  }
}
