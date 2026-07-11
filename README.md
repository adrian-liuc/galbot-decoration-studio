# Galbot Decoration Studio

A web app for designing 3D-printable decorations for the Galbot One Golf
robot: pick a parametric template (crown, badge, armor plate, wings, gem,
antenna, and more), drag/rotate/snap it onto the robot's actual mesh, stack
multiple pieces into one project, recolor the robot's own body panels, and
export everything as STL/3MF for printing.

The 3D viewer loads the robot's real URDF via [`urdf-loader`](https://github.com/gkjohnson/urdf-loaders)
so decorations attach to the robot's actual joints/links, not an approximation.

## Project layout

- `backend/` — FastAPI service: parametric decoration geometry (via
  [`trimesh`](https://trimesh.org/)), printability validation, saved-project
  storage, and STL/3MF/ZIP export. Also serves the robot's URDF + meshes.
- `frontend/` — React + Vite + react-three-fiber app: the 3D customizer UI.
- `urdf/`, `meshes/` — the subset of the robot's URDF and visual meshes that
  the backend actually serves (collision meshes and other formats
  omitted — see [Origin of the robot assets](#origin-of-the-robot-assets)).

## Running locally

**Backend**

```bash
cd backend
python -m venv .venv
./.venv/Scripts/pip install -r requirements.txt   # macOS/Linux: .venv/bin/pip
./.venv/Scripts/python -m uvicorn app.main:app --reload --port 8000
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

By default `frontend/vite.config.ts` proxies `/api` and `/robot` to
`http://127.0.0.1:8000` — update the port there if you run the backend on a
different one. Pass `--host` to `npm run dev` to make the dev server
reachable from other devices on your LAN.

## Origin of the robot assets

`urdf/galbot_one_golf_fixed_base.urdf` and `meshes/visual/**` are copied from
[`galbot_one_golf_description`](https://github.com/GalaxyGeneralRobotics/galbot_one_golf_description)
(Apache License 2.0 — see `LICENSE`), trimmed to only the URDF preset and
visual meshes this app actually loads (collision meshes, MJCF, USD, and
xacro sources from the upstream package are not needed here and were
dropped).
