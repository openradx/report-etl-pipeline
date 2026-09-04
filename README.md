# RADIS ETL TKHD

## About

RADIS ETL TKHD is a [Dagster](https://dagster.io/) pipeline to extract radiological reports (inside SR Modality instances) from a PACS (by using [ADIT](https://github.com/openradx/adit)) and transfer them to RADIS for creating a full-text search index. The pipeline contains two jobs. `collect_reports_job` collects all reports since the year 2014 (by using Dagster backfills) and also has a schedule to collect reports during the night from the previous day to send them to RADIS. `revise_reports_job` has a schedule to collect the reports of the day 8 days before again (that is 7 days before the partition of the previous day) to catch reports that were changed or added in the meantime and to send those to RADIS.

## Setup

- Both development and production uses Docker Compose to setup the Dagster server
- `dagster_home_dev` resp. `dagster_home_prod` folder in the workspace is mounted as `DAGSTER_HOME` folder. Every data output by the pipelines is stored in those folders.
- Copy `example.env` to `.env.dev` or resp. `.env.prod` and edit the settings in there.
- Artifacts are stored according to `ARTIFACTS_DIR`. If `ARTIFACTS_DIR` is not set then the files are stored in the `DAGSTER_HOME` folder under `storage`.
- A relative `ARTIFACTS_DIR` path is stored relative to `DAGSTER_HOME` which is `dagster_home_dev` folder in development and `dagster_home_prod` folder in production.
- The schedules start automatically in production (the production Compose file sets `DAGSTER_DEPLOYMENT=prod`). In development they stay stopped until turned on in the Dagster UI. A schedule that is stopped manually in the UI stays stopped in both environments until it is started again.
- Production uses Nginx for basic auth and SSL encryption.
  - Generate a password file for basic authentication by using `htpasswd -c .htpasswd <username>` (needs apache2-utils to be installed).
  - Generate SSL certificate with `openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ssl.key -out ssl.crt` (nothing has to be filled out)
- Install the dependencies with `uv sync` (or `just sync`) and activate the virtual environment with `source .venv/bin/activate`. Then start the stack with `just up` or `just up prod`.
- Run `just` to list the most common commands. `just check` runs ruff, pyright and pytest and should pass before committing changes. The same tasks are also available as invoke tasks (`inv --list`).
- Forward port `3500` in development resp. `3600` in production to Dagster UI in VS Code ports tab.
- Alternatively (for testing purposes), run a single job from command line, e.g. `python ./scripts/materialize_assets.py -d ./artifacts/ 2023-01-01`.
