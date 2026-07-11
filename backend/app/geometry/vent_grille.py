"""Parametric generator for the "vent grille" decoration template.

A rectangular plate with parallel slot cutouts — a mechanical greeble panel
for a flat body surface.
"""
from __future__ import annotations

import trimesh

SLOT_MARGIN_RATIO = 0.15
SLOT_GAP_RATIO = 0.4  # slot width as a fraction of the per-slot pitch


def build_grille_mesh(params: dict) -> trimesh.Trimesh:
    width = float(params.get("width_mm", 60.0))
    height = float(params.get("height_mm", 40.0))
    thickness = float(params.get("thickness_mm", 4.0))
    slot_count = max(int(params.get("slot_count", 5)), 1)

    base = trimesh.creation.box(extents=[width, height, thickness])
    base.apply_translation([0, 0, thickness / 2])

    slot_span = height * (1 - 2 * SLOT_MARGIN_RATIO)
    pitch = width / slot_count
    slot_width = pitch * SLOT_GAP_RATIO

    cutters = []
    for i in range(slot_count):
        cx = -width / 2 + pitch * (i + 0.5)
        cutter = trimesh.creation.box(extents=[slot_width, slot_span, thickness * 3])
        cutter.apply_translation([cx, 0, thickness / 2])
        cutters.append(cutter)

    holes = trimesh.boolean.union(cutters) if len(cutters) > 1 else cutters[0]
    mesh = trimesh.boolean.difference([base, holes])
    mesh.fix_normals()
    return mesh
