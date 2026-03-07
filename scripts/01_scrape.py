"""Script to scrape all relevant data from a meeting.

Download data from an OParl API, focusing on a specific meeting
identified by its MEETING_ID. It retrieves information such as the meeting's
organization names, agenda files, and agenda items. The collected data is then saved
as a JSON file.
"""

# %%

import json
import os
from pathlib import Path

import pandas as pd
from dotenv.main import find_dotenv, load_dotenv, set_key

from llm_podcast.oparl.schema import OparlMeeting
from llm_podcast.oparl.scrape import fetch_url, get_next_rat_meeting
from llm_podcast.schema import AgendaFile, AgendaItem, Meeting
from llm_podcast.settings import MEETING_DIR

# %%
# download OparlMeeting


# oparl_meeting: OparlMeeting = get_meeting(meeting_id=MEETING_ID)
oparl_meeting: OparlMeeting = get_next_rat_meeting()

# print(json.dumps(oparl_meeting.model_dump(), indent=2, ensure_ascii=False))
load_dotenv()
print(os.environ.get("MEETING_ID"))
print(os.environ.get("MEETING_DATE"))

# %%
# download organization names

# OPTIONAL: move to function or property
organization_names: list[str] = [
    fetch_url(url=org).get("name") for org in oparl_meeting.organization
]


# %%
# download agenda files

# OPTIONAL: extraction function

df_agenda = pd.DataFrame(
    [item.model_dump() for item in oparl_meeting.agendaItem]
).filter(items=["number", "name", "consultation"])

# map fetch_url to all consultations
df_consultation_paper = (
    pd.DataFrame(
        data=[
            fetch_url(url=consultation)
            for consultation in df_agenda.dropna(subset=["consultation"]).consultation
        ]
    )
    .filter(items=["id", "paper"])
    .rename(columns={"id": "consultation"})
)

df_paper_file_dict = (
    (
        pd.DataFrame(
            data=[fetch_url(url=paper) for paper in df_consultation_paper.paper]
        )
        .filter(items=["id", "auxiliaryFile"])
        .dropna()
    )
    .rename(columns={"id": "paper"})
    .explode("auxiliaryFile")
    .reset_index()
)

df_paper_file = (
    pd.concat(
        [
            df_paper_file_dict,
            pd.json_normalize(df_paper_file_dict.auxiliaryFile),
        ],
        axis=1,
    )
    .rename(columns={"id": "file"})
    .filter(items=["paper", "name", "fileName"])
    .assign(name=lambda df: df.name.str.replace("/", "_"))
    .rename(columns={"name": "description"})
)

df_agenda_files = (
    df_agenda.merge(
        right=df_consultation_paper,
        how="left",
        on="consultation",
    )
    .merge(
        right=df_paper_file,
        how="left",
        on="paper",
    )
    .rename(
        columns={
            "number": "agenda_number",
            "name": "agenda_name",
            "fileName": "filename",
        }
    )
)


# %%
# Transform DataFrame to list[AgendaFile]

agenda_file_dicts = (
    df_agenda_files.dropna(subset=["filename"])
    .filter(items=["agenda_number", "agenda_name", "description", "filename"])
    .to_dict(orient="records")
)

agenda_files: list[AgendaFile] = [AgendaFile(**item) for item in agenda_file_dicts]


# %%
# Transform OParlAgendaItem to AgendaItem

agenda_items = [
    AgendaItem(number=item.number, name=item.name) for item in oparl_meeting.agendaItem
]


# %%
# COMPILE MEETING INFO
meeting_id_str = os.getenv("MEETING_ID") or ""
meeting = Meeting(
    id=int(meeting_id_str),
    organization_names=organization_names,
    name=oparl_meeting.name,
    room=oparl_meeting.location.room,
    start=oparl_meeting.start,
    agenda_items=agenda_items,
    agenda_files=agenda_files,
)

# print(json.dumps(meeting.model_dump(), indent=2, ensure_ascii=False))


# %%
# WRITE MEETING OBJECT TO FILE

MEETING_DIR.mkdir(parents=True, exist_ok=True)
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
set_key(
    dotenv_path,
    "MEETING_JSON_PATH",
    str(MEETING_DIR / f"{os.getenv('MEETING_ID')}.json"),
)
print(os.getenv("MEETING_JSON_PATH"))
meeting_json_path_str = os.getenv("MEETING_JSON_PATH") or ""
Path(meeting_json_path_str).write_text(
    data=json.dumps(
        obj=meeting.model_dump(),
        indent=2,
        ensure_ascii=False,
    )
)

# %%
