from pytest_djangoapp import configure_djangoapp_plugin

pytest_plugins = configure_djangoapp_plugin(settings="store.settings")
