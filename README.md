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

- Production uses a Docker compose based setup with PostgreSQL for Dagster internal data. It also uses Nginx for basic auth.
- Make sure to have a `.env.prod` file (see `example.env` template).
- Artifacts are stored according to `ARTIFACTS_DIR` in `.env.prod`. Cave, it's inside the container if no extra folder is mounted.
- Generate a password file for basic authentication by using `htpasswd -c .htpasswd <username>` (needs apache2-utils to be installed).
- Attach the virtual environment with `poetry shell`.
- Start the stack with `inv compose-up`.
- Dagster can be accessed on localhost on port 8888.
