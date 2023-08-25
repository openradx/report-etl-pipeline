from dagster import Definitions, EnvVar, load_assets_from_modules

from . import assets, resources

all_assets = load_assets_from_modules([assets])

defs = Definitions(
    assets=all_assets,
    resources={
        "adit": resources.AditResource(
            adit_host=EnvVar("ADIT_HOST"),
            auth_token=EnvVar("AUTH_TOKEN"),
        )
    },
)
