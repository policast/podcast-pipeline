"""Scrape relevant information from Ratsinformatonssystem."""

# %%

from llm_podcast.oparl.scrape import fetch_all_pages, print_dict

# %%
# GET ALL ORGANIZATIONS

base_url = "https://oparl.stadt-muenster.de/bodies/0001/organizations"
organizations = fetch_all_pages(url=base_url)
print_dict(data=organizations)


# %%
# GET ALL MEETINGS FOR 'Rat'

rat_meetings_url = (
    "https://oparl.stadt-muenster.de/bodies/0001/organizations/gr/258/meetings"
)
rat_meetings = fetch_all_pages(url=rat_meetings_url)
print_dict(data=rat_meetings)

# %%
# FILTER DOWN TO MEETINGS IN THE FUTURE

future_rat_meetings = [
    meeting for meeting in rat_meetings if meeting["start"] > "2024-09-12"
]
print_dict(data=future_rat_meetings)

# %%
