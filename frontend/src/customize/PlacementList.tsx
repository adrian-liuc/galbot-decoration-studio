import type { LocalPlacement } from '../placement'
import type { TemplateSchema } from '../types'
import { MOUNT_POINT_LABELS } from '../mountPointLabels'

interface PlacementListProps {
  placements: LocalPlacement[]
  templates: TemplateSchema[]
  onEdit: (key: string) => void
  onRemove: (key: string) => void
}

export function PlacementList({ placements, templates, onEdit, onRemove }: PlacementListProps) {
  const templateName = (id: string) => templates.find((t) => t.id === id)?.name ?? id

  return (
    <section className="panel-card">
      <h2>已添加配饰 ({placements.length})</h2>
      {placements.length === 0 && <p className="muted">配置好一件之后点"确认加入"，可以叠加多件</p>}
      <ul className="placement-list">
        {placements.map((p) => (
          <li key={p.key} className="placement-item">
            <button className="placement-item-main" onClick={() => onEdit(p.key)}>
              <strong>{templateName(p.templateId)}</strong>
              <span className="gallery-item-meta">{MOUNT_POINT_LABELS[p.mountPoint] ?? p.mountPoint}</span>
            </button>
            <button className="placement-remove" onClick={() => onRemove(p.key)} title="删除">
              ×
            </button>
          </li>
        ))}
      </ul>
    </section>
  )
}
