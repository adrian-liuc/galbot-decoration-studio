export interface BodyColorGroup {
  id: string
  label: string
  linkPrefixes: string[]
}

// #ffffff means "no tint" since three.js multiplies a mesh's texture color
// by material.color — leaving every group at white reproduces the model's
// original look with zero extra state to track for "reset".
export const DEFAULT_BODY_COLOR = '#ffffff'

export const BODY_COLOR_GROUPS: BodyColorGroup[] = [
  { id: 'chassis', label: '底盘', linkPrefixes: ['leg_', 'omni_chassis', 'wheel_', 'chassis_'] },
  { id: 'torso', label: '躯干', linkPrefixes: ['torso_base_link'] },
  { id: 'head', label: '头部', linkPrefixes: ['head_'] },
  { id: 'left_arm', label: '左臂', linkPrefixes: ['left_arm_', 'left_gripper_', 'left_wrist_'] },
  { id: 'right_arm', label: '右臂', linkPrefixes: ['right_arm_', 'right_gripper_', 'right_wrist_'] },
]

export function defaultBodyColors(): Record<string, string> {
  const colors: Record<string, string> = {}
  for (const group of BODY_COLOR_GROUPS) colors[group.id] = DEFAULT_BODY_COLOR
  return colors
}
