from fastapi import APIRouter, HTTPException, Response

from app.geometry.export import mesh_to_glb_bytes
from app.templates_registry import TEMPLATES, default_params, list_templates

router = APIRouter(prefix="/api/templates", tags=["templates"])

GLB_MEDIA_TYPE = "model/gltf-binary"


@router.get("")
def get_templates():
    return list_templates()


@router.post("/{template_id}/preview.glb")
def preview_glb(template_id: str, params: dict):
    template = TEMPLATES.get(template_id)
    if template is None:
        raise HTTPException(404, f"Unknown template_id: {template_id}")
    merged = {**default_params(template_id), **params}
    mesh = template["build_mesh"](merged)
    glb_bytes = mesh_to_glb_bytes(mesh, merged.get("color", "#2b6cff"))
    return Response(glb_bytes, media_type=GLB_MEDIA_TYPE)
