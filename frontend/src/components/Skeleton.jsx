export function SkeletonCard() {
  return (
    <div className="skeleton-card">
      <div className="skeleton sk-icon" />
      <div className="sk-body">
        <div className="skeleton sk-title" />
        <div className="skeleton sk-sub" />
      </div>
    </div>
  )
}

export function SkeletonList({ count = 6 }) {
  return (
    <div className="list">
      {Array.from({ length: count }).map((_, i) => <SkeletonCard key={i} />)}
    </div>
  )
}

export function SkeletonGuide() {
  return (
    <div className="guide-wrap">
      <div className="sk-guide-header">
        <div className="skeleton sk-guide-icon" />
        <div className="skeleton sk-guide-title" />
      </div>
      <div className="sk-lines">
        {[100,88,72,95,60,82,50,78].map((w, i) => (
          <div key={i} className="skeleton sk-line" style={{ width:`${w}%` }} />
        ))}
      </div>
    </div>
  )
}
