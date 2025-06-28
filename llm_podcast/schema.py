"""Schema model definitions."""

from pydantic import BaseModel


class AgendaItem(BaseModel):
    """Agenda items for a Meeting."""

    number: str
    name: str


class AgendaFile(BaseModel):
    agenda_number: str
    agenda_name: str
    description: str
    filename: str


class Meeting(BaseModel):
    """Metadata for a Meeting."""

    id: int
    organization_names: list[str]
    name: str
    room: str
    start: str
    agenda_items: list[AgendaItem]
    agenda_files: list[AgendaFile]
