# Report ETL Pipeline

## About

Report ETL Pipeline is a [Dagster](https://dagster.io/) project to extract radiological reports (SR Modality) from a Synapse PACS (by using [ADIT](https://github.com/radexperts/adit)) and transfer them to RADIS for creating a full-text search index.

## Development

- Copy `example.env` to `.env` and edit the settings in there.
- Artifacts are stored according to `ARTIFACTS_DIR` in `.env`. If `ARTIFACTS_DIR` is not set then the files are stored in the `dagster_home` folder under `storage`.
- The dev environment uses a file based SQLite database with files in `dagster_home` folder for Dagster stuff.
- Start Dagster UI with `inv dagster-dev`, which is then accessible under `http://localhost:3000` (make sure the port is forwarded by VS Code, see Ports tab).
- Alternatively, run a single job from command line, e.g. `python ./scripts/materialize_assets.py -d ./artifacts/ 2023-01-01`.

## Production

- Production uses Nginx for basic auth and SSL encryption.
- Generate a password file for basic authentication by using `htpasswd -c nginx/.htpasswd <username>` (needs apache2-utils to be installed).
- Generate SSL certificate with `openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/ssl.key -out nginx/ssl.crt` (nothing has to be filled out)
- Copy `example.env` to `.env.prod` and edit the settings in there.
- Artifacts are stored according to `ARTIFACTS_DIR` in `.env.prod`. Cave, it's inside the container if no extra folder is mounted.
- Attach the virtual environment with `poetry shell` and then start the stack with `inv compose-up`.
- Dagster UI can now be accessed on `https://localhost:8888` (make sure the port is forwarded by VS Code, see Ports tab).
