"""Serves the robot's URDF with light sanitization for urdf-loader.

The preset URDF has a few `type="fixed"` joints with a bare `<axis/>` tag
(no xyz attribute) — valid per the URDF spec since a fixed joint has no
axis of motion, but urdf-loader's parser doesn't guard against a missing
xyz attribute and throws. Stripping those empty tags is safe and doesn't
change the robot's kinematics.
"""
import xml.etree.ElementTree as ET

from fastapi import APIRouter, HTTPException, Response

from app.storage import REPO_ROOT

router = APIRouter(prefix="/robot/urdf", tags=["robot"])

URDF_DIR = REPO_ROOT / "urdf"


@router.get("/{filename}")
def get_urdf(filename: str):
    path = URDF_DIR / filename
    if not path.is_file() or path.suffix != ".urdf":
        raise HTTPException(404, "URDF not found")

    tree = ET.parse(path)
    root = tree.getroot()
    for joint in root.findall("joint"):
        axis = joint.find("axis")
        if axis is not None and axis.get("xyz") is None:
            joint.remove(axis)

    return Response(ET.tostring(root, encoding="unicode"), media_type="application/xml")
