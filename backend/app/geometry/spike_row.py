"""Parametric generator for the "spike row" decoration template.

A row of graduated cone spikes along a thin base strip — a mohawk/dragon
-spine greeble.
"""
from __future__ import annotations

import math

import trimesh

STRIP_THICKNESS_RATIO = 0.35


def build_spike_row_mesh(params: dict) -> trimesh.Trimesh:
    length = float(params.get("length_mm", 60.0))
    max_height = float(params.get("max_height_mm", 20.0))
    spike_count = max(int(params.get("spike_count", 7)), 1)
    base_diameter = float(params.get("base_diameter_mm", 8.0))

    strip_thickness = max(base_diameter * STRIP_THICKNESS_RATIO, 1.5)
    strip = trimesh.creation.box(extents=[length, base_diameter, strip_thickness])
    strip.apply_translation([0, 0, strip_thickness / 2])

    spikes = []
    for i in range(spike_count):
        t = i / max(spike_count - 1, 1)
        # taper the row's silhouette: tallest in the middle, shorter at the ends
        envelope = math.sin(math.pi * t) if spike_count > 1 else 1.0
        height = max_height * (0.35 + 0.65 * envelope)
        x = -length / 2 + length * t
        cone = trimesh.creation.cone(radius=base_diameter / 2, height=height, sections=14)
        cone.apply_translation([x, 0, strip_thickness - 0.4])
        spikes.append(cone)

    spikes_union = trimesh.boolean.union(spikes) if len(spikes) > 1 else spikes[0]
    mesh = trimesh.boolean.union([strip, spikes_union])
    mesh.fix_normals()
    return mesh
