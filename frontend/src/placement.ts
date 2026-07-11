import type { QuaternionXYZW, Vec3 } from './types'

/** A confirmed decoration instance in the current in-progress project.
 * `previewUrl` is a blob URL fetched once at confirm-time, independent of
 * the draft editor's own live-updating preview. */
export interface LocalPlacement {
  key: string
  templateId: string
  mountPoint: string
  params: Record<string, number | string>
  offset: Vec3
  rotation: QuaternionXYZW
  previewUrl: string
}

let idCounter = 0
export function nextPlacementKey(): string {
  idCounter += 1
  return `p${Date.now()}_${idCounter}`
}
