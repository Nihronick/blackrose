import { useFavorites } from '@/hooks/useFavorites'
import { useHistory } from '@/hooks/useHistory'
import { useAppNavigation } from '@/lib/navigation'
import type { Category, Guide } from '@/lib/types'
import { useAppStore } from '@/store'
import { type FC, Suspense, lazy } from 'react'
import { Navigate, Route, Routes, useParams } from 'react-router-dom'

// Lazy views
const HomeView = lazy(() => import('@/views/HomeView').then((m) => ({ default: m.HomeView })))
const CategoriesView = lazy(() =>
  import('@/views/CategoriesView').then((m) => ({ default: m.CategoriesView }))
)
const FavoritesView = lazy(() =>
  import('@/views/FavoritesView').then((m) => ({ default: m.FavoritesView }))
)
const GuideView = lazy(() => import('@/views/GuideView').then((m) => ({ default: m.GuideView })))
const GuidesView = lazy(() => import('@/views/GuidesView').then((m) => ({ default: m.GuidesView })))
const GuildsView = lazy(() => import('@/views/GuildsView').then((m) => ({ default: m.GuildsView })))
const GuildRosterView = lazy(() => import('@/views/GuildRosterView').then((m) => ({ default: m.GuildRosterView })))
const HistoryView = lazy(() =>
  import('@/views/HistoryView').then((m) => ({ default: m.HistoryView }))
)
const TagResultsView = lazy(() =>
  import('@/views/TagResultsView').then((m) => ({ default: m.TagResultsView }))
)
const AdminView = lazy(() => import('@/views/AdminView').then((m) => ({ default: m.AdminView })))
const RoadmapView = lazy(() =>
  import('@/views/RoadmapView').then((m) => ({ default: m.RoadmapView }))
)
const ProfileView = lazy(() =>
  import('@/views/ProfileView').then((m) => ({ default: m.ProfileView }))
)
const SearchView = lazy(() => import('@/views/SearchView').then((m) => ({ default: m.SearchView })))

const ViewLoader = () => (
  <div className="flex h-full flex-col overflow-hidden container-padding pt-8">
    <div className="mb-10 h-10 w-2/3 rounded-2xl skeleton" />
    <div className="grid grid-cols-1 gap-5">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="h-28 rounded-[32px] border border-border/10 skeleton shadow-sm" />
      ))}
    </div>
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
