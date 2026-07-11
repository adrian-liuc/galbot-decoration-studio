import { BODY_COLOR_GROUPS, DEFAULT_BODY_COLOR } from '../bodyColorGroups'

interface BodyColorPanelProps {
  colors: Record<string, string>
  onChange: (colors: Record<string, string>) => void
}

export function BodyColorPanel({ colors, onChange }: BodyColorPanelProps) {
  const setColor = (groupId: string, hex: string) => {
    onChange({ ...colors, [groupId]: hex })
  }

  const resetAll = () => {
    const reset: Record<string, string> = {}
    for (const group of BODY_COLOR_GROUPS) reset[group.id] = DEFAULT_BODY_COLOR
    onChange(reset)
  }

  return (
    <section className="panel-card">
      <div className="body-color-header">
        <h2>机身配色</h2>
        <button className="btn-ghost small" onClick={resetAll}>
          恢复默认
        </button>
      </div>
      <div className="body-color-grid">
        {BODY_COLOR_GROUPS.map((group) => (
          <label className="body-color-swatch" key={group.id}>
            <input
              type="color"
              value={colors[group.id] ?? DEFAULT_BODY_COLOR}
              onChange={(e) => setColor(group.id, e.target.value)}
            />
            <span>{group.label}</span>
          </label>
        ))}
      </div>
    </section>
  )
}
