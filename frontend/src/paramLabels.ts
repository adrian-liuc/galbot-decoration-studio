export const PARAM_LABELS: Record<string, string> = {
  inner_diameter_mm: '内径 (mm)',
  thickness_mm: '厚度 (mm)',
  height_mm: '高度 (mm)',
  pattern: '图案',
  color: '颜色',
  shape: '形状',
  diameter_mm: '直径 (mm)',
  boss_height_mm: '凸起高度 (mm)',
  width_mm: '宽度 (mm)',
  length_mm: '长度 (mm)',
  ridge_height_mm: '中脊高度 (mm)',
  slot_count: '格栅条数',
  base_length_mm: '底边长 (mm)',
  sweep: '弯曲程度',
  band_height_mm: '环带高度 (mm)',
  spike_count: '尖刺数量',
  spike_height_mm: '尖刺高度 (mm)',
  tube_diameter_mm: '圆管粗细 (mm)',
  mast_height_mm: '杆高 (mm)',
  mast_diameter_mm: '杆径 (mm)',
  ball_diameter_mm: '球径 (mm)',
  max_height_mm: '最高尖刺 (mm)',
  base_diameter_mm: '尖刺粗细 (mm)',
  blade_count: '羽片数',
  blade_length_mm: '羽片长 (mm)',
  blade_base_mm: '羽片宽 (mm)',
  spread_deg: '展开角度 (°)',
  size_mm: '尺寸 (mm)',
  height_ratio: '拉伸比例',
  facet_style: '切面风格',
}

export const ENUM_OPTION_LABELS: Record<string, string> = {
  plain: '平面',
  hex: '六边形孔',
  wave: '波浪纹',
  circle: '圆形',
  shield: '盾形',
  icosahedron: '二十面体',
  octahedron: '八面体',
}

export function paramLabel(key: string): string {
  return PARAM_LABELS[key] ?? key
}

export function enumOptionLabel(value: string): string {
  return ENUM_OPTION_LABELS[value] ?? value
}
