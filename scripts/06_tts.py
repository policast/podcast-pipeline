"""Script to generate a transcript from a podcast episode."""

# %%

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from llm_podcast.settings import SCRIPT_DIR, SOUND_DIR

# %%
# PARSE SCRIPT

script_path = SCRIPT_DIR / "script.txt"
script_dict = json.loads(script_path.read_text())


text = ""
for section in script_dict["sections"]:
    text += f"{section['content']}\n"
    text += f"{section['relevance']}\n\n"

# replace excessive newlines
text_formatted = text.replace("\n\n\n", "\n\n")
print(text_formatted)

# %%
# TEXT TO SPEECH

print("Generating audio ...")
load_dotenv()
openai = OpenAI()
response = openai.audio.speech.create(
    model="gpt-4o-mini-tts",
    voice="onyx",  # alternatives: echo, ash
    input=text_formatted,
    response_format="mp3",
)

# %%
# SAVE AUDIO FILE

print("Saving audio file.")

SOUND_DIR.mkdir(parents=True, exist_ok=True)
# output_file = SOUND_DIR / "episode.mp3"
load_dotenv()
meeting_date_str = os.getenv("MEETING_DATE") or ""

output_file = SOUND_DIR / Path("episode_" + meeting_date_str + ".mp3")

with open(output_file, "wb") as f:
    f.write(response.content)

# %%
