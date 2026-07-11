"""Parametric generator for the "shoulder ring" decoration template.

Seed geometry is res/G1_肩部装饰环_v1.stl (a hand-modeled example). Rather than
deforming that mesh directly, we regenerate a clean parametric tube from the
same family of dimensions, which keeps every parameter combination watertight
and printable.
"""
from __future__ import annotations

import logging
import math

import numpy as np
import trimesh

logger = logging.getLogger(__name__)

DEFAULT_SECTIONS = 96
HEX_HOLE_COUNT = 10
HEX_HOLE_RADIUS_RATIO = 0.28  # relative to wall thickness


def _ring_profile_vertices(
    inner_r: float,
    outer_r: float,
    height: float,
    sections: int,
    pattern: str,
) -> trimesh.Trimesh:
    """Build a watertight tube by direct vertex generation (no boolean ops)."""
    thetas = np.linspace(0, 2 * math.pi, sections, endpoint=False)

    amplitude = 0.0
    freq = 8
    if pattern == "wave":
        amplitude = min(outer_r - inner_r, 1.5) * 0.4
        freq = 10

    outer_radii = outer_r + amplitude * np.sin(freq * thetas)

    outer_top = np.stack([outer_radii * np.cos(thetas), outer_radii * np.sin(thetas), np.full(sections, height)], axis=1)
    outer_bot = np.stack([outer_radii * np.cos(thetas), outer_radii * np.sin(thetas), np.zeros(sections)], axis=1)
    inner_top = np.stack([inner_r * np.cos(thetas), inner_r * np.sin(thetas), np.full(sections, height)], axis=1)
    inner_bot = np.stack([inner_r * np.cos(thetas), inner_r * np.sin(thetas), np.zeros(sections)], axis=1)

    vertices = np.concatenate([outer_top, outer_bot, inner_top, inner_bot], axis=0)
    n = sections
    ot, ob, it, ib = 0, n, 2 * n, 3 * n

    faces = []
    for i in range(n):
        j = (i + 1) % n
        # outer wall
        faces += [[ot + i, ot + j, ob + j], [ot + i, ob + j, ob + i]]
        # inner wall (reversed winding, normal points inward)
        faces += [[it + i, ib + j, it + j], [it + i, ib + i, ib + j]]
        # top annulus
        faces += [[ot + i, it + j, it + i], [ot + i, ot + j, it + j]]
        # bottom annulus
        faces += [[ob + i, ib + i, ib + j], [ob + i, ib + j, ob + j]]

    mesh = trimesh.Trimesh(vertices=vertices, faces=np.array(faces), process=True)
    mesh.fix_normals()
    return mesh


def _punch_hex_holes(mesh: trimesh.Trimesh, inner_r: float, outer_r: float, height: float) -> trimesh.Trimesh:
    thickness = outer_r - inner_r
    hole_r = max(thickness * HEX_HOLE_RADIUS_RATIO, 0.6)
    mid_r = (inner_r + outer_r) / 2

    cutters = []
    for i in range(HEX_HOLE_COUNT):
        theta = 2 * math.pi * i / HEX_HOLE_COUNT
        cx, cy = mid_r * math.cos(theta), mid_r * math.sin(theta)
        cutter = trimesh.creation.cylinder(radius=hole_r, height=thickness * 3, sections=6)
        # orient cylinder axis along the local radial direction
        radial = np.array([math.cos(theta), math.sin(theta), 0.0])
        z_axis = np.array([0.0, 0.0, 1.0])
        rot = trimesh.geometry.align_vectors(z_axis, radial)
        cutter.apply_transform(rot)
        cutter.apply_translation([cx, cy, height / 2])
        cutters.append(cutter)

    try:
        holes = trimesh.boolean.union(cutters)
        result = trimesh.boolean.difference([mesh, holes])
        if result.is_watertight:
            return result
        logger.warning("hex pattern boolean result not watertight, falling back to plain ring")
    except Exception:
        logger.warning("hex pattern boolean op failed, falling back to plain ring", exc_info=True)
    return mesh


def build_ring_mesh(params: dict) -> trimesh.Trimesh:
    inner_r = float(params.get("inner_diameter_mm", 60.0)) / 2
    thickness = float(params.get("thickness_mm", 3.0))
    outer_r = inner_r + thickness
    height = float(params.get("height_mm", 30.0))
    pattern = params.get("pattern", "plain")

    mesh = _ring_profile_vertices(inner_r, outer_r, height, DEFAULT_SECTIONS, pattern)

    if pattern == "hex":
        mesh = _punch_hex_holes(mesh, inner_r, outer_r, height)
        mesh.fix_normals()

    return mesh
