import type { TemplateSchema } from '../types'
import { MOUNT_POINT_LABELS } from '../mountPointLabels'
import { enumOptionLabel, paramLabel } from '../paramLabels'

interface CustomizePanelProps {
  templates: TemplateSchema[]
  template: TemplateSchema
  onTemplateChange: (templateId: string) => void
  mountPoint: string
  onMountPointChange: (mountPoint: string) => void
  params: Record<string, number | string>
  onParamsChange: (params: Record<string, number | string>) => void
}

export function CustomizePanel({
  templates,
  template,
  onTemplateChange,
  mountPoint,
  onMountPointChange,
  params,
  onParamsChange,
}: CustomizePanelProps) {
  const setParam = (key: string, value: number | string) => {
    onParamsChange({ ...params, [key]: value })
  }

  return (
    <section className="panel-card">
      <h2>定制装饰件</h2>

      <div className="field-row">
        <label className="field">
          <span>装饰模板</span>
          <select value={template.id} onChange={(e) => onTemplateChange(e.target.value)}>
            {templates.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>安装部位</span>
          <select value={mountPoint} onChange={(e) => onMountPointChange(e.target.value)}>
            {template.mount_points.map((mp) => (
              <option key={mp} value={mp}>
                {MOUNT_POINT_LABELS[mp] ?? mp}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="param-list">
        {Object.entries(template.params).map(([key, schema]) => {
          if (schema.type === 'number') {
            const value = Number(params[key] ?? schema.default)
            return (
              <label className="field" key={key}>
                <span className="field-label-row">
                  <span>{paramLabel(key)}</span>
                  <span className="field-value">{value}</span>
                </span>
                <input
                  type="range"
                  min={schema.min}
                  max={schema.max}
                  step={schema.step}
                  value={value}
                  onChange={(e) => setParam(key, Number(e.target.value))}
                />
              </label>
            )
          }
          if (schema.type === 'enum') {
            const value = String(params[key] ?? schema.default)
            return (
              <label className="field" key={key}>
                <span>{paramLabel(key)}</span>
                <select value={value} onChange={(e) => setParam(key, e.target.value)}>
                  {schema.options.map((opt) => (
                    <option key={opt} value={opt}>
                      {enumOptionLabel(opt)}
                    </option>
                  ))}
                </select>
              </label>
            )
          }
          if (schema.type === 'color') {
            const value = String(params[key] ?? schema.default)
            return (
              <label className="field field-inline" key={key}>
                <span>{paramLabel(key)}</span>
                <input type="color" value={value} onChange={(e) => setParam(key, e.target.value)} />
              </label>
            )
          }
          return null
        })}
      </div>
    </section>
  )
}
