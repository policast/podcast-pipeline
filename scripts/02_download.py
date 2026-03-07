"""Download Agenda Files for a meeting.

This script downloads all agenda files for a specific meeting. The meeting details
are loaded from a JSON file, and the agenda files are downloaded to a specified
directory.
"""

# %%
import os
from pathlib import Path

from dotenv import load_dotenv
from tqdm import tqdm

from llm_podcast.oparl.scrape import download_agenda_file
from llm_podcast.schema import Meeting
from llm_podcast.settings import PDF_DIR

# %%
# load meeting.json
load_dotenv()
print(os.getenv("MEETING_JSON_PATH"))
print(os.getenv("MEETING_ID"))
print(os.getenv("MEETING_DATE"))
meeting_json_path_str = os.getenv("MEETING_JSON_PATH") or ""
meeting = Meeting.model_validate_json(json_data=Path(meeting_json_path_str).read_text())


# %%
# DOWNLOAD ALL FILES TO FOLDERS

PDF_DIR.mkdir(parents=True, exist_ok=True)

for file_name in tqdm(iterable=meeting.agenda_files):
    download_agenda_file(file_name)

print("Downloads done.")

# %%
