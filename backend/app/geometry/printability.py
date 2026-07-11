from dataclasses import dataclass

# Conservative defaults for a typical desktop FDM printer (0.4mm nozzle).
MAX_BED_DIM_MM = 220.0
MIN_WALL_THICKNESS_MM = 1.2
MAX_HEIGHT_MM = 120.0
MIN_INNER_DIAMETER_MM = 20.0
MAX_INNER_DIAMETER_MM = 150.0


@dataclass
class PrintabilityIssue:
    field: str
    message: str


def check_ring_params(params: dict, fit_diameter_range: tuple[float, float] | None = None) -> list[PrintabilityIssue]:
    issues: list[PrintabilityIssue] = []

    inner_d = float(params.get("inner_diameter_mm", 0))
    thickness = float(params.get("thickness_mm", 0))
    height = float(params.get("height_mm", 0))

    min_d, max_d = fit_diameter_range or (MIN_INNER_DIAMETER_MM, MAX_INNER_DIAMETER_MM)
    if not (min_d <= inner_d <= max_d):
        issues.append(PrintabilityIssue(
            "inner_diameter_mm",
            f"内径需在 {min_d:.1f}-{max_d:.1f}mm 之间才能套上机器人手臂，当前 {inner_d:.1f}mm",
        ))

    if thickness < MIN_WALL_THICKNESS_MM:
        issues.append(PrintabilityIssue(
            "thickness_mm",
            f"壁厚至少需要 {MIN_WALL_THICKNESS_MM}mm 才能打印牢固，当前 {thickness:.2f}mm",
        ))

    outer_d = inner_d + 2 * thickness
    if outer_d > MAX_BED_DIM_MM:
        issues.append(PrintabilityIssue(
            "thickness_mm",
            f"外径 {outer_d:.1f}mm 超出常见打印机热床尺寸 ({MAX_BED_DIM_MM}mm)",
        ))

    if not (0 < height <= MAX_HEIGHT_MM):
        issues.append(PrintabilityIssue(
            "height_mm",
            f"高度需在 0-{MAX_HEIGHT_MM}mm 之间，当前 {height:.1f}mm",
        ))

    return issues


MAX_BADGE_DIAMETER_MM = 150.0
MIN_BADGE_THICKNESS_MM = 1.2
MAX_BADGE_TOTAL_HEIGHT_MM = 30.0


def check_badge_params(params: dict) -> list[PrintabilityIssue]:
    issues: list[PrintabilityIssue] = []

    diameter = float(params.get("diameter_mm", 0))
    thickness = float(params.get("thickness_mm", 0))
    boss_height = float(params.get("boss_height_mm", 0))

    if not (10 <= diameter <= MAX_BADGE_DIAMETER_MM):
        issues.append(PrintabilityIssue(
            "diameter_mm",
            f"直径需在 10-{MAX_BADGE_DIAMETER_MM:.0f}mm 之间，当前 {diameter:.1f}mm",
        ))

    if thickness < MIN_BADGE_THICKNESS_MM:
        issues.append(PrintabilityIssue(
            "thickness_mm",
            f"底板厚度至少需要 {MIN_BADGE_THICKNESS_MM}mm 才能打印牢固，当前 {thickness:.2f}mm",
        ))

    total_height = thickness + max(boss_height, 0)
    if total_height > MAX_BADGE_TOTAL_HEIGHT_MM:
        issues.append(PrintabilityIssue(
            "boss_height_mm",
            f"底板+凸起总高度需 ≤ {MAX_BADGE_TOTAL_HEIGHT_MM:.0f}mm，当前 {total_height:.1f}mm",
        ))

    return issues


MAX_PLATE_DIM_MM = 150.0
MIN_PLATE_THICKNESS_MM = 1.2
MAX_PLATE_TOTAL_HEIGHT_MM = 30.0


def check_plate_params(params: dict) -> list[PrintabilityIssue]:
    issues: list[PrintabilityIssue] = []

    width = float(params.get("width_mm", 0))
    length = float(params.get("length_mm", 0))
    thickness = float(params.get("thickness_mm", 0))
    ridge_height = float(params.get("ridge_height_mm", 0))

    if not (15 <= width <= MAX_PLATE_DIM_MM):
        issues.append(PrintabilityIssue("width_mm", f"宽度需在 15-{MAX_PLATE_DIM_MM:.0f}mm 之间，当前 {width:.1f}mm"))
    if not (15 <= length <= MAX_PLATE_DIM_MM):
        issues.append(PrintabilityIssue("length_mm", f"长度需在 15-{MAX_PLATE_DIM_MM:.0f}mm 之间，当前 {length:.1f}mm"))
    if thickness < MIN_PLATE_THICKNESS_MM:
        issues.append(PrintabilityIssue(
            "thickness_mm", f"底板厚度至少需要 {MIN_PLATE_THICKNESS_MM}mm 才能打印牢固，当前 {thickness:.2f}mm",
        ))

    total_height = thickness + max(ridge_height, 0)
    if total_height > MAX_PLATE_TOTAL_HEIGHT_MM:
        issues.append(PrintabilityIssue(
            "ridge_height_mm", f"底板+脊高总高度需 ≤ {MAX_PLATE_TOTAL_HEIGHT_MM:.0f}mm，当前 {total_height:.1f}mm",
        ))

    return issues


MAX_GRILLE_DIM_MM = 150.0
MIN_GRILLE_THICKNESS_MM = 1.6
MIN_SLOT_COUNT = 1
MAX_SLOT_COUNT = 12


def check_grille_params(params: dict) -> list[PrintabilityIssue]:
    issues: list[PrintabilityIssue] = []

    width = float(params.get("width_mm", 0))
    height = float(params.get("height_mm", 0))
    thickness = float(params.get("thickness_mm", 0))
    slot_count = int(params.get("slot_count", 0))

    if not (20 <= width <= MAX_GRILLE_DIM_MM):
        issues.append(PrintabilityIssue("width_mm", f"宽度需在 20-{MAX_GRILLE_DIM_MM:.0f}mm 之间，当前 {width:.1f}mm"))
    if not (20 <= height <= MAX_GRILLE_DIM_MM):
        issues.append(PrintabilityIssue("height_mm", f"高度需在 20-{MAX_GRILLE_DIM_MM:.0f}mm 之间，当前 {height:.1f}mm"))
    if thickness < MIN_GRILLE_THICKNESS_MM:
        issues.append(PrintabilityIssue(
            "thickness_mm", f"厚度至少需要 {MIN_GRILLE_THICKNESS_MM}mm 才能保证格栅间的筋牢固，当前 {thickness:.2f}mm",
        ))
    if not (MIN_SLOT_COUNT <= slot_count <= MAX_SLOT_COUNT):
        issues.append(PrintabilityIssue(
            "slot_count", f"格栅条数需在 {MIN_SLOT_COUNT}-{MAX_SLOT_COUNT} 之间，当前 {slot_count}",
        ))

    return issues


MAX_FIN_DIM_MM = 120.0
MIN_FIN_THICKNESS_MM = 1.2


def check_fin_params(params: dict) -> list[PrintabilityIssue]:
    issues: list[PrintabilityIssue] = []

    base_length = float(params.get("base_length_mm", 0))
    height = float(params.get("height_mm", 0))
    thickness = float(params.get("thickness_mm", 0))

    if not (10 <= base_length <= MAX_FIN_DIM_MM):
        issues.append(PrintabilityIssue(
            "base_length_mm", f"底边长需在 10-{MAX_FIN_DIM_MM:.0f}mm 之间，当前 {base_length:.1f}mm",
        ))
    if not (10 <= height <= MAX_FIN_DIM_MM):
        issues.append(PrintabilityIssue("height_mm", f"高度需在 10-{MAX_FIN_DIM_MM:.0f}mm 之间，当前 {height:.1f}mm"))
    if thickness < MIN_FIN_THICKNESS_MM:
        issues.append(PrintabilityIssue(
            "thickness_mm", f"厚度至少需要 {MIN_FIN_THICKNESS_MM}mm 才能打印牢固，当前 {thickness:.2f}mm",
        ))

    return issues


def check_crown_params(params: dict) -> list[PrintabilityIssue]:
    issues: list[PrintabilityIssue] = []

    inner_d = float(params.get("inner_diameter_mm", 0))
    thickness = float(params.get("thickness_mm", 0))
    band_height = float(params.get("band_height_mm", 0))
    spike_height = float(params.get("spike_height_mm", 0))
    spike_count = int(params.get("spike_count", 0))

    if not (20 <= inner_d <= 150):
        issues.append(PrintabilityIssue("inner_diameter_mm", f"内径需在 20-150mm 之间，当前 {inner_d:.1f}mm"))
    if thickness < 1.2:
        issues.append(PrintabilityIssue("thickness_mm", f"壁厚至少需要 1.2mm，当前 {thickness:.2f}mm"))
    if not (5 <= band_height <= 60):
        issues.append(PrintabilityIssue("band_height_mm", f"环带高度需在 5-60mm 之间，当前 {band_height:.1f}mm"))
    if not (5 <= spike_height <= 60):
        issues.append(PrintabilityIssue("spike_height_mm", f"尖刺高度需在 5-60mm 之间，当前 {spike_height:.1f}mm"))
    if not (3 <= spike_count <= 24):
        issues.append(PrintabilityIssue("spike_count", f"尖刺数量需在 3-24 之间，当前 {spike_count}"))

    return issues


def check_halo_params(params: dict) -> list[PrintabilityIssue]:
    issues: list[PrintabilityIssue] = []

    diameter = float(params.get("diameter_mm", 0))
    tube_diameter = float(params.get("tube_diameter_mm", 0))

    if not (20 <= diameter <= 150):
        issues.append(PrintabilityIssue("diameter_mm", f"直径需在 20-150mm 之间，当前 {diameter:.1f}mm"))
    if not (2 <= tube_diameter <= 20):
        issues.append(PrintabilityIssue("tube_diameter_mm", f"圆管粗细需在 2-20mm 之间，当前 {tube_diameter:.1f}mm"))
    if tube_diameter * 2 > diameter:
        issues.append(PrintabilityIssue("tube_diameter_mm", "圆管粗细不能超过半径，否则中心会闭合"))

    return issues


def check_antenna_params(params: dict) -> list[PrintabilityIssue]:
    issues: list[PrintabilityIssue] = []

    mast_height = float(params.get("mast_height_mm", 0))
    mast_diameter = float(params.get("mast_diameter_mm", 0))
    ball_diameter = float(params.get("ball_diameter_mm", 0))

    if not (5 <= mast_height <= 100):
        issues.append(PrintabilityIssue("mast_height_mm", f"杆高需在 5-100mm 之间，当前 {mast_height:.1f}mm"))
    if not (1.5 <= mast_diameter <= 15):
        issues.append(PrintabilityIssue("mast_diameter_mm", f"杆径需在 1.5-15mm 之间，当前 {mast_diameter:.1f}mm"))
    if not (3 <= ball_diameter <= 30):
        issues.append(PrintabilityIssue("ball_diameter_mm", f"球径需在 3-30mm 之间，当前 {ball_diameter:.1f}mm"))

    return issues


def check_spike_row_params(params: dict) -> list[PrintabilityIssue]:
    issues: list[PrintabilityIssue] = []

    length = float(params.get("length_mm", 0))
    max_height = float(params.get("max_height_mm", 0))
    base_diameter = float(params.get("base_diameter_mm", 0))
    spike_count = int(params.get("spike_count", 0))

    if not (15 <= length <= 150):
        issues.append(PrintabilityIssue("length_mm", f"总长需在 15-150mm 之间，当前 {length:.1f}mm"))
    if not (3 <= max_height <= 60):
        issues.append(PrintabilityIssue("max_height_mm", f"最高尖刺需在 3-60mm 之间，当前 {max_height:.1f}mm"))
    if not (3 <= base_diameter <= 20):
        issues.append(PrintabilityIssue("base_diameter_mm", f"尖刺粗细需在 3-20mm 之间，当前 {base_diameter:.1f}mm"))
    if not (1 <= spike_count <= 20):
        issues.append(PrintabilityIssue("spike_count", f"尖刺数量需在 1-20 之间，当前 {spike_count}"))

    return issues


def check_wing_params(params: dict) -> list[PrintabilityIssue]:
    issues: list[PrintabilityIssue] = []

    blade_count = int(params.get("blade_count", 0))
    blade_length = float(params.get("blade_length_mm", 0))
    blade_base = float(params.get("blade_base_mm", 0))
    thickness = float(params.get("thickness_mm", 0))

    if not (1 <= blade_count <= 12):
        issues.append(PrintabilityIssue("blade_count", f"羽片数需在 1-12 之间，当前 {blade_count}"))
    if not (10 <= blade_length <= 100):
        issues.append(PrintabilityIssue("blade_length_mm", f"羽片长需在 10-100mm 之间，当前 {blade_length:.1f}mm"))
    if not (5 <= blade_base <= 40):
        issues.append(PrintabilityIssue("blade_base_mm", f"羽片宽需在 5-40mm 之间，当前 {blade_base:.1f}mm"))
    if thickness < 1.2:
        issues.append(PrintabilityIssue("thickness_mm", f"厚度至少需要 1.2mm，当前 {thickness:.2f}mm"))

    return issues


def check_gem_params(params: dict) -> list[PrintabilityIssue]:
    issues: list[PrintabilityIssue] = []

    size = float(params.get("size_mm", 0))
    height_ratio = float(params.get("height_ratio", 0))

    if not (8 <= size <= 100):
        issues.append(PrintabilityIssue("size_mm", f"尺寸需在 8-100mm 之间，当前 {size:.1f}mm"))
    if not (0.3 <= height_ratio <= 3):
        issues.append(PrintabilityIssue("height_ratio", f"拉伸比例需在 0.3-3 之间，当前 {height_ratio:.2f}"))

    return issues
