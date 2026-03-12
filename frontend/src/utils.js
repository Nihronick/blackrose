export function pluralize(n, one, few, many) {
  const m10 = n % 10, m100 = n % 100
  if (m100 >= 11 && m100 <= 19) return many
  if (m10 === 1) return one
  if (m10 >= 2 && m10 <= 4) return few
  return many
}

export function parseVideo(url) {
  if (!url) return null
  const yt = url.match(/(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/)
  if (yt) return { type: 'youtube', id: yt[1] }
  if (url.match(/\.(mp4|webm|ogg)(\?|$)/i)) return { type: 'video', url }
  return { type: 'link', url }
}

export function parseDocument(url) {
  if (!url) return null
  const name = decodeURIComponent(url.split('/').pop().split('?')[0]) || 'Документ'
  const ext  = name.split('.').pop().toLowerCase()
  const icons = { pdf:'📕', doc:'📘', docx:'📘', xls:'📊', xlsx:'📊', png:'🖼', jpg:'🖼', jpeg:'🖼' }
  return { name, ext, icon: icons[ext] || '📄', url }
}
