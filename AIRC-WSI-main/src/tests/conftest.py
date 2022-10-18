import pytest
from tb_api import create_app

@pytest.fixture
def app():
    app = create_app()

    with app.app_context():
        #Init calls go here
        pass
    yield app

@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()

