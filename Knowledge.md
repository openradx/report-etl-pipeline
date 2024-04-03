# Knowledge

- When changing something in `dagster.yaml` the Dagster server has to be restarted.
- When changing code in development it will be respected in the next run (no need to reload code location).
- Reload code location seems to be important in production when using a GRPC server (we don't do that currently).
- The folder set in `local_artifact_storage` in `dagster.yaml` will get `context.instance.root_directory`.
- If `local_artifact_storage` is not set in `dagster.yaml` it is the same as `DAGSTER_HOME`.
- The `context.instance.storage_directory()` will just attach `storage` to the above `root_directory`.
