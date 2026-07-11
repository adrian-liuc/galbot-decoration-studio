"""Parametric generator for the "emblem badge" decoration template.

A flat plate (circle/hexagon/shield outline) with a smaller raised boss on
top, meant to sit flush against a flat body panel (chest, back, head).
"""
from __future__ import annotations

import math

import shapely.geometry
import trimesh

BOSS_OVERLAP_MM = 0.5


def _shape_polygon(shape: str, radius: float) -> shapely.geometry.Polygon:
    if shape == "circle":
        return shapely.geometry.Point(0, 0).buffer(radius, resolution=32)
    if shape == "hex":
        points = [
            (radius * math.cos(math.radians(60 * i)), radius * math.sin(math.radians(60 * i)))
            for i in range(6)
        ]
        return shapely.geometry.Polygon(points)
    if shape == "shield":
        unit_points = [(-1, 1), (1, 1), (1, -0.1), (0, -1.2), (-1, -0.1)]
        points = [(x * radius, y * radius) for x, y in unit_points]
        return shapely.geometry.Polygon(points)
    raise ValueError(f"Unknown badge shape: {shape}")


def build_badge_mesh(params: dict) -> trimesh.Trimesh:
    shape = params.get("shape", "circle")
    diameter = float(params.get("diameter_mm", 60.0))
    thickness = float(params.get("thickness_mm", 4.0))
    boss_height = float(params.get("boss_height_mm", 2.0))
    radius = diameter / 2

    base_poly = _shape_polygon(shape, radius)
    base = trimesh.creation.extrude_polygon(base_poly, height=thickness)

    if boss_height > 0:
        boss_poly = _shape_polygon(shape, radius * 0.7)
        boss = trimesh.creation.extrude_polygon(boss_poly, height=boss_height + BOSS_OVERLAP_MM)
        boss.apply_translation([0, 0, thickness - BOSS_OVERLAP_MM])
        mesh = trimesh.boolean.union([base, boss])
    else:
        mesh = base

    mesh.fix_normals()
    return mesh
