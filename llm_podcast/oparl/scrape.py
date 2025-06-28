"""Scraping functions."""

import json
from pathlib import Path

import requests
from joblib import Memory

from llm_podcast.oparl.schema import OparlMeeting
from llm_podcast.schema import AgendaFile
from llm_podcast.settings import PDF_DIR

memory = Memory(location=".cache", verbose=0)


@memory.cache
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
