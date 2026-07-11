import { useEffect, useMemo, useRef, useState } from 'react'
import './App.css'
import galbotMark from './assets/galbot-mark.png'
import { RobotViewer } from './viewer/RobotViewer'
import { CustomizePanel } from './customize/CustomizePanel'
import { BodyColorPanel } from './customize/BodyColorPanel'
import { PlacementList } from './customize/PlacementList'
import { Gallery } from './gallery/Gallery'
import {
  ApiError,
  createDesign,
  designZipExportUrl,
  fetchContext,
  fetchTemplates,
  placementExportUrl,
  previewTemplateGlb,
} from './api/client'
import { defaultBodyColors } from './bodyColorGroups'
import { nextPlacementKey, type LocalPlacement } from './placement'
import type { ContextResponse, Design, QuaternionXYZW, TemplateSchema, Vec3 } from './types'

const IDENTITY_ROTATION: QuaternionXYZW = [0, 0, 0, 1]
const ZERO_OFFSET: Vec3 = [0, 0, 0]

function debounce<Args extends unknown[]>(fn: (...args: Args) => void, delayMs: number) {
  let timer: ReturnType<typeof setTimeout> | undefined
  return (...args: Args) => {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => fn(...args), delayMs)
  }
}

function defaultParamsFor(template: TemplateSchema): Record<string, number | string> {
  const defaults: Record<string, number | string> = {}
  for (const [key, schema] of Object.entries(template.params)) {
    defaults[key] = schema.default
  }
  return defaults
}

function App() {
  const [context, setContext] = useState<ContextResponse | null>(null)
  const [templates, setTemplates] = useState<TemplateSchema[]>([])

  // the decoration currently being configured, not yet confirmed
  const [draftTemplate, setDraftTemplate] = useState<TemplateSchema | null>(null)
  const [draftMountPoint, setDraftMountPoint] = useState('')
  const [draftParams, setDraftParams] = useState<Record<string, number | string>>({})
  const [draftOffset, setDraftOffset] = useState<Vec3>(ZERO_OFFSET)
  const [draftRotation, setDraftRotation] = useState<QuaternionXYZW>(IDENTITY_ROTATION)
  const [draftPreviewUrl, setDraftPreviewUrl] = useState<string | null>(null)

  // decorations confirmed into the current in-progress project
  const [placements, setPlacements] = useState<LocalPlacement[]>([])

  const [transformMode, setTransformMode] = useState<'translate' | 'rotate'>('translate')
  const [snapMode, setSnapMode] = useState(false)
  const [bodyColors, setBodyColors] = useState<Record<string, string>>(defaultBodyColors())
  const [teamName, setTeamName] = useState('')
  const [savedDesign, setSavedDesign] = useState<Design | null>(null)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [galleryRefreshKey, setGalleryRefreshKey] = useState(0)
  const draftPreviewUrlRef = useRef<string | null>(null)

  useEffect(() => {
    fetchContext().then((ctx) => {
      setContext(ctx)
      fetchTemplates().then((fetched) => {
        setTemplates(fetched)
        const first = fetched[0]
        setDraftTemplate(first)
        const firstMountPoint = first.mount_points[0]
        setDraftMountPoint(firstMountPoint)
        setDraftParams(defaultParamsFor(first))
        setDraftOffset(ctx.mount_points[firstMountPoint]?.offset ?? ZERO_OFFSET)
        setDraftRotation(IDENTITY_ROTATION)
      })
    })
  }, [])

  const debouncedPreview = useMemo(
    () =>
      debounce((templateId: string, p: Record<string, number | string>) => {
        previewTemplateGlb(templateId, p)
          .then((blob) => {
            const url = URL.createObjectURL(blob)
            if (draftPreviewUrlRef.current) URL.revokeObjectURL(draftPreviewUrlRef.current)
            draftPreviewUrlRef.current = url
            setDraftPreviewUrl(url)
          })
          .catch(() => {
            // transient invalid params while dragging a slider; ignore and keep last preview
          })
      }, 300),
    [],
  )

  useEffect(() => {
    if (!draftTemplate || Object.keys(draftParams).length === 0) return
    debouncedPreview(draftTemplate.id, draftParams)
  }, [draftTemplate, draftParams, debouncedPreview])

  if (!draftTemplate || !context) {
    return <div className="loading">加载中...</div>
  }

  const resetSaveState = () => {
    setSavedDesign(null)
    setSaveError(null)
  }

  const resetDraft = (nextTemplate: TemplateSchema) => {
    setDraftTemplate(nextTemplate)
    const nextMountPoint = nextTemplate.mount_points[0]
    setDraftMountPoint(nextMountPoint)
    setDraftParams(defaultParamsFor(nextTemplate))
    setDraftOffset(context.mount_points[nextMountPoint]?.offset ?? ZERO_OFFSET)
    setDraftRotation(IDENTITY_ROTATION)
  }

  const handleDraftTemplateChange = (templateId: string) => {
    const next = templates.find((t) => t.id === templateId)
    if (!next) return
    resetDraft(next)
  }

  const handleDraftMountPointChange = (mp: string) => {
    setDraftMountPoint(mp)
    setDraftOffset(context.mount_points[mp]?.offset ?? ZERO_OFFSET)
    setDraftRotation(IDENTITY_ROTATION)
  }

  const handleResetDraftPlacement = () => {
    setDraftOffset(context.mount_points[draftMountPoint]?.offset ?? ZERO_OFFSET)
    setDraftRotation(IDENTITY_ROTATION)
  }

  const handleConfirmPlacement = async () => {
    resetSaveState()
    try {
      const blob = await previewTemplateGlb(draftTemplate.id, draftParams)
      const url = URL.createObjectURL(blob)
      setPlacements((prev) => [
        ...prev,
        {
          key: nextPlacementKey(),
          templateId: draftTemplate.id,
          mountPoint: draftMountPoint,
          params: draftParams,
          offset: draftOffset,
          rotation: draftRotation,
          previewUrl: url,
        },
      ])
      resetDraft(draftTemplate)
    } catch {
      setSaveError('生成预览失败，请检查参数')
    }
  }

  const handleRemovePlacement = (key: string) => {
    resetSaveState()
    setPlacements((prev) => {
      const target = prev.find((p) => p.key === key)
      if (target) URL.revokeObjectURL(target.previewUrl)
      return prev.filter((p) => p.key !== key)
    })
  }

  const handleEditPlacement = (key: string) => {
    const target = placements.find((p) => p.key === key)
    if (!target) return
    const targetTemplate = templates.find((t) => t.id === target.templateId)
    if (targetTemplate) setDraftTemplate(targetTemplate)
    setDraftMountPoint(target.mountPoint)
    setDraftParams(target.params)
    setDraftOffset(target.offset)
    setDraftRotation(target.rotation)
    URL.revokeObjectURL(target.previewUrl)
    setPlacements((prev) => prev.filter((p) => p.key !== key))
  }

  const handleSave = async () => {
    setSaveError(null)
    if (!teamName.trim()) {
      setSaveError('请先填写队名')
      return
    }
    if (placements.length === 0) {
      setSaveError('请至少确认加入一件配饰')
      return
    }
    try {
      const design = await createDesign({
        team_name: teamName.trim(),
        placements: placements.map((p) => ({
          template_id: p.templateId,
          mount_point: p.mountPoint,
          params: p.params,
          offset: p.offset,
          rotation: p.rotation,
        })),
        body_colors: bodyColors,
      })
      setSavedDesign(design)
      setGalleryRefreshKey((k) => k + 1)
    } catch (err) {
      if (err instanceof ApiError && Array.isArray(err.detail)) {
        const messages = (err.detail as { field: string; message: string }[]).map((i) => i.message)
        setSaveError(messages.join('；'))
      } else {
        setSaveError('保存失败，请重试')
      }
    }
  }

  const handleSelectDesign = async (design: Design) => {
    for (const p of placements) URL.revokeObjectURL(p.previewUrl)
    const loaded: LocalPlacement[] = []
    for (const placement of design.placements) {
      try {
        const blob = await previewTemplateGlb(placement.template_id, placement.params)
        loaded.push({
          key: nextPlacementKey(),
          templateId: placement.template_id,
          mountPoint: placement.mount_point,
          params: placement.params,
          offset: placement.offset ?? context.mount_points[placement.mount_point]?.offset ?? ZERO_OFFSET,
          rotation: placement.rotation ?? IDENTITY_ROTATION,
          previewUrl: URL.createObjectURL(blob),
        })
      } catch {
        // skip placements whose template no longer exists/validates
      }
    }
    setPlacements(loaded)
    setTeamName(design.team_name)
    setBodyColors(design.body_colors ?? defaultBodyColors())
    setSavedDesign(design)
    setSaveError(null)
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <img className="brand-mark" src={galbotMark} alt="Galbot" />
          <div>
            <h1>
              GALBOT <span className="brand-divider">/</span> 装饰定制工坊
            </h1>
            <p>配色 · 选模板 · 摆放 · 导出打印</p>
          </div>
        </div>
      </header>
      <div className="app-layout">
        <div className="viewer-pane">
          <RobotViewer
            urdfUrl={context.urdf_url}
            robotBaseUrl={context.robot_base_url}
            mountPoints={context.mount_points}
            bodyColors={bodyColors}
            confirmedPlacements={placements}
            draftMountPoint={draftMountPoint}
            draftUrl={draftPreviewUrl}
            offset={draftOffset}
            rotation={draftRotation}
            onOffsetChange={setDraftOffset}
            onRotationChange={setDraftRotation}
            snapMode={snapMode}
            transformMode={transformMode}
          />
          <div className="viewer-toolbar">
            <button
              className={transformMode === 'translate' ? 'active' : ''}
              onClick={() => setTransformMode('translate')}
            >
              移动
            </button>
            <button className={transformMode === 'rotate' ? 'active' : ''} onClick={() => setTransformMode('rotate')}>
              旋转
            </button>
            <button className={snapMode ? 'active' : ''} onClick={() => setSnapMode((s) => !s)}>
              {snapMode ? '贴合模式：点击机器人表面贴合' : '开启贴合模式'}
            </button>
          </div>
          <p className="viewer-hint">
            {snapMode
              ? '点击机器人表面，正在编辑的配饰会自动贴合到该处并对齐法线方向'
              : '拖动箭头移动、拖动圆环旋转正在编辑的配饰；已确认的配饰会固定显示'}
          </p>
        </div>
        <div className="side-pane">
          <BodyColorPanel colors={bodyColors} onChange={setBodyColors} />
          <CustomizePanel
            templates={templates}
            template={draftTemplate}
            onTemplateChange={handleDraftTemplateChange}
            mountPoint={draftMountPoint}
            onMountPointChange={handleDraftMountPointChange}
            params={draftParams}
            onParamsChange={setDraftParams}
          />
          <div className="draft-actions">
            <button className="btn-ghost" onClick={handleResetDraftPlacement}>
              重置位置/角度
            </button>
            <button className="btn-primary" onClick={handleConfirmPlacement}>
              ✓ 确认加入，添加下一件
            </button>
          </div>

          <PlacementList
            placements={placements}
            templates={templates}
            onEdit={handleEditPlacement}
            onRemove={handleRemovePlacement}
          />

          <section className="panel-card save-section">
            <h2>保存 &amp; 导出整套作品</h2>
            <label className="field">
              <span>队名</span>
              <input value={teamName} onChange={(e) => setTeamName(e.target.value)} placeholder="输入队名" />
            </label>
            <button className="btn-primary" onClick={handleSave}>
              保存到作品库
            </button>
            {saveError && <p className="field-error">{saveError}</p>}
            {savedDesign && (
              <div className="export-links">
                <a href={designZipExportUrl(savedDesign.id)}>⬇ 下载全部 (ZIP)</a>
                {savedDesign.placements.map((_, i) => (
                  <a key={i} href={placementExportUrl(savedDesign.id, i, 'stl')}>
                    ⬇ {i + 1}.stl
                  </a>
                ))}
              </div>
            )}
          </section>

          <Gallery refreshKey={galleryRefreshKey} onSelect={handleSelectDesign} templates={templates} />
        </div>
      </div>
    </div>
  )
}

export default App
