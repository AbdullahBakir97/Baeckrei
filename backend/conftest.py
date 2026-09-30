import pytest


@pytest.fixture(autouse=True)
def _plain_http_in_tests(settings):
    # The test client talks plain HTTP; with DEBUG off, the production HTTPS
    # redirect would otherwise answer every request with a 301.
    settings.SECURE_SSL_REDIRECT = False
