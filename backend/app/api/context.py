import json

from fastapi import APIRouter

from app.storage import ASSETS_DIR

router = APIRouter(prefix="/api/context", tags=["context"])

MOUNT_POINTS_PATH = ASSETS_DIR / "mount_points.json"

URDF_URL = "/robot/urdf/galbot_one_golf_fixed_base.urdf"
ROBOT_BASE_URL = "/robot/"


@router.get("")
def get_context():
    mount_points = json.loads(MOUNT_POINTS_PATH.read_text(encoding="utf-8"))
    return {
        "urdf_url": URDF_URL,
        "robot_base_url": ROBOT_BASE_URL,
        "mount_points": mount_points,
    }
