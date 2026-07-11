export type ParamSchemaEntry =
  | { type: 'number'; min: number; max: number; default: number; step: number }
  | { type: 'enum'; options: string[]; default: string }
  | { type: 'color'; default: string }

export interface TemplateSchema {
  id: string
  name: string
  mount_points: string[]
  params: Record<string, ParamSchemaEntry>
}

export interface MountPointInfo {
  link: string
  attachment_type: 'ring' | 'flat'
  offset: [number, number, number]
}

export interface ContextResponse {
  urdf_url: string
  robot_base_url: string
  mount_points: Record<string, MountPointInfo>
}

export type Vec3 = [number, number, number]
export type QuaternionXYZW = [number, number, number, number]

export interface Placement {
  template_id: string
  mount_point: string
  params: Record<string, number | string>
  offset: Vec3 | null
  rotation: QuaternionXYZW | null
}

export interface Design {
  id: number
  team_name: string
  placements: Placement[]
  body_colors: Record<string, string> | null
  created_at: string
  updated_at: string
}
