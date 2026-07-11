"""Shared mesh -> bytes export helpers used by every decoration template."""
import trimesh


def mesh_to_glb_bytes(mesh: trimesh.Trimesh, color_hex: str = "#2b6cff") -> bytes:
    rgb = tuple(int(color_hex.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
    mesh.visual = trimesh.visual.ColorVisuals(mesh, vertex_colors=[*rgb, 255])
    scene = trimesh.Scene([mesh])
    return scene.export(file_type="glb")
