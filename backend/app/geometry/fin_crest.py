"""Parametric generator for the "fin crest" decoration template.

A swept blade/fin shape extruded to a thin constant thickness — a spikier
alternative to the flat badge/plate templates.
"""
from __future__ import annotations

import shapely.geometry
import trimesh


def _fin_profile(base_length: float, height: float, sweep: float) -> shapely.geometry.Polygon:
    points = [
        (0, 0),
        (base_length, 0),
        (base_length * 0.5, height * 0.6),
        (base_length * (0.15 + sweep * 0.5), height),
        (0, height * 0.3),
    ]
    return shapely.geometry.Polygon(points)


def build_fin_mesh(params: dict) -> trimesh.Trimesh:
    base_length = float(params.get("base_length_mm", 40.0))
    height = float(params.get("height_mm", 50.0))
    thickness = float(params.get("thickness_mm", 4.0))
    sweep = max(0.0, min(1.0, float(params.get("sweep", 0.5))))

    profile = _fin_profile(base_length, height, sweep)
    mesh = trimesh.creation.extrude_polygon(profile, height=thickness)
    mesh.apply_translation([-base_length / 2, 0, 0])
    mesh.fix_normals()
    return mesh
