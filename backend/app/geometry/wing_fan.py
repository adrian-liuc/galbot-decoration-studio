"""Parametric generator for the "wing fan" decoration template.

Several tapered blades fanned out from a shared base — a mechanical
wing/feather-fan accent, reusing the fin_crest blade profile.
"""
from __future__ import annotations

import math

import shapely.geometry
import trimesh

from app.geometry.fin_crest import _fin_profile


def build_wing_mesh(params: dict) -> trimesh.Trimesh:
    blade_count = max(int(params.get("blade_count", 5)), 1)
    blade_length = float(params.get("blade_length_mm", 45.0))
    blade_base = float(params.get("blade_base_mm", 12.0))
    thickness = float(params.get("thickness_mm", 2.5))
    spread_deg = float(params.get("spread_deg", 120.0))

    profile = _fin_profile(blade_base, blade_length, sweep=0.35)
    base_blade = trimesh.creation.extrude_polygon(profile, height=thickness)
    base_blade.apply_translation([-blade_base / 2, 0, 0])

    blades = []
    start_angle = -spread_deg / 2
    step = spread_deg / max(blade_count - 1, 1) if blade_count > 1 else 0
    for i in range(blade_count):
        angle_deg = start_angle + step * i
        blade = base_blade.copy()
        rot = trimesh.transformations.rotation_matrix(math.radians(angle_deg), [0, 0, 1])
        blade.apply_transform(rot)
        blades.append(blade)

    mesh = trimesh.util.concatenate(blades) if len(blades) > 1 else blades[0]
    mesh.fix_normals()
    return mesh
