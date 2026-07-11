import { useEffect, useState } from 'react'
import { designZipExportUrl, listDesigns } from '../api/client'
import type { Design, TemplateSchema } from '../types'
import { MOUNT_POINT_LABELS } from '../mountPointLabels'

interface GalleryProps {
  refreshKey: number
  onSelect: (design: Design) => void
  templates: TemplateSchema[]
}

export function Gallery({ refreshKey, onSelect, templates }: GalleryProps) {
  const [teamFilter, setTeamFilter] = useState('')
  const [designs, setDesigns] = useState<Design[]>([])
  const [loading, setLoading] = useState(false)

  const reload = () => {
    setLoading(true)
    listDesigns(teamFilter || undefined)
      .then(setDesigns)
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    reload()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refreshKey])

  const templateName = (id: string) => templates.find((t) => t.id === id)?.name ?? id

  const summarize = (d: Design) => {
    if (d.placements.length === 0) return '空作品'
    const first = templateName(d.placements[0].template_id)
    const extra = d.placements.length > 1 ? ` 等 ${d.placements.length} 件` : ''
    return `${MOUNT_POINT_LABELS[d.placements[0].mount_point] ?? d.placements[0].mount_point} · ${first}${extra}`
  }

  return (
    <section className="panel-card">
      <h2>作品库</h2>
      <div className="gallery-filter">
        <input
          placeholder="按队名筛选"
          value={teamFilter}
          onChange={(e) => setTeamFilter(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && reload()}
        />
        <button className="btn-ghost" onClick={reload}>
          刷新
        </button>
      </div>
      {loading && <p className="muted">加载中...</p>}
      {!loading && designs.length === 0 && <p className="muted">还没有作品，快去保存第一个吧</p>}
      <ul className="gallery-list">
        {designs.map((d) => (
          <li key={d.id} className="gallery-item">
            <button className="gallery-item-main" onClick={() => onSelect(d)}>
              <strong>{d.team_name}</strong>
              <span className="gallery-item-meta">{summarize(d)}</span>
            </button>
            <div className="gallery-item-links">
              <a href={designZipExportUrl(d.id)}>ZIP</a>
            </div>
          </li>
        ))}
      </ul>
    </section>
  )
}
