import { useFavorites } from '@/hooks/useFavorites'
import { useHistory } from '@/hooks/useHistory'
import { useAppNavigation } from '@/lib/navigation'
import type { Category, Guide } from '@/lib/types'
import { useAppStore } from '@/store'
import { type FC, Suspense, lazy } from 'react'
import { Navigate, Route, Routes, useParams } from 'react-router-dom'

function lazyWithRetry<T extends React.ComponentType<any>>(
  componentImport: () => Promise<{ default: T } | { [key: string]: T }>
) {
  return lazy(async () => {
    const pageHasAlreadyBeenReloaded =
      sessionStorage.getItem('page_reloaded_for_chunk_error') === 'true'

    try {
      const component = await componentImport()
      sessionStorage.setItem('page_reloaded_for_chunk_error', 'false')
      return 'default' in component ? component : { default: Object.values(component)[0] as T }
    } catch (error) {
      if (!pageHasAlreadyBeenReloaded) {
        sessionStorage.setItem('page_reloaded_for_chunk_error', 'true')
        window.location.reload()
        return new Promise(() => {})
      }
      throw error
    }
  })
}

// Lazy views with chunk retry protection
const HomeView = lazyWithRetry(() =>
  import('@/views/HomeView').then((m) => ({ default: m.HomeView }))
)
const CategoriesView = lazyWithRetry(() =>
  import('@/views/CategoriesView').then((m) => ({ default: m.CategoriesView }))
)
const FavoritesView = lazyWithRetry(() =>
  import('@/views/FavoritesView').then((m) => ({ default: m.FavoritesView }))
)
const GuideView = lazyWithRetry(() =>
  import('@/views/GuideView').then((m) => ({ default: m.GuideView }))
)
const GuidesView = lazyWithRetry(() =>
  import('@/views/GuidesView').then((m) => ({ default: m.GuidesView }))
)
const GuildsView = lazyWithRetry(() =>
  import('@/views/GuildsView').then((m) => ({ default: m.GuildsView }))
)
const GuildRosterView = lazyWithRetry(() =>
  import('@/views/GuildRosterView').then((m) => ({ default: m.GuildRosterView }))
)
const HistoryView = lazyWithRetry(() =>
  import('@/views/HistoryView').then((m) => ({ default: m.HistoryView }))
)
const TagResultsView = lazyWithRetry(() =>
  import('@/views/TagResultsView').then((m) => ({ default: m.TagResultsView }))
)
const AdminView = lazyWithRetry(() =>
  import('@/views/AdminView').then((m) => ({ default: m.AdminView }))
)
const RoadmapView = lazyWithRetry(() =>
  import('@/views/RoadmapView').then((m) => ({ default: m.RoadmapView }))
)
const ProfileView = lazyWithRetry(() =>
  import('@/views/ProfileView').then((m) => ({ default: m.ProfileView }))
)
const SearchView = lazyWithRetry(() =>
  import('@/views/SearchView').then((m) => ({ default: m.SearchView }))
)
const BuildPlannerView = lazyWithRetry(() =>
  import('@/views/BuildPlannerView').then((m) => ({ default: m.BuildPlannerView }))
)

const ViewLoader = () => (
  <div className="flex h-full flex-col overflow-hidden container-padding pt-6 pb-24 space-y-6 animate-pulse">
    <div className="flex items-center justify-between">
      <div className="h-10 w-48 rounded-2xl bg-rose-500/10 border border-rose-500/20" />
      <div className="h-8 w-24 rounded-xl bg-amber-500/10 border border-amber-500/20" />
    </div>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
      <div className="h-44 rounded-3xl rose-bento-card border-rose-500/20 bg-card/60" />
      <div className="h-44 rounded-3xl rose-bento-card border-rose-500/20 bg-card/60" />
      <div className="h-44 rounded-3xl rose-bento-card border-rose-500/20 bg-card/60" />
    </div>
    <div className="h-32 rounded-3xl rose-bento-card border-rose-500/20 bg-card/40" />
  </div>
)

export const AppRouter: FC = () => {
  const { push } = useAppNavigation()
  const { cats, setCats } = useAppStore()
  const { favorites, toggle: toggleFav, isFavorite } = useFavorites()
  const { history, addToHistory } = useHistory()

  const handleOpenGuide = (key: string, title?: string, icon?: string) => {
    if (key) {
      addToHistory({ key, title: title || key, icon: icon || '' })
      push({ type: 'guide', id: key })
    }
  }

  return (
    <Suspense fallback={<ViewLoader />}>
      <Routes>
        <Route
          path="/"
          element={
            <HomeView
              onSelectCategory={(cat) => push({ type: 'category', id: cat.key })}
              onSelectGuide={handleOpenGuide}
            />
          }
        />
        <Route
          path="/categories"
          element={
            <CategoriesView
              onSelectCategory={(cat) => push({ type: 'category', id: cat.key })}
              onCategoriesLoaded={setCats}
            />
          }
        />
        <Route
          path="/category/:id"
          element={<InnerGuidesView onSelectGuide={handleOpenGuide} cats={cats} />}
        />
        <Route
          path="/guide/:id"
          element={
            <InnerGuideView
              isFavorite={isFavorite}
              onToggleFavorite={toggleFav}
              onOpenGuide={handleOpenGuide}
              onTagClick={(tag) => push({ type: 'tag', tag })}
              onGuideLoaded={(g) => addToHistory({ key: g.key, title: g.title, icon: g.icon })}
            />
          }
        />
        <Route path="/tag/:tag" element={<InnerTagResultsView onSelectGuide={handleOpenGuide} />} />
        <Route
          path="/favorites"
          element={
            <FavoritesView
              favorites={favorites}
              onSelectGuide={handleOpenGuide}
              onToggle={toggleFav}
            />
          }
        />
        <Route
          path="/history"
          element={<HistoryView history={history} onSelectGuide={handleOpenGuide} />}
        />
        <Route path="/roadmap" element={<RoadmapView onSelectGuide={handleOpenGuide} />} />
        <Route path="/profile" element={<ProfileView />} />
        <Route path="/search" element={<SearchView />} />
        <Route path="/build" element={<BuildPlannerView />} />
        <Route path="/admin" element={<AdminView onClose={() => push({ type: 'home' })} />} />
        <Route path="/guilds" element={<GuildsView />} />
        <Route path="/guilds/:id" element={<InnerGuildRosterView />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  )
}

// Route wrappers
interface RouteWrapperProps {
  onSelectGuide: (key: string, title?: string, icon?: string) => void
}

const InnerGuidesView = ({
  onSelectGuide,
  cats,
}: { onSelectGuide: RouteWrapperProps['onSelectGuide']; cats: Category[] }) => {
  const { id } = useParams()
  const cat = cats?.find((c) => c.key === id)
  const category = { key: id!, title: cat?.title || 'Гайды', icon: cat?.icon }
  return <GuidesView category={category} onSelectGuide={onSelectGuide} />
}

const InnerGuideView = ({
  onToggleFavorite,
  isFavorite,
  onOpenGuide,
  onTagClick,
  onGuideLoaded,
}: {
  onToggleFavorite: (guide: { key: string; title: string; icon: string }) => void
  isFavorite: (key: string) => boolean
  onOpenGuide: (key: string, title?: string, icon?: string) => void
  onTagClick: (tag: string) => void
  onGuideLoaded: (guide: Guide) => void
}) => {
  const { id } = useParams()
  return (
    <GuideView
      guideKey={id!}
      isFavorite={isFavorite(id!)}
      onToggleFavorite={onToggleFavorite}
      onOpenGuide={onOpenGuide}
      onTagClick={onTagClick}
      onGuideLoaded={onGuideLoaded}
    />
  )
}

const InnerTagResultsView = ({ onSelectGuide }: RouteWrapperProps) => {
  const { tag } = useParams()
  return <TagResultsView tag={tag!} onSelectGuide={onSelectGuide} />
}

const InnerGuildRosterView = () => {
  const { id } = useParams()
  return <GuildRosterView guildId={Number(id)} />
}
