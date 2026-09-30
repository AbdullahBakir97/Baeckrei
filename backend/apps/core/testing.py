import secrets


def make_test_password():
    """A throwaway password for test users.

    Generated at runtime so no credential-like string is committed (secret
    scanners flag hard-coded passwords even in tests).
    """
    return f'{secrets.token_urlsafe(12)}-Aa1!'
