from homebridge import HomebridgeAPI


def test_get_accessories():
    """
    Test that we get all the accessories from
    a currently setup
    """

    # Ensure that we even have an available API
    test_api = HomebridgeAPI()
    assert test_api.refresh_accessories()
    assert test_api.is_available()

    # Ensure that we get at least one accessory
    foo = test_api.get_plugin_List()
    print(foo)
    assert test_api.get_outlets()


def test_toggle_accessories():
    """
    Test that ensures that we can toggle an accessory
    """
    test_api = HomebridgeAPI()
    assert test_api.is_available()

    outlets = test_api.get_outlets()

    # Toggle the available accessories
    for outlet in outlets:
        if outlet.name.lower() == "office plug":
            assert test_api.toggle_outlet(outlet.unique_id, outlet.get_toggle_payload())
