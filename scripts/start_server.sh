#!/usr/bin/env bash

if [[ -z "$DAGSTER_HOME" ]]; then
    echo "DAGSTER_HOME environment variable missing" 1>&2
    exit 1
fi

if [[ ! -f "$DAGSTER_HOME/dagster.yaml" ]]; then
    echo "dagster.yaml not found in $DAGSTER_HOME" 1>&2
    exit 1
fi

# Replace this shell with Dagster so that it receives the container's stop signal directly and
# can shut down its services (and any in-flight runs) cleanly.
exec dagster dev -h 0.0.0.0 -m radis_etl_tkhd
