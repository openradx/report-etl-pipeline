# Report ETL Pipeline

## About

Report ETL Pipeline is a [Dagster](https://dagster.io/) project to extract radiological reports (SR Modality) from a Synapse PACS (by using [ADIT](https://github.com/radexperts/adit)) and transfer them to RADIS for creating a full-text search index.

## Development

- Make sure to have a `.env` file (see `example.env` template).
- Artifacts are stored according to `.env`.
- Uses file based SQLite database with files in `dagster_home` folder for Dagster stuff.
- Start Dagster UI with `inv dagster-dev`.
- Alternatively, run a single job from command line, e.g. `python ./scripts/materialize_assets.py -d ./artifacts/ 2023-01-01`.

## Production

- Make sure to have a `.env.prod` file (see `example.env` template).
- Uses a container based setup with PostgreSQL for Dagster stuff.
- Artifacts are stored according to `.env.prod` (Cave, inside the container if no extra folder is mounted).
- Start environment with `inv compose-up`.
