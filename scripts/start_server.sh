#!/usr/bin/env bash

if [[ -z "$DAGSTER_HOME" ]]; then
    echo "DAGSTER_HOME environment variable missing" 1>&2
    exit 1
fi

if [[ ! -f "$DAGSTER_HOME/dagster.yaml" ]]; then
    echo "dagster.yaml not found in $DAGSTER_HOME" 1>&2
    exit 1
fi

dagster dev -h 0.0.0.0 -m report_etl_pipeline
