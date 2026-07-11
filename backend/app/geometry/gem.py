"""Parametric generator for the "gem" decoration template.

A faceted low-poly gem (icosahedron or octahedron), stretched into a
teardrop-ish jewel silhouette.
"""
from __future__ import annotations

import numpy as np
import trimesh


def _octahedron() -> trimesh.Trimesh:
    vertices = np.array([
        [1, 0, 0], [-1, 0, 0],
        [0, 1, 0], [0, -1, 0],
        [0, 0, 1], [0, 0, -1],
    ], dtype=float)
    faces = [
        [0, 2, 4], [2, 1, 4], [1, 3, 4], [3, 0, 4],
        [2, 0, 5], [1, 2, 5], [3, 1, 5], [0, 3, 5],
    ]
    return trimesh.Trimesh(vertices=vertices, faces=faces, process=True)


def build_gem_mesh(params: dict) -> trimesh.Trimesh:
    size = float(params.get("size_mm", 24.0))
    facet_style = params.get("facet_style", "icosahedron")
    height_ratio = float(params.get("height_ratio", 1.2))

    mesh = _octahedron() if facet_style == "octahedron" else trimesh.creation.icosphere(subdivisions=0)

    radius = size / 2
    bounds_radius = max(mesh.bounding_sphere.extents) / 2
    scale = radius / bounds_radius
    mesh.apply_scale([scale, scale, scale * height_ratio])
    mesh.apply_translation([0, 0, radius * height_ratio])
    mesh.fix_normals()
    return mesh
