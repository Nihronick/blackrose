import { PTR_THRESHOLD } from '../hooks/usePullToRefresh'

export function PtrIndicator({ pullY, refreshing }) {
  if (pullY < 8 && !refreshing) return null
  const progress = Math.min(pullY / PTR_THRESHOLD, 1)

  return (
    <div style={{ display:'flex', justifyContent:'center', paddingTop: `${Math.max(pullY * 0.55, refreshing ? 12 : 0)}px`, paddingBottom: 8, transition: refreshing ? 'padding .2s' : 'none' }}>
      <div style={{
        width:36, height:36, background:'var(--surface)', borderRadius:'50%',
        display:'flex', alignItems:'center', justifyContent:'center',
        boxShadow:'var(--shadow)',
        transform:`scale(${.55 + progress*.45}) rotate(${progress*200}deg)`,
        transition: refreshing ? 'transform .2s' : 'none',
      }}>
        <div style={{
          width:20, height:20, borderRadius:'50%',
          border:'2.5px solid var(--separator)',
          borderTopColor: refreshing ? 'var(--accent)' : `rgba(51,144,236,${progress})`,
          animation: refreshing ? 'ptr-spin .7s linear infinite' : 'none',
        }}/>
      </div>
    </div>
  )
}
