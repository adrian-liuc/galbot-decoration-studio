import io
import zipfile
from datetime import datetime
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlmodel import Session, select

from app.db import get_session
from app.geometry.export import mesh_to_glb_bytes
from app.models import Design, DesignCreate, DesignRead, DesignUpdate, Placement
from app.storage import cache_path, params_hash
from app.templates_registry import TEMPLATES, default_params

router = APIRouter(prefix="/api/designs", tags=["designs"])

GLB_MEDIA_TYPE = "model/gltf-binary"
STL_MEDIA_TYPE = "model/stl"
THREEMF_MEDIA_TYPE = "model/3mf"


def _get_template(template_id: str) -> dict:
    template = TEMPLATES.get(template_id)
    if template is None:
        raise HTTPException(404, f"Unknown template_id: {template_id}")
    return template


def _validate_placement(placement: Placement, index: int) -> dict:
    template = _get_template(placement.template_id)
    if placement.mount_point not in template["schema"]["mount_points"]:
        raise HTTPException(422, f"[第{index + 1}件] {placement.template_id} 不支持挂载点 {placement.mount_point}")
    merged_params = {**default_params(placement.template_id), **placement.params}
    issues = template["validate"](merged_params)
    if issues:
        raise HTTPException(
            422,
            detail=[{"field": i.field, "message": f"[第{index + 1}件] {i.message}"} for i in issues],
        )
    return {
        "template_id": placement.template_id,
        "mount_point": placement.mount_point,
        "params": merged_params,
        "offset": placement.offset,
        "rotation": placement.rotation,
    }


def _validate_placements(placements: list[Placement]) -> list[dict]:
    return [_validate_placement(p, i) for i, p in enumerate(placements)]


def _get_design_or_404(design_id: int, session: Session) -> Design:
    design = session.get(Design, design_id)
    if design is None:
        raise HTTPException(404, "Design not found")
    return design


@router.post("", response_model=DesignRead)
def create_design(payload: DesignCreate, session: Session = Depends(get_session)):
    design = Design(
        team_name=payload.team_name,
        placements=_validate_placements(payload.placements),
        body_colors=payload.body_colors,
    )
    session.add(design)
    session.commit()
    session.refresh(design)
    return design


@router.get("", response_model=list[DesignRead])
def list_designs(team_name: str | None = Query(default=None), session: Session = Depends(get_session)):
    statement = select(Design)
    if team_name:
        statement = statement.where(Design.team_name == team_name)
    return session.exec(statement.order_by(Design.created_at.desc())).all()


@router.get("/{design_id}", response_model=DesignRead)
def get_design(design_id: int, session: Session = Depends(get_session)):
    return _get_design_or_404(design_id, session)


@router.patch("/{design_id}", response_model=DesignRead)
def update_design(design_id: int, payload: DesignUpdate, session: Session = Depends(get_session)):
    design = _get_design_or_404(design_id, session)
    if payload.placements is not None:
        design.placements = _validate_placements(payload.placements)
    if payload.body_colors is not None:
        design.body_colors = payload.body_colors
    design.updated_at = datetime.utcnow()
    session.add(design)
    session.commit()
    session.refresh(design)
    return design


def _get_placement_or_404(design: Design, index: int) -> dict:
    if index < 0 or index >= len(design.placements):
        raise HTTPException(404, "Placement not found")
    return design.placements[index]


def _build_mesh_for_placement(placement: dict):
    template = _get_template(placement["template_id"])
    return template["build_mesh"](placement["params"])


@router.get("/{design_id}/placements/{index}/preview.glb")
def preview_placement_glb(design_id: int, index: int, session: Session = Depends(get_session)):
    design = _get_design_or_404(design_id, session)
    placement = _get_placement_or_404(design, index)
    key = params_hash(placement["template_id"], placement["params"])
    path = cache_path(f"{design_id}p{index}", key, "glb")
    if not path.exists():
        mesh = _build_mesh_for_placement(placement)
        path.write_bytes(mesh_to_glb_bytes(mesh, placement["params"].get("color", "#2b6cff")))
    return Response(path.read_bytes(), media_type=GLB_MEDIA_TYPE)


@router.get("/{design_id}/placements/{index}/export.stl")
def export_placement_stl(design_id: int, index: int, session: Session = Depends(get_session)):
    design = _get_design_or_404(design_id, session)
    placement = _get_placement_or_404(design, index)
    key = params_hash(placement["template_id"], placement["params"])
    path = cache_path(f"{design_id}p{index}", key, "stl")
    if not path.exists():
        mesh = _build_mesh_for_placement(placement)
        path.write_bytes(mesh.export(file_type="stl"))
    filename = f"{index + 1:02d}_{placement['template_id']}.stl"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(path.read_bytes(), media_type=STL_MEDIA_TYPE, headers=headers)


@router.get("/{design_id}/placements/{index}/export.3mf")
def export_placement_3mf(design_id: int, index: int, session: Session = Depends(get_session)):
    design = _get_design_or_404(design_id, session)
    placement = _get_placement_or_404(design, index)
    key = params_hash(placement["template_id"], placement["params"])
    path = cache_path(f"{design_id}p{index}", key, "3mf")
    if not path.exists():
        mesh = _build_mesh_for_placement(placement)
        path.write_bytes(mesh.export(file_type="3mf"))
    filename = f"{index + 1:02d}_{placement['template_id']}.3mf"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(path.read_bytes(), media_type=THREEMF_MEDIA_TYPE, headers=headers)


@router.get("/{design_id}/export.zip")
def export_design_zip(design_id: int, session: Session = Depends(get_session)):
    design = _get_design_or_404(design_id, session)
    if not design.placements:
        raise HTTPException(422, "这套作品还没有任何配饰")

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for index, placement in enumerate(design.placements):
            mesh = _build_mesh_for_placement(placement)
            filename = f"{index + 1:02d}_{placement['template_id']}.stl"
            zf.writestr(filename, mesh.export(file_type="stl"))
    buffer.seek(0)

    # Content-Disposition must be latin-1 encodable; team names are often
    # Chinese, so ASCII-filter for the plain `filename`, and additionally
    # provide RFC 5987 `filename*` so browsers show the real team name.
    safe_team = "".join(c for c in design.team_name if c.isascii() and c.isalnum()) or "team"
    encoded_team = quote(design.team_name)
    headers = {
        "Content-Disposition": (
            f'attachment; filename="{safe_team}_galbot_decorations.zip"; '
            f"filename*=UTF-8''{encoded_team}_galbot_decorations.zip"
        )
    }
    return Response(buffer.read(), media_type="application/zip", headers=headers)
