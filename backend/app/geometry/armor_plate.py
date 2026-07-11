"""Parametric generator for the "armor plate" decoration template.

A rounded-rectangle plate with a raised center ridge, meant to sit flush
against a flat body panel — a more angular alternative to emblem_badge.
"""
from __future__ import annotations

import shapely.geometry
import trimesh

RIDGE_OVERLAP_MM = 0.5


def _rounded_rect(width: float, length: float, corner_radius: float) -> shapely.geometry.Polygon:
    corner_radius = min(corner_radius, width / 2 - 0.1, length / 2 - 0.1)
    inset = shapely.geometry.box(-width / 2 + corner_radius, -length / 2 + corner_radius,
                                  width / 2 - corner_radius, length / 2 - corner_radius)
    return inset.buffer(corner_radius, resolution=8)


def build_plate_mesh(params: dict) -> trimesh.Trimesh:
    width = float(params.get("width_mm", 50.0))
    length = float(params.get("length_mm", 70.0))
    thickness = float(params.get("thickness_mm", 4.0))
    ridge_height = float(params.get("ridge_height_mm", 4.0))
    corner_radius = min(width, length) * 0.18

    base_poly = _rounded_rect(width, length, corner_radius)
    base = trimesh.creation.extrude_polygon(base_poly, height=thickness)

    if ridge_height > 0:
        ridge_poly = _rounded_rect(width * 0.28, length * 0.82, width * 0.1)
        ridge = trimesh.creation.extrude_polygon(ridge_poly, height=ridge_height + RIDGE_OVERLAP_MM)
        ridge.apply_translation([0, 0, thickness - RIDGE_OVERLAP_MM])
        mesh = trimesh.boolean.union([base, ridge])
    else:
        mesh = base

    mesh.fix_normals()
    return mesh
