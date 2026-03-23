"""Summarize meeting documents using a language model."""

# %%

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from joblib import Memory
from tqdm import tqdm

from llm_podcast.llm import query_llm
from llm_podcast.schema import Meeting
from llm_podcast.settings import MEETING_DIR, SUMMARY_DIR, TXT_DIR

TEMPERATURE: float = 0.5  # Temperature setting for summarization

SYSTEM_PROMPT_DOCUMENT_SUMMARY = """
Fasse die folgende Datei zusammen,
die zu einer Parlementssitzung in der Kommunalpolitik gehört.

Die Zusammenfassung darf nicht mehr als 500 Zeichen lang sein.
Falls der Input sich mit weniger zusammenfassen lässt, nutze weniger als 500 Zeichen.

WICHTIG:
Benutze nur die im Input gegebenen Infos und dichte nichts hinzu.
Gib ausschließlich Informationen wieder, die im Text enthalten sind,
d.h. keine Interpretationen, Bewertungen oder Ergänzungen.

Bleibe dabei neutral und versuche die wichtigsten Punkte zu erfassen.
"""


# %%
# READ MEETING JSON
load_dotenv()
MEETING_JSON_PATH = MEETING_DIR / f"{os.getenv('MEETING_ID')}.json"
meeting_dict = json.loads(MEETING_JSON_PATH.read_text())
meeting = Meeting(**meeting_dict)


# %%
# INDEX TXT FILES TO SUMMARIZE


filenames = [
    TXT_DIR / Path(file.filename).with_suffix(".txt") for file in meeting.agenda_files
]

filenames


# %%
# FUNCTIONS


# initialize memory for disk caching
memory = Memory(location=".cache", verbose=0)


# OPITONAL: move to library
@memory.cache(verbose=0)
def summarize(
    text_raw: str,
    temperature: float,
    prompt: str = SYSTEM_PROMPT_DOCUMENT_SUMMARY,
) -> str:
    """Summarize a text using LLM.

    Args:
        text_raw: Raw text to summarize.
        prompt: Prompt to use for summarization.
            Defaults to SYSTEM_PROMPT_DOCUMENT_SUMMARY.
    Returns:
        Summary of the text.
    """
    summary = query_llm(
        system=prompt,
        input=text_raw,
        temperature=temperature,
    )
    return summary


# %%
# SUMMARIZE ALL TEXTS

texts = [file.read_text() for file in filenames]

SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

for filename, text in tqdm(
    iterable=zip(filenames, texts, strict=True),
    total=len(filenames),
    desc="Summarizing files",
):
    print(f"Summarizing text file://{filename.resolve()} ...")
    summary = summarize(text_raw=text, temperature=TEMPERATURE)
    summary_path = SUMMARY_DIR / filename.name
    print(f"Writing summary to file://{summary_path.resolve()} .")
    summary_path.write_text(summary)

print("Done.")

# %%
