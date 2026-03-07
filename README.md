# llm-podcast

[![pre-commit](https://github.com/muenster-interessierts/msi-pipeline/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/muenster-interessierts/msi-pipeline/actions/workflows/pre-commit.yml)

LLM-generated podcast about and for Münster

## Resources

Data input for this project is exclusively from the ***Ratsinformationssystem*** of the city of Münster.  
See these resources for more information:

* [Ratsinformationssystem](https://www.stadt-muenster.de/sessionnet/sessionnetbi/info.php)
* [Ratsinformationssystem API documentation](https://opendata.stadt-muenster.de/dataset/oparl-schnittstelle-zum-ratsinformationsystem-der-stadt-m%C3%BCnster)

## System requirements

1. Dependencies are managed with `uv`.
See [installation instructions](https://docs.astral.sh/uv/getting-started/installation/) on howto install it.

2. To install the Python version defined in `.python-version`, run:

    ```
    uv python install
    ```

## Development setup

1. Install the dependencies, as defined in `pyproject.toml` by running:

    ```
    uv sync
    ```

2. Install the pre-commit hooks:

    ```
    uv run pre-commit install
    ```

3. Settings are set in the `.env` file and read from there by `llm_podcast.settings`.
  Use `.env.example` as a template.

4. Authorize against S3-compatible storage for DVC:

    ```
    uv run dvc remote modify --local url <PATH TO STORAGE e.g. s3://mybucket>
    uv run dvc remote modify --local myremote access_key_id <ACCESS_KEY>
    uv run dvc remote modify --local myremote secret_access_key <SECRET>
    ```
   check that it is set up with
    ```
    uv run dvc remote list
    ```

5. Load data from DVC cache:

    ```
    uv run dvc pull
    ```

6. Explore the DAG of the project:

    ```
    uv run dvc dag
    ```

7. Run the pipeline (if not already cached):

    ```
    uv run dvc repro
    ```

## Test suite

Tests are written with `pytest`, and located in the `tests` directory.
They are divided into `unit` and `integration` tests.

Run all **unit tests** with: `uv run pytest test/unit`

Run all **integration tests** with: `uv run pytest test/integration` <br>
Note that this requires authorized access to 3rd party APIs.

## Roadmap

1. Fetch future calendar events from RIS, and report if documents are attached.
2. Überblick über kommende Woche
