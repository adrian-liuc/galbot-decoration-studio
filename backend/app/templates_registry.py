"""Registry of decoration templates: parameter schema, geometry builder, and
printability validator for each. Adding a new decoration type means adding
one entry here plus a geometry module under app.geometry — nothing else in
the API layer needs to change.

Every template lists every mount point: with manual drag/rotate/snap-to-
surface placement in the viewer, the mount point is just a starting spot,
not a hard constraint on which decorations "belong" where.
"""
from app.geometry import (
    antenna,
    armor_plate,
    crown,
    emblem_badge,
    fin_crest,
    gem,
    halo,
    shoulder_ring,
    spike_row,
    vent_grille,
    wing_fan,
)
from app.geometry.printability import (
    check_antenna_params,
    check_badge_params,
    check_crown_params,
    check_fin_params,
    check_gem_params,
    check_grille_params,
    check_halo_params,
    check_plate_params,
    check_ring_params,
    check_spike_row_params,
    check_wing_params,
)

ALL_MOUNT_POINTS = ["left_shoulder", "right_shoulder", "chest", "back", "head_top"]

TEMPLATES = {
    "shoulder_ring": {
        "schema": {
            "id": "shoulder_ring",
            "name": "关节装饰环",
            "mount_points": ALL_MOUNT_POINTS,
            "params": {
                "inner_diameter_mm": {"type": "number", "min": 20, "max": 150, "default": 60, "step": 1},
                "thickness_mm": {"type": "number", "min": 1.2, "max": 8, "default": 3, "step": 0.1},
                "height_mm": {"type": "number", "min": 5, "max": 120, "default": 30, "step": 1},
                "pattern": {"type": "enum", "options": ["plain", "hex", "wave"], "default": "plain"},
                "color": {"type": "color", "default": "#2b6cff"},
            },
        },
        "build_mesh": shoulder_ring.build_ring_mesh,
        "validate": check_ring_params,
    },
    "emblem_badge": {
        "schema": {
            "id": "emblem_badge",
            "name": "徽章挂饰",
            "mount_points": ALL_MOUNT_POINTS,
            "params": {
                "shape": {"type": "enum", "options": ["circle", "hex", "shield"], "default": "circle"},
                "diameter_mm": {"type": "number", "min": 10, "max": 150, "default": 60, "step": 1},
                "thickness_mm": {"type": "number", "min": 1.2, "max": 10, "default": 4, "step": 0.1},
                "boss_height_mm": {"type": "number", "min": 0, "max": 20, "default": 3, "step": 0.5},
                "color": {"type": "color", "default": "#ff6a00"},
            },
        },
        "build_mesh": emblem_badge.build_badge_mesh,
        "validate": check_badge_params,
    },
    "armor_plate": {
        "schema": {
            "id": "armor_plate",
            "name": "装甲护片",
            "mount_points": ALL_MOUNT_POINTS,
            "params": {
                "width_mm": {"type": "number", "min": 15, "max": 150, "default": 50, "step": 1},
                "length_mm": {"type": "number", "min": 15, "max": 150, "default": 70, "step": 1},
                "thickness_mm": {"type": "number", "min": 1.2, "max": 10, "default": 4, "step": 0.1},
                "ridge_height_mm": {"type": "number", "min": 0, "max": 15, "default": 4, "step": 0.5},
                "color": {"type": "color", "default": "#4a4a52"},
            },
        },
        "build_mesh": armor_plate.build_plate_mesh,
        "validate": check_plate_params,
    },
    "vent_grille": {
        "schema": {
            "id": "vent_grille",
            "name": "通风格栅",
            "mount_points": ALL_MOUNT_POINTS,
            "params": {
                "width_mm": {"type": "number", "min": 20, "max": 150, "default": 60, "step": 1},
                "height_mm": {"type": "number", "min": 20, "max": 150, "default": 40, "step": 1},
                "thickness_mm": {"type": "number", "min": 1.6, "max": 10, "default": 4, "step": 0.1},
                "slot_count": {"type": "number", "min": 1, "max": 12, "default": 5, "step": 1},
                "color": {"type": "color", "default": "#2b2b30"},
            },
        },
        "build_mesh": vent_grille.build_grille_mesh,
        "validate": check_grille_params,
    },
    "fin_crest": {
        "schema": {
            "id": "fin_crest",
            "name": "鳍片饰刃",
            "mount_points": ALL_MOUNT_POINTS,
            "params": {
                "base_length_mm": {"type": "number", "min": 10, "max": 120, "default": 40, "step": 1},
                "height_mm": {"type": "number", "min": 10, "max": 120, "default": 50, "step": 1},
                "thickness_mm": {"type": "number", "min": 1.2, "max": 10, "default": 4, "step": 0.1},
                "sweep": {"type": "number", "min": 0, "max": 1, "default": 0.5, "step": 0.05},
                "color": {"type": "color", "default": "#9a2bff"},
            },
        },
        "build_mesh": fin_crest.build_fin_mesh,
        "validate": check_fin_params,
    },
    "crown": {
        "schema": {
            "id": "crown",
            "name": "王冠",
            "mount_points": ALL_MOUNT_POINTS,
            "params": {
                "inner_diameter_mm": {"type": "number", "min": 20, "max": 150, "default": 60, "step": 1},
                "thickness_mm": {"type": "number", "min": 1.2, "max": 8, "default": 3, "step": 0.1},
                "band_height_mm": {"type": "number", "min": 5, "max": 60, "default": 18, "step": 1},
                "spike_count": {"type": "number", "min": 3, "max": 24, "default": 6, "step": 1},
                "spike_height_mm": {"type": "number", "min": 5, "max": 60, "default": 22, "step": 1},
                "color": {"type": "color", "default": "#ffd23f"},
            },
        },
        "build_mesh": crown.build_crown_mesh,
        "validate": check_crown_params,
    },
    "halo": {
        "schema": {
            "id": "halo",
            "name": "光环",
            "mount_points": ALL_MOUNT_POINTS,
            "params": {
                "diameter_mm": {"type": "number", "min": 20, "max": 150, "default": 90, "step": 1},
                "tube_diameter_mm": {"type": "number", "min": 2, "max": 20, "default": 6, "step": 0.5},
                "color": {"type": "color", "default": "#ffe27a"},
            },
        },
        "build_mesh": halo.build_halo_mesh,
        "validate": check_halo_params,
    },
    "antenna": {
        "schema": {
            "id": "antenna",
            "name": "天线信标",
            "mount_points": ALL_MOUNT_POINTS,
            "params": {
                "mast_height_mm": {"type": "number", "min": 5, "max": 100, "default": 35, "step": 1},
                "mast_diameter_mm": {"type": "number", "min": 1.5, "max": 15, "default": 3, "step": 0.5},
                "ball_diameter_mm": {"type": "number", "min": 3, "max": 30, "default": 8, "step": 0.5},
                "color": {"type": "color", "default": "#ff3b3b"},
            },
        },
        "build_mesh": antenna.build_antenna_mesh,
        "validate": check_antenna_params,
    },
    "spike_row": {
        "schema": {
            "id": "spike_row",
            "name": "脊刺排",
            "mount_points": ALL_MOUNT_POINTS,
            "params": {
                "length_mm": {"type": "number", "min": 15, "max": 150, "default": 60, "step": 1},
                "max_height_mm": {"type": "number", "min": 3, "max": 60, "default": 20, "step": 1},
                "base_diameter_mm": {"type": "number", "min": 3, "max": 20, "default": 8, "step": 0.5},
                "spike_count": {"type": "number", "min": 1, "max": 20, "default": 7, "step": 1},
                "color": {"type": "color", "default": "#2b2b30"},
            },
        },
        "build_mesh": spike_row.build_spike_row_mesh,
        "validate": check_spike_row_params,
    },
    "wing_fan": {
        "schema": {
            "id": "wing_fan",
            "name": "机械羽翼",
            "mount_points": ALL_MOUNT_POINTS,
            "params": {
                "blade_count": {"type": "number", "min": 1, "max": 12, "default": 5, "step": 1},
                "blade_length_mm": {"type": "number", "min": 10, "max": 100, "default": 45, "step": 1},
                "blade_base_mm": {"type": "number", "min": 5, "max": 40, "default": 12, "step": 1},
                "thickness_mm": {"type": "number", "min": 1.2, "max": 10, "default": 2.5, "step": 0.1},
                "spread_deg": {"type": "number", "min": 0, "max": 360, "default": 120, "step": 5},
                "color": {"type": "color", "default": "#c084fc"},
            },
        },
        "build_mesh": wing_fan.build_wing_mesh,
        "validate": check_wing_params,
    },
    "gem": {
        "schema": {
            "id": "gem",
            "name": "棱晶宝石",
            "mount_points": ALL_MOUNT_POINTS,
            "params": {
                "size_mm": {"type": "number", "min": 8, "max": 100, "default": 24, "step": 1},
                "height_ratio": {"type": "number", "min": 0.3, "max": 3, "default": 1.2, "step": 0.1},
                "facet_style": {"type": "enum", "options": ["icosahedron", "octahedron"], "default": "icosahedron"},
                "color": {"type": "color", "default": "#22d3ee"},
            },
        },
        "build_mesh": gem.build_gem_mesh,
        "validate": check_gem_params,
    },
}


def default_params(template_id: str) -> dict:
    schema = TEMPLATES[template_id]["schema"]
    return {key: spec["default"] for key, spec in schema["params"].items()}


def list_templates() -> list[dict]:
    return [t["schema"] for t in TEMPLATES.values()]
