from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, Column, JSON


class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Placement(SQLModel):
    """One decoration instance: a template + params placed at a mount point."""
    template_id: str
    mount_point: str
    params: dict = {}
    offset: Optional[list[float]] = None
    rotation: Optional[list[float]] = None


class Design(SQLModel, table=True):
    """A saved "look": a team's full set of decoration placements + body colors."""
    id: Optional[int] = Field(default=None, primary_key=True)
    team_name: str = Field(index=True)
    placements: list = Field(default_factory=list, sa_column=Column(JSON))
    body_colors: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DesignCreate(SQLModel):
    team_name: str
    placements: list[Placement] = []
    body_colors: Optional[dict[str, str]] = None


class DesignUpdate(SQLModel):
    placements: Optional[list[Placement]] = None
    body_colors: Optional[dict[str, str]] = None


class DesignRead(SQLModel):
    id: int
    team_name: str
    placements: list
    body_colors: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
