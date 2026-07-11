"""Parametric generator for the "antenna" decoration template.

A thin mast with a ball tip — classic radar/antenna greeble.
"""
from __future__ import annotations

import trimesh

BALL_OVERLAP_MM = 0.6


def build_antenna_mesh(params: dict) -> trimesh.Trimesh:
    mast_height = float(params.get("mast_height_mm", 35.0))
    mast_diameter = float(params.get("mast_diameter_mm", 3.0))
    ball_diameter = float(params.get("ball_diameter_mm", 8.0))

    mast = trimesh.creation.cylinder(radius=mast_diameter / 2, height=mast_height, sections=20)
    mast.apply_translation([0, 0, mast_height / 2])

    ball = trimesh.creation.uv_sphere(radius=ball_diameter / 2, count=[20, 20])
    ball.apply_translation([0, 0, mast_height - BALL_OVERLAP_MM])

    mesh = trimesh.boolean.union([mast, ball])
    mesh.fix_normals()
    return mesh
