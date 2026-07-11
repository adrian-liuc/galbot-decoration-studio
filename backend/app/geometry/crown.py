"""Parametric generator for the "crown" decoration template.

A ring band with a row of conical spikes around the top rim — a literal
crown silhouette, but the same wrap-around-a-cylinder technique works
equally well as a spiky collar/mohawk base anywhere on the robot.
"""
from __future__ import annotations

import math

import numpy as np
import trimesh

DEFAULT_SECTIONS = 96


def _band_mesh(inner_r: float, outer_r: float, height: float) -> trimesh.Trimesh:
    thetas = np.linspace(0, 2 * math.pi, DEFAULT_SECTIONS, endpoint=False)
    outer_top = np.stack([outer_r * np.cos(thetas), outer_r * np.sin(thetas), np.full(DEFAULT_SECTIONS, height)], axis=1)
    outer_bot = np.stack([outer_r * np.cos(thetas), outer_r * np.sin(thetas), np.zeros(DEFAULT_SECTIONS)], axis=1)
    inner_top = np.stack([inner_r * np.cos(thetas), inner_r * np.sin(thetas), np.full(DEFAULT_SECTIONS, height)], axis=1)
    inner_bot = np.stack([inner_r * np.cos(thetas), inner_r * np.sin(thetas), np.zeros(DEFAULT_SECTIONS)], axis=1)

    vertices = np.concatenate([outer_top, outer_bot, inner_top, inner_bot], axis=0)
    n = DEFAULT_SECTIONS
    ot, ob, it, ib = 0, n, 2 * n, 3 * n

    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces += [[ot + i, ot + j, ob + j], [ot + i, ob + j, ob + i]]
        faces += [[it + i, ib + j, it + j], [it + i, ib + i, ib + j]]
        faces += [[ot + i, it + j, it + i], [ot + i, ot + j, it + j]]
        faces += [[ob + i, ib + i, ib + j], [ob + i, ib + j, ob + j]]

    mesh = trimesh.Trimesh(vertices=vertices, faces=np.array(faces), process=True)
    mesh.fix_normals()
    return mesh


def build_crown_mesh(params: dict) -> trimesh.Trimesh:
    inner_r = float(params.get("inner_diameter_mm", 60.0)) / 2
    thickness = float(params.get("thickness_mm", 3.0))
    outer_r = inner_r + thickness
    band_height = float(params.get("band_height_mm", 18.0))
    spike_count = max(int(params.get("spike_count", 6)), 1)
    spike_height = float(params.get("spike_height_mm", 22.0))

    band = _band_mesh(inner_r, outer_r, band_height)

    mid_r = (inner_r + outer_r) / 2
    spike_base_r = thickness * 0.55
    spikes = []
    for i in range(spike_count):
        theta = 2 * math.pi * i / spike_count
        cone = trimesh.creation.cone(radius=spike_base_r, height=spike_height, sections=16)
        cone.apply_translation([mid_r * math.cos(theta), mid_r * math.sin(theta), band_height - spike_base_r * 0.3])
        spikes.append(cone)

    spikes_union = trimesh.boolean.union(spikes) if len(spikes) > 1 else spikes[0]
    mesh = trimesh.boolean.union([band, spikes_union])
    mesh.fix_normals()
    return mesh
