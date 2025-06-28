"""Schema models that are subsets of the OParl schema."""

from pydantic import BaseModel


class OparlLocation(BaseModel):
    """Location of a meeting."""

    id: str
    room: str


class OParlAgendaItem(BaseModel):
    """Agenda items for a Meeting."""

    id: str
    number: str
    name: str
    order: int
    consultation: str | None = None


class OParlInvitation(BaseModel):
    """Invitation for a Meeting."""

    name: str
    fileName: str


class OparlMeeting(BaseModel):
    """Metadata for a Meeting."""

    id: str
    name: str
    start: str
    location: OparlLocation
    organization: list[str]
    invitation: OParlInvitation | None = None
    agendaItem: list[OParlAgendaItem]
    # auxiliary_files: list[str]  # may be relevant for other meetings
