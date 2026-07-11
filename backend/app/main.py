from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import context, designs, robot, templates
from app.db import create_db_and_tables
from app.storage import REPO_ROOT

app = FastAPI(title="Galbot Decoration Studio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.mount("/robot/meshes", StaticFiles(directory=REPO_ROOT / "meshes"), name="robot-meshes")

app.include_router(templates.router)
app.include_router(context.router)
app.include_router(designs.router)
app.include_router(robot.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
