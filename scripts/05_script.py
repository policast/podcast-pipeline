"""Script stage to draft the podcast script."""

# %%
import json
from pathlib import Path

from llm_podcast.llm import query_llm
from llm_podcast.schema import AgendaFile, Meeting
from llm_podcast.settings import MEETING_JSON_PATH, SCRIPT_DIR, SUMMARY_DIR

TEMPERATURE: float = 0.5

SYSTEM_PROMPT_SCRIPT = """
Erstelle ein Podcast-Skript im JSON-Format, in dem David,
der Moderator des Podcasts „Münster interessierts“,
allein über eine bevorstehende Sitzung eines städtischen Ausschusses in Münster berichtet.

Verwende ausschließlich die Informationen aus dem bereitgestellten JSON zur Sitzung.
Das Ausgabeformat soll aus mehreren klar getrennten Abschnitten bestehen, jeweils im folgenden Schema:

Jeder neue thematische Abschnitt bekommt einen neuen JSON-Block.
Die Inhalte sollen:
- locker, verständlich und bürgernah formuliert sein
- neutral und informativ sein
- konkret erklären, worum es im Tagesordnungspunkt geht und was das für Bürger:innen bedeutet

Die Folge ist für ca. 3-5 Minuten Länge gedacht (~5-10 JSON-Blöcke).

Struktur des Skripts:
1. Begrüßung und kurze Vorstellung des Podcasts
2. Vorstellung der Sitzung (Ausschussname, Datum) mit sehr kurzer Einleitung ins Thema.
2. Überblick über die relevantesten Tagesordnungspunkte.
4. Ausblick: Fazit und Ermutigung zum Mitmachen.

Für jeden Tagesordnungspunkt mit Datei:
1. 'title': Überschrift für Abschnitt.
1. 'content': Kurze Erklärung.
2. 'relevance': Warum ist das Thema relevant?
3. 'file': Verweis auf die als Quelle verwendete PDF-Datei (Dateiname)

Hinweis:
- Nenne nur Tagesordnungspunkte, zu denen Dateien vorliegen
- Tagesordnungspunkte ohne Dokumente bitte weglassen
- Nutze die file-Angabe ausschließlich für die Dateinamen, die mit einem Thema verknüpft sind
- Keine fiktiven Inhalte oder Spekulationen - bleibe bei den gelieferten Fakten
- Vermeide auffordernde Abschlüsse wie "Lasst uns gemeinsam..."
- Halte den Text neutral und informativ
- beginne die antwort nicht mit "```json" und beende sie nicht mit "```"
- spreche nicht von "Müstertalern", sondern von "Münsteranern"
- nutze das Wort "wichtig" spärlich

Zusätzlich zu den Sektionen erstelle folgende Metadaten für die Podcast-Episode:
1. 'title': Ein prägnanter Titel für die gesamte Podcast-Episode (Name der Sitzung, Datum)
2. 'description': Eine kurzes Summary des Inhalts der Episode (3-5 Sätze)
3. 'shownotes': Eine ausführliches Summary der Episode zum Überblick (5-10 Sätze),
        die auch die wichtigsten Themen und Punkte der Sitzung umfasst.
        Die Formattierung der Shownotes MUSS Markdown Markup enthalten.
        Eine Stukturierung der Abschnitte in Bullets ist erwünscht.
4. 'tags': Eine Liste von 5-10 relevanten Schlagworten für die Episode.

JSON-Format:
{{
    'metadata': {{
        'title': '<Titel der Podcast-Episode>',
        'description': '<Beschreibung der Episode>',
        'shownotes': '<Show-Notes der Episode in Markdown>',s
        'tags': [
            '<Erstes Schlagwort>',
            '<Zweites Schlagwort>',
            ...
        ]
    }},
    'sections': [
        {{
            'title': '<Titel des Abschnitts>',
            'content': '<Inhalt des Abschnitts>',
            'relevance': '<Relevanz des Themas>',
            'file': '<Dateiname der Datei>' # alternativ, null, wenn keine Datei relevant
        }},
        ...  # weitere Sections
    ]
}}
"""  # noqa: E501


# %%
# READ MEETING JSON

meeting_dict = json.loads(MEETING_JSON_PATH.read_text())
meeting = Meeting(**meeting_dict)


# %%
# LOAD SUMMARIES

summary_files = [
    SUMMARY_DIR / Path(file.filename).with_suffix(".txt")
    for file in meeting.agenda_files
]

summary_files

summaries = [file.read_text() for file in summary_files]

summary_pdfs = [file.with_suffix(".pdf").name for file in summary_files]


# combine to dict
summary_dict = dict(zip(summary_pdfs, summaries))


# %%


agenda_files_summaries = [
    {**dict(agenda_file), "summary": summary_dict[agenda_file.filename]}
    for agenda_file in meeting.agenda_files
]

agenda_files_summaries

# %%
# INSERT SUMMARIES INTO AGENDA FILES


class AgendaFileSummary(AgendaFile):
    summary: str


class MeetingSummary(Meeting):
    agenda_files: list[AgendaFileSummary]  # type: ignore


meeting_dict = meeting.model_dump()
meeting_dict["agenda_files"] = [
    AgendaFileSummary(**agenda_file) for agenda_file in agenda_files_summaries
]

meeting_summary = MeetingSummary(**meeting_dict)


# %%
# GENERATE SCRIPT


script = query_llm(
    system=SYSTEM_PROMPT_SCRIPT,
    input=str(meeting_summary.model_dump()),
    temperature=TEMPERATURE,
)


# %%
# WRITE RESULT TO FILE

SCRIPT_DIR.mkdir(parents=True, exist_ok=True)

script_path = SCRIPT_DIR / "script.txt"

script_path.write_text(script)

print(f"Podcast script written to file:///{script_path.resolve()}")
