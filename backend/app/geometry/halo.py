"""Parametric generator for the "halo" decoration template.

A genuine torus (donut) built directly from its standard parametrization —
a floating ring accent, e.g. above the head.
"""
from __future__ import annotations

import math

import numpy as np
import trimesh

MAJOR_SEGMENTS = 64
MINOR_SEGMENTS = 20


def build_halo_mesh(params: dict) -> trimesh.Trimesh:
    major_r = float(params.get("diameter_mm", 90.0)) / 2
    minor_r = float(params.get("tube_diameter_mm", 6.0)) / 2

    vertices = []
    for i in range(MAJOR_SEGMENTS):
        theta = 2 * math.pi * i / MAJOR_SEGMENTS
        for j in range(MINOR_SEGMENTS):
            phi = 2 * math.pi * j / MINOR_SEGMENTS
            x = (major_r + minor_r * math.cos(phi)) * math.cos(theta)
            y = (major_r + minor_r * math.cos(phi)) * math.sin(theta)
            z = minor_r * math.sin(phi)
            vertices.append([x, y, z])

    faces = []
    for i in range(MAJOR_SEGMENTS):
        i_next = (i + 1) % MAJOR_SEGMENTS
        for j in range(MINOR_SEGMENTS):
            j_next = (j + 1) % MINOR_SEGMENTS
            a = i * MINOR_SEGMENTS + j
            b = i_next * MINOR_SEGMENTS + j
            c = i_next * MINOR_SEGMENTS + j_next
            d = i * MINOR_SEGMENTS + j_next
            faces += [[a, b, c], [a, c, d]]

    mesh = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces), process=True)
    mesh.fix_normals()
    return mesh
