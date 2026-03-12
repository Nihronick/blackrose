const PATHS = {
  photo: 'M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z',
  video: 'M8 5v14l11-7z',
  doc:   'M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z',
}

function Badge({ cls, path, label }) {
  return (
    <span className={`badge ${cls}`}>
      <svg viewBox="0 0 24 24" width="10" height="10" fill="currentColor"><path d={path}/></svg>
      {label}
    </span>
  )
}

export function ContentBadges({ hasPhoto, hasVideo, hasDocument }) {
  if (!hasPhoto && !hasVideo && !hasDocument) return null
  return (
    <span className="badges-row">
      {hasPhoto    && <Badge cls="badge-photo" path={PATHS.photo} label="Фото"  />}
      {hasVideo    && <Badge cls="badge-video" path={PATHS.video} label="Видео" />}
      {hasDocument && <Badge cls="badge-doc"   path={PATHS.doc}   label="Файл"  />}
    </span>
  )
}
