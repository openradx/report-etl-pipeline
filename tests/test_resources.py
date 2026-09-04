from radis_etl_tkhd.resources import RadisResource


def test_radis_resource_needs_only_host_and_token() -> None:
    resource = RadisResource(radis_host="http://radis.test", auth_token="token")
    assert resource.radis_host == "http://radis.test"
