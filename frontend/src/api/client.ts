import type { ContextResponse, Design, Placement, TemplateSchema } from '../types'

async function handleJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new ApiError(res.status, body.detail ?? res.statusText)
  }
  return res.json() as Promise<T>
}

export class ApiError extends Error {
  status: number
  detail: unknown
  constructor(status: number, detail: unknown) {
    super(typeof detail === 'string' ? detail : JSON.stringify(detail))
    this.status = status
    this.detail = detail
  }
}

export async function fetchContext(): Promise<ContextResponse> {
  const res = await fetch('/api/context')
  return handleJson(res)
}

export async function fetchTemplates(): Promise<TemplateSchema[]> {
  const res = await fetch('/api/templates')
  return handleJson(res)
}

export async function previewTemplateGlb(
  templateId: string,
  params: Record<string, unknown>,
): Promise<Blob> {
  const res = await fetch(`/api/templates/${templateId}/preview.glb`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new ApiError(res.status, body.detail ?? res.statusText)
  }
  return res.blob()
}

export async function createDesign(payload: {
  team_name: string
  placements: Placement[]
  body_colors?: Record<string, string> | null
}): Promise<Design> {
  const res = await fetch('/api/designs', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  return handleJson(res)
}

export async function listDesigns(teamName?: string): Promise<Design[]> {
  const url = teamName ? `/api/designs?team_name=${encodeURIComponent(teamName)}` : '/api/designs'
  const res = await fetch(url)
  return handleJson(res)
}

export function placementExportUrl(designId: number, index: number, format: 'stl' | '3mf'): string {
  return `/api/designs/${designId}/placements/${index}/export.${format}`
}

export function designZipExportUrl(designId: number): string {
  return `/api/designs/${designId}/export.zip`
}
