"""Scraping functions."""

import json
from datetime import datetime
from pathlib import Path

import requests
from dotenv.main import find_dotenv, load_dotenv, set_key
from joblib import Memory

from llm_podcast.oparl.schema import OparlMeeting
from llm_podcast.schema import AgendaFile
from llm_podcast.settings import PDF_DIR

memory = Memory(location=".cache", verbose=0)


# @memory.cache
def fetch_url(url: str) -> dict:
    """Fetch a URL and return the JSON response.

    Args:
        url: URL to fetch.
    Returns:
        JSON response.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an error for bad responses
    except requests.exceptions.HTTPError as e:
        print(f"Error fetching {url}: {e}")
        return {}
    return response.json()


@memory.cache
def fetch_all_pages(url: str) -> list[dict]:
    """Fetch all pages of a paginated API entry.

    Args:
        url: URL to the first page of the API entry.
    Returns:
        all entities from all pages.
    """
    all_entities = []
    current_page_url = url

    while current_page_url:
        print(f"Fetching {current_page_url}...")
        response = requests.get(current_page_url)
        response.raise_for_status()  # Raises an error for bad responses
        data = response.json()
        all_entities.extend(data.get("data", []))
        current_page_url = data.get("links", {}).get("next")

    return all_entities


@memory.cache
def cached_requests_get(url: str) -> requests.Response:
    """Cached wrapper around requests.get().

    Args:
        url: URL to fetch.
    Returns:
        Response from get().
    """
    response = requests.get(url)
    return response


def print_dict(data: list[dict]):
    print(json.dumps(data, indent=2))


def get_meeting(meeting_id: int) -> OparlMeeting:
    """Get a single meeting by ID.

    Args:
        meeting_id: ID of the meeting.
    Returns:
        OparlMeeting object.
    """
    MEETINGS_ROUTE = "https://oparl.stadt-muenster.de/bodies/0001/meetings/"

    meeting_url = MEETINGS_ROUTE + str(meeting_id)
    meeting_json = fetch_url(url=meeting_url)

    return OparlMeeting(**meeting_json)


# OPTIONAL: only pass filename
def download_agenda_file(agenda_file: AgendaFile) -> None:
    """Download a single AgendaFile.

    Args:
        agenda_file: AgendaFile object to download from OParl API.
    Raises:
        HTTPError: if the response is not successful.
    """
    print(f"downloading {agenda_file.filename} ...")
    file_id = Path(agenda_file.filename).stem
    download_url = f"https://www.stadt-muenster.de/sessionnet/sessionnetbi/getfile.php?id={file_id}"
    response = cached_requests_get(download_url)
    response.raise_for_status()  # Raises an error for bad responses
    with open(PDF_DIR / agenda_file.filename, "wb") as file:
        file.write(response.content)


# @memory.cache
def get_next_rat_meeting() -> OparlMeeting:
    """Get next meeting.

    Args:
        none
    Returns:
        OparlMeeting object.
    """

    # GET ALL MEETINGS FOR 'Rat'
    rat_meetings_url = (
        "https://oparl.stadt-muenster.de/bodies/0001/organizations/gr/258/meetings"
    )
    rat_meetings = fetch_all_pages(url=rat_meetings_url)

    # FILTER DOWN TO MEETINGS IN THE FUTURE
    future_rat_meetings = [
        meeting
        for meeting in rat_meetings
        if meeting["start"] > str(datetime.today().strftime("%Y-%m-%d"))
    ]

    # Get next meeting
    for dic in future_rat_meetings:
        dic["start"] = datetime.strptime(dic["start"], "%Y-%m-%dT%H:%M:%S%z")

    next_meeting_json = min(future_rat_meetings, key=lambda d: d.get("start", 0))

    # Convert start date back to string to add to OparlMeeting object
    next_meeting_json["start"] = next_meeting_json["start"].strftime("%Y-%m-%d")

    # Set variables as environment variables
    dotenv_path = find_dotenv()
    load_dotenv(dotenv_path)
    next_meeting_id = next_meeting_json["id"].rsplit("/")[-1]
    set_key(dotenv_path, "MEETING_ID", next_meeting_id)
    set_key(dotenv_path, "MEETING_DATE", next_meeting_json["start"])

    MEETINGS_ROUTE = "https://oparl.stadt-muenster.de/bodies/0001/meetings/"

    meeting_url = MEETINGS_ROUTE + next_meeting_id
    meeting_json = fetch_url(url=meeting_url)

    # oparl_meeting: OparlMeeting = get_meeting(meeting_id=int(next_meeting_id))
    return OparlMeeting(**meeting_json)
    # return oparl_meeting
