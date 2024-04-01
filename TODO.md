# TODO

- Make it configurable what to fetch from ADIT and store to RADIS based on the partition key
  - Maybe we would not like to fetch the most recent reports, but those 2-3 days earlier. Otherwise we would maybe miss some that are not revised yet.
  - An alternative would be to not only fetch the newest ones, but also update those a week (or month?!) earlier.
  - For configuration see <https://docs.dagster.io/concepts/configuration/config-schema> and <https://docs.dagster.io/concepts/configuration/advanced-config-types>
