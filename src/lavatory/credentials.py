import os

from .exceptions import MissingEnvironmentVariable


def load_credentials():
    credentials = {
        "artifactory_password": os.getenv('ARTIFACTORY_PASSWORD'),
        "artifactory_username": os.getenv('ARTIFACTORY_USERNAME'),
        "artifactory_url": os.getenv('ARTIFACTORY_URL')
    }

    for key in credentials:
        if credentials[key] is None:
            raise MissingEnvironmentVariable(key.upper())

    return credentials
